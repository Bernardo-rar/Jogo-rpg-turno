"""Calcula budget de spell slots baseado no level."""

from __future__ import annotations

from src.core.skills.slot_config import LEVEL_10_THRESHOLD, SlotConfig


def calculate_slot_budget(level: int, config: SlotConfig) -> int:
    """Budget por slot = base + (level-1) * per_level + bonus_lv10.

    Exemplo: level 1 = 8, level 5 = 12, level 10 = 18.
    """
    base = config.base_slot_budget
    scaling = (level - 1) * config.budget_per_level
    bonus = config.level_10_bonus if level >= LEVEL_10_THRESHOLD else 0
    return base + scaling + bonus
