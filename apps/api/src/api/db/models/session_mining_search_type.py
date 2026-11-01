"""Search types available for mining sessions."""

from enum import Enum


class SessionMiningSearchType(str, Enum):
    E = "E"
    O = "O"
    T = "T"
    EO = "EO"
    ET = "ET"
    OT = "OT"
    EOT = "EOT"
