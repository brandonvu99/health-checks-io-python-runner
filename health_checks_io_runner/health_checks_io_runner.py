"""Module for HealthChecksRunner."""

from __future__ import annotations

import logging
import socket
import urllib.error
import urllib.request
from enum import Enum
from typing import Callable

from health_checks_io_runner.script_status import ScriptStatus

logger = logging.getLogger(__name__)


class HealthChecksIoRunner:  # pylint: disable=too-few-public-methods
    """
    Class that will run a function that returns a {ScriptStatus},
    and send that status to a healthchecks.io instance.
    """

    @staticmethod
    def run(
        function_to_run: Callable[..., ScriptStatus],
        health_checks_io_base_url: str,
    ) -> bool:
        """
        Sends a "start" ping to the Healthchecks.io, runs {function_to_run},
        and sends either:
            1) a "success" ping to Healthchecks.io if the {function_to_run}
               returned a successful {ScriptStatus}, or
            2) a "failure" ping to Healthchecks.io if the {function_to_run}
               returned a failure {ScriptStatus}.

        Arguments:
            function_to_run (Callable): a function that returns a ScriptStatus
            health_checks_io_base_url (str): base url for your Healthchecks.io instance
                                             (e.g. "http://healthchecksio.myhomeserver.com")
        Returns:
            bool: True if any ping was successful, false otherwise.
        """
        if not HealthChecksIoRunner.__base_url_points_to_a_real_running_instance(
            health_checks_io_base_url
        ):
            logger.error(
                "The given [%s] does not point to a real running instance of Healthschecks.io. The supplied [%s] will still be ran, but no Healthchecks.io pings will be sent.",
                f"{health_checks_io_base_url=}",
                f"{function_to_run=}",
            )
            function_to_run()
            return False

        HealthChecksIoRunner.__send_status(
            HealthChecksPingType.START, health_checks_io_base_url
        )

        try:
            script_status = function_to_run()
            if script_status.is_success:
                return HealthChecksIoRunner.__send_status(
                    HealthChecksPingType.SUCCESS,
                    health_checks_io_base_url,
                    script_status.message,
                )

            return HealthChecksIoRunner.__send_status(
                HealthChecksPingType.FAIL,
                health_checks_io_base_url,
                script_status.message,
            )
        except Exception as e:  # pylint: disable=broad-exception-caught
            return HealthChecksIoRunner.__send_status(
                HealthChecksPingType.FAIL, health_checks_io_base_url, str(e)
            )

    @staticmethod
    def __base_url_points_to_a_real_running_instance(
        health_checks_io_base_url: str,
    ) -> bool:
        """
        Checks if getting {health_checks_io_base_url} will return expected errors for a real
        running instance of Healthchecks.io.

        Returns:
            (bool): True if and only if the given {health_checks_io_base_url} points to a real
                    running instance of Healthchecks.io.
        """

        def base_url_points_to_health_checks_io_home_page() -> bool:
            with urllib.request.urlopen(health_checks_io_base_url) as f:
                response = f.read().decode("utf8")
            response_has_github_link_html = (
                '<a href="https://github.com/healthchecks/healthchecks">github</a>'
                in response
            )
            return response_has_github_link_html

        def base_url_with_random_check_uuid_returns_404() -> bool:
            try:
                with urllib.request.urlopen("http://192.168.0.70:8529/sadfff") as f:
                    pass
                return False
            except urllib.error.HTTPError as e:
                response_has_health_checks_error_string = (
                    "Using the URLconf defined in <code>hc.urls</code>,"
                    in str(e.read().decode("utf8"))
                )
                return response_has_health_checks_error_string

        return (
            base_url_points_to_health_checks_io_home_page()
            and base_url_with_random_check_uuid_returns_404()
        )

    @staticmethod
    def __send_status(
        ping_type: HealthChecksPingType,
        health_checks_io_base_url: str,
        message: str = None,
    ) -> bool:
        """
        Pings the healthchecks.io with some status.

        Arguments:
            ping_type (HealthChecksPingType): what type of ping to send
            health_checks_io_base_url (str): base url for your healthchecks.io instance
                                             (e.g. "http://healthchecksio.myhomeserver.com")
            message (str): a message to send with the ping
        Returns:
            bool: True if the ping was successful, false otherwise.
        """
        if ping_type == HealthChecksPingType.UNKNOWN:
            raise ValueError(f"{HealthChecksPingType.UNKNOWN} is not supported.")
        url_to_ping = f"{health_checks_io_base_url}/{ping_type.value}"
        try:
            with urllib.request.urlopen(
                url_to_ping,
                timeout=10,
                data=message.encode() if message else None,
            ):
                pass
            logger.info("Pinged a %s to %s.", ping_type, url_to_ping)
            return True
        except (socket.error, Exception) as e:  # pylint: disable=broad-exception-caught
            logger.error(
                "Healthchecks %s ping with message %s failed due to: %s",
                ping_type,
                message,
                e,
            )

        return False


class HealthChecksPingType(Enum):
    """
    Enum representing the types of pings we can do for healthchecks.io.
    Values are the endpoint name in healthchecks.io for each ping type, except for UNKNOWN.
    """

    UNKNOWN = 0
    START = "START"
    SUCCESS = ""
    FAIL = "FAIL"
