"""Module for HealthChecksRunner."""

# TODO(): move this entire file into its own git repo that can be cloned by all your scripts.
from __future__ import annotations

import logging
import socket
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
        Sends a "start" ping to the healthchecks.io, runs {function_to_run},
        and sends either:
            1) a "success" ping to healthchecks.io if the {function_to_run}
               returned a successful {ScriptStatus}, or
            2) a "failure" ping to healthchecks.io if the {function_to_run}
               returned a failure {ScriptStatus}.

        Arguments:
            function_to_run (Callable): a function that returns a ScriptStatus
            health_checks_io_base_url (str): base url for your healthchecks.io instance
                                             (e.g. "http://healthchecksio.myhomeserver.com")
        Returns:
            bool: True if any ping was successful, false otherwise.
        """
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

    # TODO(): expose this function? right now, it's essentially a private method bc
    # it's a staticmethod and the __ name prefix. name mangling makes it essentially private.
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
