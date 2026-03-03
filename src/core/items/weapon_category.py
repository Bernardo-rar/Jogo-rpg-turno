"""Categorias de proficiencia de armas."""

from enum import Enum, auto


class WeaponCategory(Enum):
    """Determina quais classes podem equipar a arma."""

    SIMPLE = auto()
    MARTIAL = auto()
    MAGICAL = auto()
