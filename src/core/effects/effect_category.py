"""Categoria de efeito (buff ou debuff)."""

from enum import Enum, auto


class EffectCategory(Enum):
    """Categoria do efeito para filtragem e display."""

    BUFF = auto()
    DEBUFF = auto()
    AILMENT = auto()
