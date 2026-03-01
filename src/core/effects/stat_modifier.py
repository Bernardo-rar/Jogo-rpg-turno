"""Dataclass para modificacao de stat por efeito."""

from __future__ import annotations

from dataclasses import dataclass

from src.core.effects.modifiable_stat import ModifiableStat


@dataclass(frozen=True)
class StatModifier:
    """Modificacao flat + percentual num stat derivado.

    Aplicacao: final = (base + flat) * (1.0 + percent / 100.0)
    Valores negativos para debuffs (ex: flat=-5, percent=-10.0).
    """

    stat: ModifiableStat
    flat: int = 0
    percent: float = 0.0
