"""Module for ScriptStatus."""

from dataclasses import dataclass


@dataclass
class ScriptStatus:
    """
    Represents that status of this script run.
    """

    is_success: bool
    message: str = ""
