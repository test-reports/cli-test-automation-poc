# CLI Test Automation POC

Lightweight test automation layout for testing a CLI application.

## Structure

```
cli-test-automation-poc/
├── tests/
│   ├── conftest.py          # Shared fixtures (e.g. CLI command)
│   ├── test_cli_help.py     # Tests for --help
│   └── test_cli_version.py  # Tests for --version
├── core/
│   └── command_runner.py    # Run CLI commands and capture output
├── utils/
│   └── logger.py           # Logging helpers
├── config/
│   └── config.yaml         # CLI path, timeouts, etc.
├── reports/                # Test reports (e.g. JUnit, HTML)
├── requirements.txt
├── pytest.ini
├── README.md
└── .gitignore
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## Running tests

Default tests use `echo` as a placeholder CLI:

```bash
pytest
```

To test your own CLI, set the command (space-separated):

```bash
# Example: Python module
export CLI_CMD="python -m mycli"
pytest

# Example: Installed binary
export CLI_CMD="mycli"
pytest
```

## Configuration

- **config/config.yaml** — CLI command, timeout, report paths, logging.
- Override with **config/local.yaml** (gitignored) for local settings.

## Reports

Generated reports (JUnit XML, HTML, etc.) can be written under `reports/`. Add your preferred pytest plugins (e.g. `pytest-html`, `pytest-junit`) and configure them in `pytest.ini` or `pyproject.toml`.

### Viewing the HTML report in the browser (no download)

On each **push** to `poc-cli-tests`, the workflow publishes the pytest HTML report to **GitHub Pages**. You can open it in a browser without downloading.

1. **Enable GitHub Pages (one-time):** Repo → **Settings** → **Pages** → under "Build and deployment", set **Source** to **GitHub Actions**.
2. **Report URL** (after the first successful push):
   - **User/org site:** `https://<username>.github.io/cli-test-automation-poc/report.html`
   - **Project site:** `https://<username>.github.io/<repo-name>/report.html`

The artifact is still uploaded for the run; the Pages deployment gives you a stable URL to view the latest report.

---

## Complete sequence (Mac terminal)

From a Mac terminal, run these in order to set up, run tests locally, and trigger the CI workflow.

### 1. Clone and enter the repo

```bash
cd ~/Documents/GitHub
git clone https://github.com/YOUR_ORG/cli-test-automation-poc.git
cd cli-test-automation-poc
```

### 2. Switch to the workflow branch

```bash
git checkout poc-cli-tests
```

If the branch doesn’t exist yet:

```bash
git checkout -b poc-cli-tests
```

### 3. Create virtualenv and install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4. Run tests locally

```bash
pytest -v --tb=short
```

With HTML report:

```bash
mkdir -p reports
pytest -v --tb=short --html=reports/report.html --self-contained-html
```

### 5. Commit and push (triggers the GitHub Actions workflow)

```bash
git add .
git status
git commit -m "Your commit message"
git push origin poc-cli-tests
```

After the push, the **Test** workflow runs on GitHub. Open the repo → **Actions** → select the run → download the **pytest-html-report** artifact to view the HTML report.
