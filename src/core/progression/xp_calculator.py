"""XP Calculator — calcula XP ganho apos um combate."""

from __future__ import annotations

from dataclasses import dataclass
from math import floor

from src.core.progression.xp_reward_config import XpRewardConfig


@dataclass(frozen=True)
class CombatXpInput:
    """Dados do combate para calculo de XP."""

    encounter_type: str
    tier: int
    rounds: int
    party_deaths: int
    xp_run_mult: float = 1.0


def calculate_combat_xp(
    combat: CombatXpInput, config: XpRewardConfig,
) -> int:
    """Calcula XP final de um combate.

    Formula: floor(base * no_death * fast_clear * run_mult)
    """
    base = config.base_xp(combat.encounter_type, combat.tier)
    if base == 0:
        return 0
    mult = _compute_multiplier(combat, config)
    return floor(base * mult)


def _compute_multiplier(
    combat: CombatXpInput, config: XpRewardConfig,
) -> float:
    """Calcula multiplicador total de XP."""
    mult = combat.xp_run_mult
    if combat.party_deaths == 0:
        mult *= config.bonuses.no_death_mult
    if combat.rounds <= config.bonuses.fast_clear_max_rounds:
        mult *= config.bonuses.fast_clear_mult
    return mult
