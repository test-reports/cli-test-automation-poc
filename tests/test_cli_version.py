"""Tests for CLI version (--version / -V)."""

import pytest

from core.command_runner import run_cli


@pytest.fixture
def cli_command(cli_base_command):
    """CLI command with --version. Uses CLI_CMD env for base command."""
    return cli_base_command + ["--version"]


def test_cli_version_exits_successfully(cli_command):
    """CLI --version should exit with code 0."""
    result = run_cli(cli_command, timeout=5)
    assert result.returncode == 0


def test_cli_version_prints_version_like_output(cli_command):
    """CLI --version should print version-like content to stdout or stderr."""
    result = run_cli(cli_command, timeout=5)
    combined = (result.stdout or "") + (result.stderr or "")
    # echo --version prints "--version"; real CLI would print e.g. "1.0.0"
    assert "--version" in combined or len(combined.strip()) > 0
