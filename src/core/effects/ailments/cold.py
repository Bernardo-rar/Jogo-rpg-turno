"""Cold - debuff de speed."""

from __future__ import annotations

from src.core.effects.ailments.debuff_ailment import DebuffAilment
from src.core.effects.modifiable_stat import ModifiableStat
from src.core.effects.stat_modifier import StatModifier


class Cold(DebuffAilment):
    """Frio: reduz speed durante a duracao."""

    def __init__(self, duration: int, speed_reduction_percent: float) -> None:
        modifier = StatModifier(
            stat=ModifiableStat.SPEED,
            percent=-abs(speed_reduction_percent),
        )
        super().__init__(modifiers=[modifier], duration=duration)
