"""Calcula numero de slots de acessorio baseado em CHA thresholds."""

from __future__ import annotations

BASE_ACCESSORY_SLOTS = 2
_BONUS_KEY = "magic_item_slots"


def calculate_accessory_slots(threshold_bonuses: dict[str, int]) -> int:
    """Retorna total de slots: 2 base + bonus de CHA thresholds."""
    return BASE_ACCESSORY_SLOTS + threshold_bonuses.get(_BONUS_KEY, 0)
