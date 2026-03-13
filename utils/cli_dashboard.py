"""Generate a static HTML dashboard for CLI test runs.

The dashboard is a single self-contained HTML file with:
- Tailwind CSS (via CDN) for layout and styling
- Chart.js (via CDN) for basic charts

It reads a pytest HTML report and derives a very simple summary
(pass/fail/error/skip counts) using string heuristics. This keeps the
generator independent from pytest internals and plugins.

Intended usage from CI:
- After pytest generates reports/report.html
- Call: python -m utils.cli_dashboard --report-path reports/report.html --output-dir public
- Publish public/ via GitHub Pages.
"""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime


def _infer_counts(report_html: str) -> Dict[str, int]:
    """Very lightweight heuristic to infer test result counts from pytest-html.

    This is intentionally simple and robust: it just counts common class names
    for results. It will not be perfect but gives an approximate distribution.

    To reduce confusing mismatches (e.g. dashboard says 9 tests when pytest
    summary shows a different number), we also try to parse the pytest
    summary line (``X passed, Y failed, Z skipped in Ns``). If that summary
    is present and disagrees with the class-name heuristic, we prefer the
    summary counts and mark the result as ``summary_inconsistent=True`` so
    the dashboard can flag it.
    """
    lowered = report_html.lower()

    # Try to read counts from the pytest summary line first.
    summary_counts: Optional[Dict[str, int]] = None
    summary_total = 0
    summary_match = re.search(
        r"(?:===\s*)?"
        r"(?P<passed>\d+)\s+passed"
        r"(?:,\s*(?P<failed>\d+)\s+failed)?"
        r"(?:,\s*(?P<error>\d+)\s+error[s]?)?"
        r"(?:,\s*(?P<skipped>\d+)\s+skipped)?"
        r"(?:\s+in\s+[\d\.]+s)?"
        r"(?:\s*===)?",
        lowered,
    )
    if summary_match:
        summary_counts = {
            "passed": int(summary_match.group("passed") or 0),
            "failed": int(summary_match.group("failed") or 0),
            "error": int(summary_match.group("error") or 0),
            "skipped": int(summary_match.group("skipped") or 0),
        }
        summary_total = (
            summary_counts["passed"]
            + summary_counts["failed"]
            + summary_counts["error"]
            + summary_counts["skipped"]
        )

    def count_any(markers):
        return sum(lowered.count(m) for m in markers)

    passed = count_any(['class="passed"', "class='passed'", "data-test-result=\"passed\""])
    failed = count_any(['class="failed"', "class='failed'", "data-test-result=\"failed\""])
    error = count_any(['class="error"', "class='error'", "data-test-result=\"error\""])
    skipped = count_any(['class="skipped"', "class='skipped'", "data-test-result=\"skipped\""])

    raw_total = passed + failed + error + skipped

    # If we have a trustworthy pytest summary and it disagrees with the raw
    # HTML heuristic (common when some rows are hidden/filtered), prefer the
    # summary numbers and flag the inconsistency so the UI can surface it.
    summary_inconsistent = False
    if summary_counts and summary_total:
        if summary_total != raw_total:
            summary_inconsistent = True
            passed = summary_counts["passed"]
            failed = summary_counts["failed"]
            error = summary_counts["error"]
            skipped = summary_counts["skipped"]
            total = summary_total
        else:
            total = raw_total
    else:
        total = raw_total

    return {
        "passed": passed,
        "failed": failed,
        "error": error,
        "skipped": skipped,
        "total": total,
        "raw_total": raw_total,
        "summary_total": summary_total or raw_total,
        "summary_inconsistent": summary_inconsistent,
    }


def _extract_title(report_html: str) -> str:
    """Extract a title from the pytest HTML report or fall back to default."""
    m = re.search(r"<title>(.*?)</title>", report_html, flags=re.IGNORECASE | re.DOTALL)
    if not m:
        return "CLI Test Dashboard"
    return html.escape(m.group(1).strip() or "CLI Test Dashboard")


