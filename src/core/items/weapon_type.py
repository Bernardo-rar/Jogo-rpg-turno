"""Familias de armas."""

from enum import Enum, auto


class WeaponType(Enum):
    """Tipo/familia da arma (espada, adaga, arco, etc.)."""

    SWORD = auto()
    DAGGER = auto()
    BOW = auto()
    STAFF = auto()
    HAMMER = auto()
    LANCE = auto()
    MACE = auto()
    FIST = auto()
