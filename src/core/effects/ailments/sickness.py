"""Sickness - reducao de cura recebida."""

from __future__ import annotations

from src.core.effects.ailments.debuff_ailment import DebuffAilment
from src.core.effects.modifiable_stat import ModifiableStat
from src.core.effects.stat_modifier import StatModifier


class Sickness(DebuffAilment):
    """Doenca: reduz cura/recuperacao recebida."""

    def __init__(self, duration: int, recovery_reduction_percent: float) -> None:
        modifier = StatModifier(
            stat=ModifiableStat.HEALING_RECEIVED,
            percent=-abs(recovery_reduction_percent),
        )
        super().__init__(modifiers=[modifier], duration=duration)
