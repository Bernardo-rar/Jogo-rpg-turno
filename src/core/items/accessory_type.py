"""Tipos de acessorio."""

from enum import Enum, auto


class AccessoryType(Enum):
    """Amuleto, anel, capa, bracelete."""

    AMULET = auto()
    RING = auto()
    CLOAK = auto()
    BRACELET = auto()
