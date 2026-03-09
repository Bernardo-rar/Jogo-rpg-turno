"""Tipos de alvo para skills."""

from enum import Enum, auto


class TargetType(Enum):
    """Quem a skill pode atingir."""

    SELF = auto()
    SINGLE_ALLY = auto()
    SINGLE_ENEMY = auto()
    ALL_ALLIES = auto()
    ALL_ENEMIES = auto()
