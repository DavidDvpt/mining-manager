"""Types of session lines."""

from enum import Enum


class SessionLineType(str, Enum):
    CONSUMED = "CONSUMED"
    PRODUCED = "PRODUCED"
