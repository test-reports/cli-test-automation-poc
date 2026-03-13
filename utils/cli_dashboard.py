"""Generate a static HTML dashboard for CLI test runs.

The dashboard is a single self-contained HTML file with:
- Tailwind CSS (via CDN) for layout and styling
- Chart.js (via CDN) for basic charts

It reads a JUnit XML report and derives summary + individual test rows,
mirroring the Product Catalog API dashboard approach (structured data
first, then HTML).

Intended usage from CI:
- After pytest generates reports/junit.xml (via --junitxml)
- Call: python -m utils.cli_dashboard --junit-path reports/junit.xml --output-dir dashboard
- Publish dashboard/ via GitHub Pages.
"""

from __future__ import annotations

import argparse
import html
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
from zoneinfo import ZoneInfo
import xml.etree.ElementTree as ET


def _escape_html(s: str) -> str:
    if not s:
        return ""
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _parse_junit(junit_path: Path) -> Tuple[Dict[str, int], List[Tuple[str, str, str]]]:
    """Parse a JUnit XML report into counts and test rows.

    Returns:
        (counts, rows) where:
          counts = {passed, failed, error, skipped, total}
          rows   = list of (label, status, badge_class)
    """
    tree = ET.parse(junit_path)
    root = tree.getroot()

    testcases = root.findall(".//testcase")

    counts = {
        "passed": 0,
        "failed": 0,
        "error": 0,
        "skipped": 0,
        "total": 0,
    }
    rows: List[Tuple[str, str, str]] = []

    def status_badge(tag: str) -> Tuple[str, str]:
        t = tag.lower()
        if t == "passed":
            return "Passed", "bg-emerald-500/20 text-emerald-400 border border-emerald-500/50"
        if t == "failed":
            return "Failed", "bg-rose-500/20 text-rose-400 border border-rose-500/50"
        if t == "error":
            return "Error", "bg-amber-500/20 text-amber-300 border border-amber-500/50"
        if t == "skipped":
            return "Skipped", "bg-slate-500/20 text-slate-300 border border-slate-500/50"
        return "", ""

    for tc in testcases:
        classname = tc.get("classname", "") or ""
        name = tc.get("name", "") or ""
        label = f"{classname}::{name}" if classname else name
        label = _escape_html(label)

        status = "passed"
        if tc.find("failure") is not None:
            status = "failed"
        elif tc.find("error") is not None:
            status = "error"
        elif tc.find("skipped") is not None:
            status = "skipped"

        status_label, badge = status_badge(status)
        counts[status] += 1
        counts["total"] += 1

        rows.append((label, status_label, badge))

    return counts, rows


def summarize_junit(junit_path: Path) -> Dict[str, int]:
    """Return only aggregate counts from a JUnit XML report."""
    counts, _ = _parse_junit(junit_path)
    return counts


def build_dashboard(junit_path: Path, output_dir: Path) -> Path:
    """Build a static Tailwind + Chart.js dashboard HTML from JUnit XML."""
    counts, test_rows = _parse_junit(junit_path)
    title = "CLI Test Dashboard"

    # Timestamp similar to Product Catalog API dashboard, pinned to LA time (PST/PDT)
    la_tz = ZoneInfo("America/Los_Angeles")
    now = datetime.now(tz=la_tz)
    run_date = now.strftime("%Y-%m-%d")
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S %Z")

    passed = counts["passed"]
    failed = counts["failed"]
    error = counts["error"]
    skipped = counts["skipped"]
    total = counts["total"] or 1  # avoid div/0
    pass_rate = round(100.0 * passed / total, 1)

    # Extract individual tests similar to Product Catalog API dashboard
    if test_rows:
        table_rows_html_parts: List[str] = []
        for idx, (label, status, badge_class) in enumerate(test_rows, start=1):
            table_rows_html_parts.append(
                f'<tr class="border-b border-slate-800 hover:bg-slate-800/40">'
                f'<td class="py-3 px-3 w-12 text-xs text-slate-500 tabular-nums">{idx}</td>'
                f'<td class="py-3 px-3 text-sm text-slate-200">{label}</td>'
                f'<td class="py-3 px-3 text-sm">'
                f'<span class="inline-flex items-center px-2.5 py-0.5 rounded text-xs font-medium {badge_class}">{status}</span>'
                f"</td>"
                f"</tr>"
            )
        tests_table_html = "\n".join(table_rows_html_parts)
    else:
        tests_table_html = (
            '<tr><td colspan="3" class="py-4 px-3 text-sm text-slate-500">'
            "No individual test rows could be extracted from the JUnit XML report."
            "</td></tr>"
        )

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
          <p class="text-xs text-slate-500 mt-1">Summary view generated from JUnit XML report.</p>
        </div>
      </header>
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
            This dashboard summarizes the latest test run. Counts and test list are derived from the JUnit XML report.
          </p>
          <ul class="mt-4 space-y-1 text-sm text-slate-300">
            <li><span class="text-slate-400">Passed:</span> {passed}</li>
            <li><span class="text-slate-400">Failed:</span> {failed}</li>
            <li><span class="text-slate-400">Error:</span> {error}</li>
            <li><span class="text-slate-400">Skipped:</span> {skipped}</li>
          </ul>
        </div>
      </section>

      <section class="mt-8 bg-surface rounded-xl border border-slate-800 p-4">
        <h2 class="text-sm font-semibold mb-3">All tests</h2>
        <div class="overflow-x-auto">
          <table class="min-w-full text-left text-sm">
            <thead>
              <tr class="border-b border-slate-800 text-xs uppercase tracking-wide text-slate-500">
                <th class="py-2 px-3 w-12">#</th>
                <th class="py-2 px-3">Test</th>
                <th class="py-2 px-3">Status</th>
              </tr>
            </thead>
            <tbody>
{tests_table_html}
            </tbody>
          </table>
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
    parser = argparse.ArgumentParser(description="Generate CLI test dashboard HTML from JUnit XML.")
    parser.add_argument("--junit-path", type=Path, required=True, help="Path to JUnit XML report.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Output directory where index.html will be written.",
    )
    args = parser.parse_args()

    if not args.junit_path.is_file():
        raise SystemExit(f"JUnit path does not exist or is not a file: {args.junit_path}")

    out = build_dashboard(args.junit_path, args.output_dir)
    print(f"Dashboard written to {out}")


if __name__ == "__main__":
    main()

