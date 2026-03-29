"""Aplica subclass ao personagem — skills + passive bonuses."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.core.effects.buff_factory import create_percent_buff
from src.core.effects.modifiable_stat import ModifiableStat
from src.core.progression.subclass_config import SubclassOption

if TYPE_CHECKING:
    from src.core.characters.character import Character

_PERMANENT_DURATION = 999


def apply_subclass(char: Character, option: SubclassOption) -> None:
    """Aplica subclass: adiciona passive bonuses como buffs permanentes."""
    for bonus in option.passive_bonuses:
        _apply_stat_bonus(char, bonus.stat, bonus.percent)


def _apply_stat_bonus(
    char: Character, stat_name: str, percent: float,
) -> None:
    """Aplica bonus percentual como buff permanente."""
    try:
        stat = ModifiableStat[stat_name]
    except KeyError:
        return
    buff = create_percent_buff(stat, percent, _PERMANENT_DURATION)
    char.effect_manager.add_effect(buff)
