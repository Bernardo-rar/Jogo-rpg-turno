"""Tiers de raridade de itens (armaduras, acessorios)."""

from enum import Enum, auto


class ItemRarity(Enum):
    """Comum, incomum, raro, lendario."""

    COMMON = auto()
    UNCOMMON = auto()
    RARE = auto()
    LEGENDARY = auto()
