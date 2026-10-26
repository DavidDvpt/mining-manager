"""Common values shared by lots and sessions."""

from enum import Enum


class LotAndSessionType(str, Enum):
    MINING = "MINING"
    REFINING = "REFINING"
    TRADE = "TRADE"
    CRAFTING = "CRAFTING"
