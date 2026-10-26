"""Types of mining loot."""

from enum import Enum


class MiningLootType(str, Enum):
    E = "E"
    O = "O"
    OE = "OE"
