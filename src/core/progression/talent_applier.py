"""Aplica talento ao personagem — buffs permanentes."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.core.effects.buff_factory import create_percent_buff
from src.core.effects.modifiable_stat import ModifiableStat
from src.core.progression.talent_config import Talent

if TYPE_CHECKING:
    from src.core.characters.character import Character

_PERMANENT_DURATION = 999


def apply_talent(char: Character, talent: Talent) -> None:
    """Aplica efeitos do talento como buffs permanentes."""
    for effect in talent.effects:
        _apply_effect(char, effect.stat, effect.percent)


def _apply_effect(char: Character, stat_name: str, percent: float) -> None:
    """Aplica bonus percentual como buff permanente."""
    try:
        stat = ModifiableStat[stat_name]
    except KeyError:
        return
    buff = create_percent_buff(stat, percent, _PERMANENT_DURATION)
    char.effect_manager.add_effect(buff)
