"""Testes para calculate_skill_slots."""

from __future__ import annotations

from src.core.skills.skill_slots_calculator import (
    BASE_SKILL_SLOTS,
    calculate_skill_slots,
)


class TestCalculateSkillSlots:
    def test_base_is_three(self) -> None:
        assert BASE_SKILL_SLOTS == 3

    def test_no_bonuses(self) -> None:
        assert calculate_skill_slots({}) == 3

    def test_with_one_int_threshold(self) -> None:
        bonuses = {"skill_slots": 1}
        assert calculate_skill_slots(bonuses) == 4

    def test_with_multiple_thresholds(self) -> None:
        bonuses = {"skill_slots": 3}
        assert calculate_skill_slots(bonuses) == 6

    def test_ignores_unrelated_bonuses(self) -> None:
        bonuses = {"mana_mod": 5, "def_magical_mod": 2}
        assert calculate_skill_slots(bonuses) == 3
