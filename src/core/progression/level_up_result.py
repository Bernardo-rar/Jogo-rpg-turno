"""Resultado de um level up: novo nivel e pontos a distribuir."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LevelUpResult:
    """Resultado imutavel de um level up."""

    new_level: int
    physical_points: int
    mental_points: int

    @property
    def total_points(self) -> int:
        return self.physical_points + self.mental_points
