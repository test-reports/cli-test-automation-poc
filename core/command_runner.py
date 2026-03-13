"""CLI command runner for test automation."""

import subprocess
from typing import Optional


def run_cli(
    args: list[str],
    cwd: Optional[str] = None,
    env: Optional[dict[str, str]] = None,
    timeout: Optional[int] = None,
) -> subprocess.CompletedProcess:
    """
    Run a CLI command and return the result.

    Args:
        args: Command and arguments as a list (e.g. ["mycli", "--help"]).
        cwd: Working directory for the command.
        env: Optional environment variables to merge with current env.
        timeout: Optional timeout in seconds.

    Returns:
        CompletedProcess with returncode, stdout, stderr.
    """
    full_env = None
    if env is not None:
        import os
        full_env = {**os.environ, **env}

    return subprocess.run(
        args,
        capture_output=True,
        text=True,
        cwd=cwd,
        env=full_env,
        timeout=timeout,
    )
