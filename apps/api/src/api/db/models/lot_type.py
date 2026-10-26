"""Types of lots."""

from enum import Enum


class LotType(str, Enum):
    MINING = "MINING"
    REFINING = "REFINING"
    TRADE = "TRADE"
    CRAFTING = "CRAFTING"
