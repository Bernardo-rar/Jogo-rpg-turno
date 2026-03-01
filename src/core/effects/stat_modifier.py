"""Dataclass para modificacao de stat por efeito."""

from __future__ import annotations

from dataclasses import dataclass

from src.core.effects.modifiable_stat import ModifiableStat

PERCENT_DIVISOR = 100.0


@dataclass(frozen=True)
class StatModifier:
    """Modificacao flat + percentual num stat derivado.

    Aplicacao: final = (base + flat) * (1.0 + percent / PERCENT_DIVISOR)
    Valores negativos para debuffs (ex: flat=-5, percent=-10.0).
    """

    stat: ModifiableStat
    flat: int = 0
    percent: float = 0.0

    def apply(self, base: int) -> int:
        """Aplica este modificador ao valor base. Resultado minimo = 0."""
        return max(0, int(
            (base + self.flat) * (1.0 + self.percent / PERCENT_DIVISOR),
        ))
