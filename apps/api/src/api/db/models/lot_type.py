"""Types of lots."""

from enum import Enum


class LotType(str, Enum):
    MINING = "MINING"
    REFINING = "REFINING"
    TRANSACTION = "TRANSACTION"
    CRAFTING = "CRAFTING"
