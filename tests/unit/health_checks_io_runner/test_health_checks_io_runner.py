"""Modules for HealthChecksRunnerTest."""

from __future__ import annotations

import socket
import unittest
from unittest.mock import call, patch

import pytest
from assertpy import assert_that
from src.health_checks_io_runner import health_checks_io_runner
from src.health_checks_io_runner.health_checks_io_runner import (
    HealthChecksIoRunner,
    HealthChecksPingType,
    ScriptStatus,
)


class HealthChecksRunnerTest(unittest.TestCase):
    """
    Unit tests for HealthChecksRunner.
    """

    # pylint: disable=line-too-long
    def test__run__function_to_run_returns_success__then__health_checks_endpoint_pinged__with_success(
        self,
    ):
        with patch.object(
            health_checks_io_runner.urllib.request,
            "urlopen",
            return_value=MockUrlOpen(),
        ) as mocked_urlopen:

            ping_was_successful = HealthChecksIoRunner.run(
                lambda: self.SCRIPT_STATUS_SUCCESS,
                self.FAKE_HEALTH_CHECKS_IO_URL,
            )

            assert_that(ping_was_successful).is_true()
            mocked_urlopen.assert_has_calls(
                [
                    call(
                        f"{self.FAKE_HEALTH_CHECKS_IO_URL}/START", timeout=10, data=None
                    ),
                    call(f"{self.FAKE_HEALTH_CHECKS_IO_URL}/", timeout=10, data=self.SUCCESS_MESSAGE.encode()),
                ]
            )

    def test__run__function_to_run_returns_failure__with_message__then__health_checks_endpoint_pinged__with_failure__with_failure_message(
        self,
    ):
        with patch.object(
            health_checks_io_runner.urllib.request,
            "urlopen",
            return_value=MockUrlOpen(),
        ) as mocked_urlopen:

            ping_was_successful = HealthChecksIoRunner.run(
                lambda: ScriptStatus(is_success=False, message=self.FAILURE_MESSAGE),
                self.FAKE_HEALTH_CHECKS_IO_URL,
            )

            assert_that(ping_was_successful).is_true()
            mocked_urlopen.assert_has_calls(
                [
                    call(
                        f"{self.FAKE_HEALTH_CHECKS_IO_URL}/START", timeout=10, data=None
                    ),
                    call(
                        f"{self.FAKE_HEALTH_CHECKS_IO_URL}/FAIL",
                        timeout=10,
                        data=self.FAILURE_MESSAGE.encode(),
                    ),
                ]
            )

    def test__run__function_to_run_raises_exception__then__health_checks_endpoint_pinged__with_failure__with_exception_message(
        self,
    ):
        def raise_exception(exception_message):
            raise Exception(exception_message)  # pylint: disable=broad-exception-raised

        with patch.object(
            health_checks_io_runner.urllib.request,
            "urlopen",
            return_value=MockUrlOpen(),
        ) as mocked_urlopen:

            ping_was_successful = HealthChecksIoRunner.run(
                lambda: raise_exception(self.EXCEPTION_MESSAGE),
                self.FAKE_HEALTH_CHECKS_IO_URL,
            )

            assert_that(ping_was_successful).is_true()
            mocked_urlopen.assert_has_calls(
                [
                    call(
                        f"{self.FAKE_HEALTH_CHECKS_IO_URL}/START", timeout=10, data=None
                    ),
                    call(
                        f"{self.FAKE_HEALTH_CHECKS_IO_URL}/FAIL",
                        timeout=10,
                        data=self.EXCEPTION_MESSAGE.encode(),
                    ),
                ]
            )

    def test__run__urllib_request_urlopen_fails__with_socket_error__then__returns_false(
        self,
    ):
        with patch.object(
            health_checks_io_runner.urllib.request,
            "urlopen",
            side_effect=socket.error(),
        ) as mocked_urlopen:

            ping_was_successful = HealthChecksIoRunner.run(
                lambda: self.SUCCESS_MESSAGE,
                self.FAKE_HEALTH_CHECKS_IO_URL,
            )

            assert_that(ping_was_successful).is_false()
            mocked_urlopen.assert_has_calls(
                [
                    call(
                        f"{self.FAKE_HEALTH_CHECKS_IO_URL}/START", timeout=10, data=None
                    ),
                ]
            )

    def test__run__urllib_request_urlopen_fails__with_exception__then__returns_false(
        self,
    ):
        with patch.object(
            health_checks_io_runner.urllib.request,
            "urlopen",
            side_effect=Exception(),
        ) as mocked_urlopen:

            ping_was_successful = HealthChecksIoRunner.run(
                lambda: self.SUCCESS_MESSAGE,
                self.FAKE_HEALTH_CHECKS_IO_URL,
            )

            assert_that(ping_was_successful).is_false()
            mocked_urlopen.assert_has_calls(
                [
                    call(
                        f"{self.FAKE_HEALTH_CHECKS_IO_URL}/START", timeout=10, data=None
                    ),
                ]
            )

    def test____send_status__ping_type_unknown__raises_value_error(self):
        with pytest.raises(ValueError) as excinfo:
            HealthChecksIoRunner._HealthChecksIoRunner__send_status(  # pylint: disable=protected-access
                HealthChecksPingType.UNKNOWN
            )

        assert_that(str(excinfo.value)).contains(
            f"{HealthChecksPingType.UNKNOWN} is not supported."
        )

    FAKE_HEALTH_CHECKS_IO_URL = "http://fake.url.com"
    SUCCESS_MESSAGE = "test success message"
    SCRIPT_STATUS_SUCCESS = ScriptStatus(is_success=True, message=SUCCESS_MESSAGE)
    FAILURE_MESSAGE = "test failure message"
    EXCEPTION_MESSAGE = "test exception message"
    # pylint: enable=line-too-long


class MockUrlOpen:
    """
    Fake context manager class used to mock {urllib.request.urlopen}.
    """

    def __enter__(self) -> MockUrlOpen:
        """
        Called when creating this class in a with statement.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Called when the code exits the with statement that created this class.
        """
        return


if __name__ == "__main__":
    unittest.main()
