"""Weakness - reducao de defesa fisica e magica."""

from __future__ import annotations

from src.core.effects.ailments.debuff_ailment import DebuffAilment
from src.core.effects.modifiable_stat import ModifiableStat
from src.core.effects.stat_modifier import StatModifier


class Weakness(DebuffAilment):
    """Fraqueza: reduz defesa fisica e magica."""

    def __init__(self, duration: int, defense_reduction_percent: float) -> None:
        phys_mod = StatModifier(
            stat=ModifiableStat.PHYSICAL_DEFENSE,
            percent=-abs(defense_reduction_percent),
        )
        mag_mod = StatModifier(
            stat=ModifiableStat.MAGICAL_DEFENSE,
            percent=-abs(defense_reduction_percent),
        )
        super().__init__(modifiers=[phys_mod, mag_mod], duration=duration)
