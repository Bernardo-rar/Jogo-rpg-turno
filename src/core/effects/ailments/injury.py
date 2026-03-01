"""Injury - reducao de ataque fisico e magico."""

from __future__ import annotations

from src.core.effects.ailments.debuff_ailment import DebuffAilment
from src.core.effects.modifiable_stat import ModifiableStat
from src.core.effects.stat_modifier import StatModifier


class Injury(DebuffAilment):
    """Lesao: reduz ataque fisico e magico."""

    def __init__(self, duration: int, attack_reduction_percent: float) -> None:
        phys_mod = StatModifier(
            stat=ModifiableStat.PHYSICAL_ATTACK,
            percent=-abs(attack_reduction_percent),
        )
        mag_mod = StatModifier(
            stat=ModifiableStat.MAGICAL_ATTACK,
            percent=-abs(attack_reduction_percent),
        )
        super().__init__(modifiers=[phys_mod, mag_mod], duration=duration)
