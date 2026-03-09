"""Calcula numero de skill slots baseado em INT thresholds."""

from __future__ import annotations

BASE_SKILL_SLOTS = 3
_BONUS_KEY = "skill_slots"


def calculate_skill_slots(threshold_bonuses: dict[str, int]) -> int:
    """Retorna total de slots: 3 base + bonus de INT thresholds."""
    return BASE_SKILL_SLOTS + threshold_bonuses.get(_BONUS_KEY, 0)
