"""ElementType enum - 10 elementos do sistema de dano elemental."""

from __future__ import annotations

from enum import Enum, auto


class ElementType(Enum):
    """Os 10 elementos do jogo. Usados em ataques, armas e fraquezas."""

    FIRE = auto()
    WATER = auto()
    ICE = auto()
    LIGHTNING = auto()
    EARTH = auto()
    HOLY = auto()
    DARKNESS = auto()
    CELESTIAL = auto()
    PSYCHIC = auto()
    FORCE = auto()