def build_dashboard(report_path: Path, output_dir: Path) -> Path:
    """Build a static Tailwind + Chart.js dashboard HTML."""
    text = report_path.read_text(encoding="utf-8", errors="ignore")
    counts = _infer_counts(text)
    title = _extract_title(text)

    # Timestamp similar to Product Catalog API dashboard
    now = datetime.now()
    run_date = now.strftime("%Y-%m-%d")
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

    passed = counts["passed"]
    failed = counts["failed"]
    error = counts["error"]
    skipped = counts["skipped"]
    total = counts["total"] or 1  # avoid div/0
    pass_rate = round(100.0 * passed / total, 1)

    inconsistency_banner = ""
    if counts.get("summary_inconsistent"):
        inconsistency_banner = """
      <div class="mb-4 rounded-lg border border-amber-400/40 bg-amber-500/5 px-4 py-3 text-sm text-amber-200">
        Detected a mismatch between the pytest summary line and the HTML table counts.
        Numbers below use the pytest summary, which is usually more accurate.
      </div>
    """

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "index.html"

    html_content = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{title}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
      tailwind.config = {{
        darkMode: 'class',
        theme: {{
          extend: {{
            colors: {{
              background: '#0f1114',
              surface: '#151820',
              border: '#1f2430',
              success: '#22c55e',
              failed: '#fb7185',
              warning: '#eab308',
              info: '#38bdf8'
            }}
          }}
        }}
      }};
    </script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
    <style>
      body {{
        background: #0f1114;
        color: #e6e8eb;
      }}
      .chart-container {{
        position: relative;
        height: 260px;
        width: 100%;
      }}
    </style>
  </head>
  <body class="min-h-screen font-sans">
    <div class="max-w-6xl mx-auto px-4 py-8">
      <header class="mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 class="text-2xl font-semibold tracking-tight">CLI Test Dashboard</h1>
          <p class="text-sm text-slate-400 mt-1">Run date: {run_date} · {timestamp}</p>
          <p class="text-xs text-slate-500 mt-1">Summary view generated from pytest HTML report.</p>
        </div>
        <a
          href="../reports/report.html"
          class="inline-flex items-center px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-sm font-medium border border-slate-700 transition"
        >
          View raw pytest HTML report
        </a>
      </header>
      {inconsistency_banner}

      <section class="grid gap-4 md:grid-cols-4 mb-8">
        <div class="bg-surface rounded-xl border border-slate-800 p-4">
          <div class="text-xs uppercase tracking-wide text-slate-400 mb-1">Total tests</div>
          <div class="text-2xl font-semibold">{total}</div>
        </div>
        <div class="bg-surface rounded-xl border border-slate-800 p-4">
          <div class="text-xs uppercase tracking-wide text-slate-400 mb-1">Passed</div>
          <div class="text-2xl font-semibold text-emerald-400">{passed}</div>
        </div>
        <div class="bg-surface rounded-xl border border-slate-800 p-4">
          <div class="text-xs uppercase tracking-wide text-slate-400 mb-1">Failed / Error</div>
          <div class="text-2xl font-semibold text-rose-400">{failed + error}</div>
        </div>
        <div class="bg-surface rounded-xl border border-slate-800 p-4">
          <div class="text-xs uppercase tracking-wide text-slate-400 mb-1">Pass rate</div>
          <div class="text-2xl font-semibold text-sky-400">{pass_rate}%</div>
        </div>
      </section>

      <section class="grid gap-6 md:grid-cols-2">
        <div class="bg-surface rounded-xl border border-slate-800 p-4">
          <h2 class="text-sm font-semibold mb-3">Result distribution</h2>
          <div class="chart-container">
            <canvas id="resultDistributionChart"></canvas>
          </div>
        </div>
        <div class="bg-surface rounded-xl border border-slate-800 p-4">
          <h2 class="text-sm font-semibold mb-3">Summary</h2>
          <p class="text-sm text-slate-300">
            This dashboard summarizes the latest test run. Counts are inferred from the pytest HTML report;
            for full details, open the raw report.
          </p>
          <ul class="mt-4 space-y-1 text-sm text-slate-300">
            <li><span class="text-slate-400">Passed:</span> {passed}</li>
            <li><span class="text-slate-400">Failed:</span> {failed}</li>
            <li><span class="text-slate-400">Error:</span> {error}</li>
            <li><span class="text-slate-400">Skipped:</span> {skipped}</li>
          </ul>
        </div>
      </section>
    </div>

    <script>
      const ctx = document.getElementById('resultDistributionChart');
      if (ctx) {{
        new Chart(ctx, {{
          type: 'doughnut',
          data: {{
            labels: ['Passed', 'Failed', 'Error', 'Skipped'],
            datasets: [{{
              data: [{passed}, {failed}, {error}, {skipped}],
              backgroundColor: [
                '#22c55e',
                '#fb7185',
                '#f97316',
                '#64748b'
              ],
              borderColor: '#020617',
              borderWidth: 1
            }}]
          }},
          options: {{
            plugins: {{
              legend: {{
                position: 'bottom',
                labels: {{
                  color: '#e5e7eb'
                }}
              }}
            }}
          }}
        }});
      }}
    </script>
  </body>
</html>
"""

    out_path.write_text(html_content, encoding="utf-8")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate CLI test dashboard HTML from pytest report.")
    parser.add_argument("--report-path", type=Path, required=True, help="Path to pytest HTML report.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Output directory where index.html will be written.",
    )
    args = parser.parse_args()

    if not args.report_path.is_file():
        raise SystemExit(f"Report path does not exist or is not a file: {args.report_path}")

    out = build_dashboard(args.report_path, args.output_dir)
    print(f"Dashboard written to {out}")


if __name__ == "__main__":
    main()

