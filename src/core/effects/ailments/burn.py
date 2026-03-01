"""Burn - DoT de fogo + reducao de cura recebida."""

from __future__ import annotations

from src.core.effects.ailments.dot_ailment import DotAilment
from src.core.effects.modifiable_stat import ModifiableStat
from src.core.effects.stat_modifier import StatModifier

DEFAULT_HEALING_REDUCTION = 30.0


class Burn(DotAilment):
    """Queimadura: dano de fogo por turno + reduz cura recebida em %."""

    def __init__(
        self,
        damage_per_tick: int,
        duration: int,
        healing_reduction_percent: float = DEFAULT_HEALING_REDUCTION,
    ) -> None:
        super().__init__(damage_per_tick, duration)
        self._healing_reduction = healing_reduction_percent

    @property
    def healing_reduction_percent(self) -> float:
        """Percentual de reducao na cura recebida."""
        return self._healing_reduction

    @property
    def tick_message(self) -> str:
        return f"Burn deals {self.damage_per_tick} fire damage"

    def get_modifiers(self) -> list[StatModifier]:
        """Reduz cura recebida alem do DoT."""
        return [
            StatModifier(
                stat=ModifiableStat.HEALING_RECEIVED,
                percent=-self._healing_reduction,
            ),
        ]
