"""Factory functions para criacao ergonomica de buffs e debuffs."""

from __future__ import annotations

from src.core.effects.modifiable_stat import ModifiableStat
from src.core.effects.stat_buff import StatBuff
from src.core.effects.stat_debuff import StatDebuff
from src.core.effects.stat_modifier import StatModifier


def create_flat_buff(
    stat: ModifiableStat, flat: int, duration: int,
) -> StatBuff:
    """Cria buff com modificacao flat. Ex: +10 Physical Attack por 3 turnos."""
    modifier = StatModifier(stat=stat, flat=flat)
    return StatBuff(modifier=modifier, duration=duration)


def create_percent_buff(
    stat: ModifiableStat, percent: float, duration: int,
) -> StatBuff:
    """Cria buff com modificacao percentual. Ex: +20% Speed por 2 turnos."""
    modifier = StatModifier(stat=stat, percent=percent)
    return StatBuff(modifier=modifier, duration=duration)


def create_flat_debuff(
    stat: ModifiableStat, flat: int, duration: int,
) -> StatDebuff:
    """Cria debuff com reducao flat. Recebe valor positivo, nega internamente."""
    modifier = StatModifier(stat=stat, flat=-abs(flat))
    return StatDebuff(modifier=modifier, duration=duration)


def create_percent_debuff(
    stat: ModifiableStat, percent: float, duration: int,
) -> StatDebuff:
    """Cria debuff com reducao percentual. Recebe valor positivo, nega internamente."""
    modifier = StatModifier(stat=stat, percent=-abs(percent))
    return StatDebuff(modifier=modifier, duration=duration)


def create_combined_buff(
    stat: ModifiableStat, flat: int, percent: float, duration: int,
) -> StatBuff:
    """Cria buff com flat + percentual combinados."""
    modifier = StatModifier(stat=stat, flat=flat, percent=percent)
    return StatBuff(modifier=modifier, duration=duration)


def create_combined_debuff(
    stat: ModifiableStat, flat: int, percent: float, duration: int,
) -> StatDebuff:
    """Cria debuff com flat + percentual. Recebe positivos, nega internamente."""
    modifier = StatModifier(stat=stat, flat=-abs(flat), percent=-abs(percent))
    return StatDebuff(modifier=modifier, duration=duration)
