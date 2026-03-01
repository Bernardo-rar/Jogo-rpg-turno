"""Dataclass para resultado de tick de efeito."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TickResult:
    """Resultado de um tick de efeito por turno.

    Usado para comunicar dano DoT, cura HoT, drain de mana, etc.
    Defaults todos zero (tick sem efeito visivel).
    """

    damage: int = 0
    healing: int = 0
    mana_change: int = 0
    message: str = ""
