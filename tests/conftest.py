"""Pytest configuration and shared fixtures."""

import os

import pytest


@pytest.fixture(scope="session")
def cli_base_command():
    """Base CLI command from env or default. Set CLI_CMD for your binary (e.g. 'python -m mycli')."""
    return os.environ.get("CLI_CMD", "echo").split()
