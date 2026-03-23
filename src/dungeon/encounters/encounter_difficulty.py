"""Niveis de dificuldade de encounter."""

from enum import Enum, auto


class EncounterDifficulty(Enum):
    """Dificuldade do encounter — afeta composicao e numero de monstros."""

    EASY = auto()
    MEDIUM = auto()
    HARD = auto()
    ELITE = auto()
