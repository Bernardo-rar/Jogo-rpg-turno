"""Synergy behaviors — aura buffs, pack tactics, combo tracking."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.core.combat.synergy.synergy_config import CommanderAuraConfig
from src.core.effects.modifiable_stat import ModifiableStat
from src.core.effects.stat_buff import StatBuff
from src.core.effects.stat_modifier import StatModifier

if TYPE_CHECKING:
    from src.core.characters.character import Character

AURA_DURATION = 2
AURA_ATK_KEY = "synergy_aura_atk"
AURA_DEF_KEY = "synergy_aura_def"


def apply_commander_aura(
    followers: list[Character],
    config: CommanderAuraConfig,
) -> None:
    """Applies/refreshes aura buffs to alive followers."""
    for char in followers:
        if not char.is_alive:
            continue
        _refresh_aura_buff(
            char, AURA_ATK_KEY,
            ModifiableStat.PHYSICAL_ATTACK, config.atk_bonus_pct,
        )
        _refresh_aura_buff(
            char, AURA_DEF_KEY,
            ModifiableStat.PHYSICAL_DEFENSE, config.def_bonus_pct,
        )


def remove_commander_aura(followers: list[Character]) -> None:
    """Removes aura buffs from all followers."""
    for char in followers:
        _remove_by_key(char, AURA_ATK_KEY)
        _remove_by_key(char, AURA_DEF_KEY)


def check_pack_same_target(
    attacks: dict[str, str],
    bonus_pct: float,
) -> dict[str, float]:
    """Returns bonus % for each attacker who hit a same target.

    First attacker on each target gets no bonus. Subsequent ones do.
    """
    target_order: dict[str, list[str]] = {}
    for attacker, target in attacks.items():
        target_order.setdefault(target, []).append(attacker)
    result: dict[str, float] = {}
    for attackers in target_order.values():
        for attacker in attackers[1:]:
            result[attacker] = bonus_pct
    return result


def _refresh_aura_buff(
    char: Character,
    stacking_key: str,
    stat: ModifiableStat,
    percent: float,
) -> None:
    """Adds or refreshes an aura buff on a character."""
    _remove_by_key(char, stacking_key)
    modifier = StatModifier(stat=stat, percent=percent)
    buff = _AuraBuff(modifier, AURA_DURATION, stacking_key)
    char.effect_manager.add_effect(buff)


def _remove_by_key(char: Character, key: str) -> None:
    """Removes all effects matching the stacking key."""
    char.effect_manager.remove_by_key(key)


class _AuraBuff(StatBuff):
    """StatBuff with custom stacking key for aura identification."""

    def __init__(
        self,
        modifier: StatModifier,
        duration: int,
        key: str,
    ) -> None:
        super().__init__(modifier=modifier, duration=duration)
        self._aura_key = key

    @property
    def stacking_key(self) -> str:
        return self._aura_key
