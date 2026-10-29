"""Kinds of specialized lots."""

from enum import Enum


class LotKind(str, Enum):
    TOOL = "TOOL"
    ENHANCER = "ENHANCER"
    MATERIAL = "MATERIAL"
