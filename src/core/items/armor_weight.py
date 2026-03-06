"""Categorias de peso de armadura."""

from enum import Enum, auto


class ArmorWeight(Enum):
    """Leve, media, pesada."""

    LIGHT = auto()
    MEDIUM = auto()
    HEAVY = auto()
