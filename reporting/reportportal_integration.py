"""
ReportPortal integration module for test result reporting.

This module provides configuration and helpers for ReportPortal integration.
ReportPortal uses pytest-reportportal plugin which sends results in real-time
during test execution, so this module mainly provides configuration helpers.
Same pattern as test-automation repo.
"""

import os
from typing import Optional


class ReportPortalIntegration:
    """ReportPortal integration handler for test result reporting."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        project: Optional[str] = None,
        launch_name: Optional[str] = None,
    ):
        """
        Initialize ReportPortal integration.

        Args:
            api_key: ReportPortal API key (from pytest.ini or env var)
            endpoint: ReportPortal endpoint URL (from pytest.ini or env var)
            project: ReportPortal project name (from pytest.ini or env var)
            launch_name: ReportPortal launch name (optional, can be set per run)
        """
        self.api_key = api_key or os.getenv("RP_API_KEY")
        self.endpoint = endpoint or os.getenv("RP_ENDPOINT", "http://localhost:8080")
        self.project = project or os.getenv("RP_PROJECT", "superadmin_personal")
        self.launch_name = launch_name or os.getenv("RP_LAUNCH", "CLI_Test_Launch")

    def is_enabled(self) -> bool:
        """
        Check if ReportPortal integration is enabled.

        ReportPortal is enabled via --reportportal pytest flag, not via
        environment variables. This method checks if configuration exists.

        Returns:
            True if configured, False otherwise
        """
        return bool(self.api_key and self.endpoint and self.project)

    def get_pytest_args(self, launch_name: Optional[str] = None) -> str:
        """
        Get pytest arguments for ReportPortal integration.

        Args:
            launch_name: Override launch name (optional)

        Returns:
            Pytest arguments string for ReportPortal
        """
        if not self.is_enabled():
            return ""

        launch = launch_name or self.launch_name
        args = "--reportportal"

        if launch:
            args += f" --rp-launch={launch}"

        return args

    def get_launch_name_for_test_type(self, test_type: str) -> str:
        """
        Get ReportPortal launch name based on test type.

        Args:
            test_type: Test type (e.g. 'api', 'all-api')

        Returns:
            ReportPortal launch name
        """
        launch_mapping = {
            "api": "CLI_API_Launch",
            "all-api": "CLI_API_Launch",
        }
        return launch_mapping.get(test_type, "CLI_Test_Launch")

    def get_retry_launch_name(self, test_type: str) -> str:
        """
        Get ReportPortal launch name for retry runs.

        Args:
            test_type: Test type

        Returns:
            ReportPortal launch name for retry
        """
        base_name = self.get_launch_name_for_test_type(test_type)
        return f"{base_name}_Retry"
