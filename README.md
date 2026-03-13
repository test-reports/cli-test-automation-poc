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
│   ├── logger.py           # Logging helpers
│   └── cli_dashboard.py    # HTML dashboard generator (Tailwind + Chart.js)
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

## GitHub Actions runners

Workflows use GitHub-hosted runners (for example `macos-latest`) so no self-hosted runner is required.

## Configuration

- **config/config.yaml** — CLI command, timeout, report paths, logging.
- Override with **config/local.yaml** (gitignored) for local settings.

## Reports

Generated reports (JUnit XML, HTML, etc.) can be written under `reports/`. This project’s GitHub Actions workflows generate a JUnit XML file (`reports/junit.xml`) and then build a Tailwind + Chart.js HTML dashboard from it, which is published via GitHub Pages.

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
pytest -v --tb=short --junitxml=reports/junit.xml
```

Then generate the HTML dashboard locally (optional, mirrors CI):

```bash
python -m utils.cli_dashboard --junit-path reports/junit.xml --output-dir dashboard
# Open dashboard/index.html in your browser
```

### 5. Commit and push (triggers the GitHub Actions workflow)

```bash
git add .
git status
git commit -m "Your commit message"
git push origin poc-cli-tests
```

After the push, the **Test** workflow runs on GitHub. Open the repo → **Actions** → select the run to inspect logs and test status.
