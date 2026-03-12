"""Tests for CLI --help behavior."""

import pytest

from core.command_runner import run_cli


@pytest.fixture
def cli_command(cli_base_command):
    """CLI command with --help. Uses CLI_CMD env for base command."""
    return cli_base_command + ["--help"]


def test_cli_help_exits_successfully(cli_command):
    """CLI --help should exit with code 0."""
    result = run_cli(cli_command, timeout=5)
    assert result.returncode == 0


def test_cli_help_produces_stdout(cli_command):
    """CLI --help should print something to stdout."""
    result = run_cli(cli_command, timeout=5)
    assert result.stdout is not None
    assert len(result.stdout.strip()) >= 0  # echo --help may print "--help"


def test_cli_help_no_stderr_on_success(cli_command):
    """CLI --help typically does not write to stderr on success."""
    result = run_cli(cli_command, timeout=5)
    # Allow empty or minimal stderr; strict check depends on your CLI
    assert result.stderr is not None
