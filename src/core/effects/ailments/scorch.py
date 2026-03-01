"""Scorch - DoT massivo + reducao cumulativa de MAX_HP."""

from __future__ import annotations

from src.core.effects.ailments.dot_ailment import DotAilment
from src.core.effects.modifiable_stat import ModifiableStat
from src.core.effects.stat_modifier import StatModifier

DEFAULT_MAX_HP_REDUCTION = 10


class Scorch(DotAilment):
    """Scorch: dano massivo por turno + reduz Max HP (cumulativo com STACK)."""

    def __init__(
        self,
        damage_per_tick: int,
        duration: int,
        max_hp_reduction: int = DEFAULT_MAX_HP_REDUCTION,
    ) -> None:
        super().__init__(damage_per_tick, duration)
        self._max_hp_reduction = max_hp_reduction

    @property
    def max_hp_reduction(self) -> int:
        """Reducao flat de MAX_HP."""
        return self._max_hp_reduction

    @property
    def tick_message(self) -> str:
        return f"Scorch deals {self.damage_per_tick} fire damage"

    def get_modifiers(self) -> list[StatModifier]:
        """Reduz MAX_HP alem do DoT."""
        return [
            StatModifier(
                stat=ModifiableStat.MAX_HP,
                flat=-self._max_hp_reduction,
            ),
        ]
