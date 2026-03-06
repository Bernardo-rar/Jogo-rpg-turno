"""Testes para accessory_slots calculator."""

from __future__ import annotations

from src.core.items.accessory_slots import (
    BASE_ACCESSORY_SLOTS,
    calculate_accessory_slots,
)


class TestAccessorySlots:
    def test_base_slots(self) -> None:
        assert calculate_accessory_slots({}) == BASE_ACCESSORY_SLOTS

    def test_base_is_two(self) -> None:
        assert BASE_ACCESSORY_SLOTS == 2

    def test_one_threshold_adds_one(self) -> None:
        bonuses = {"magic_item_slots": 1}
        assert calculate_accessory_slots(bonuses) == 3

    def test_multiple_thresholds(self) -> None:
        bonuses = {"magic_item_slots": 3}
        assert calculate_accessory_slots(bonuses) == 5
