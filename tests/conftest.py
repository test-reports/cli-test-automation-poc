"""Pytest configuration and shared fixtures. Same ReportPortal pattern as test-automation repo."""

import logging
import os
from pathlib import Path

import pytest

# Load local env (e.g. RP_API_KEY) from config/local.env if present; file is gitignored
_local_env = Path(__file__).resolve().parent.parent / "config" / "local.env"
if _local_env.exists():
    from dotenv import load_dotenv
    load_dotenv(_local_env)

try:
    from reportportal_client import RPLogger
    _RP_LOGGER_AVAILABLE = True
except ImportError:
    _RP_LOGGER_AVAILABLE = False


@pytest.fixture(scope="session")
def rp_logger():
    """ReportPortal logger fixture following official pytest-reportportal example (test-automation pattern)."""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    if _RP_LOGGER_AVAILABLE:
        logging.setLoggerClass(RPLogger)
    return logger


@pytest.fixture(scope="session")
def cli_base_command():
    """Base CLI command from env or default. Set CLI_CMD for your binary (e.g. 'python -m mycli')."""
    return os.environ.get("CLI_CMD", "echo").split()
