"""Tiers de raridade de armas."""

from enum import Enum, auto


class WeaponRarity(Enum):
    """Comum, incomum, raro, lendario."""

    COMMON = auto()
    UNCOMMON = auto()
    RARE = auto()
    LEGENDARY = auto()
