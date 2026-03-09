"""Testes para SpellSlot frozen dataclass e funcoes de budget."""

from __future__ import annotations

import pytest

from src.core.combat.action_economy import ActionType
from src.core.skills.skill import Skill
from src.core.skills.skill_effect import SkillEffect
from src.core.skills.skill_effect_type import SkillEffectType
from src.core.skills.spell_slot import (
    SpellSlot,
    add_skill_to_slot,
    fits_in_slot,
    total_slot_cost,
)
from src.core.skills.target_type import TargetType


def _make_skill(skill_id: str, slot_cost: int) -> Skill:
    return Skill(
        skill_id=skill_id, name=skill_id.title(), mana_cost=10,
        action_type=ActionType.ACTION, target_type=TargetType.SINGLE_ENEMY,
        effects=(SkillEffect(effect_type=SkillEffectType.DAMAGE, base_power=10),),
        slot_cost=slot_cost,
    )


class TestSpellSlotCreation:
    def test_create_empty(self) -> None:
        slot = SpellSlot(max_cost=8)
        assert slot.max_cost == 8
        assert slot.skills == ()

    def test_create_with_skills(self) -> None:
        sk = _make_skill("zap", 3)
        slot = SpellSlot(max_cost=8, skills=(sk,))
        assert len(slot.skills) == 1

    def test_is_frozen(self) -> None:
        slot = SpellSlot(max_cost=8)
        with pytest.raises(AttributeError):
            slot.max_cost = 10  # type: ignore[misc]


class TestTotalSlotCost:
    def test_empty_slot(self) -> None:
        slot = SpellSlot(max_cost=8)
        assert total_slot_cost(slot) == 0

    def test_single_skill(self) -> None:
        slot = SpellSlot(max_cost=8, skills=(_make_skill("a", 3),))
        assert total_slot_cost(slot) == 3

    def test_multiple_skills(self) -> None:
        slot = SpellSlot(
            max_cost=10,
            skills=(_make_skill("a", 3), _make_skill("b", 4)),
        )
        assert total_slot_cost(slot) == 7


class TestFitsInSlot:
    def test_fits_when_under_budget(self) -> None:
        slot = SpellSlot(max_cost=8)
        assert fits_in_slot(slot, _make_skill("a", 5)) is True

    def test_fits_exact_budget(self) -> None:
        slot = SpellSlot(max_cost=8)
        assert fits_in_slot(slot, _make_skill("a", 8)) is True

    def test_does_not_fit_over_budget(self) -> None:
        slot = SpellSlot(max_cost=8)
        assert fits_in_slot(slot, _make_skill("a", 9)) is False

    def test_fits_with_existing_skills(self) -> None:
        slot = SpellSlot(max_cost=8, skills=(_make_skill("a", 3),))
        assert fits_in_slot(slot, _make_skill("b", 5)) is True

    def test_does_not_fit_with_existing(self) -> None:
        slot = SpellSlot(max_cost=8, skills=(_make_skill("a", 3),))
        assert fits_in_slot(slot, _make_skill("b", 6)) is False


class TestAddSkillToSlot:
    def test_add_returns_new_slot(self) -> None:
        slot = SpellSlot(max_cost=8)
        result = add_skill_to_slot(slot, _make_skill("a", 3))
        assert result is not None
        assert len(result.skills) == 1

    def test_add_preserves_max_cost(self) -> None:
        slot = SpellSlot(max_cost=8)
        result = add_skill_to_slot(slot, _make_skill("a", 3))
        assert result is not None
        assert result.max_cost == 8

    def test_add_returns_none_over_budget(self) -> None:
        slot = SpellSlot(max_cost=8)
        assert add_skill_to_slot(slot, _make_skill("a", 9)) is None

    def test_add_multiple(self) -> None:
        slot = SpellSlot(max_cost=10)
        slot2 = add_skill_to_slot(slot, _make_skill("a", 3))
        assert slot2 is not None
        slot3 = add_skill_to_slot(slot2, _make_skill("b", 4))
        assert slot3 is not None
        assert total_slot_cost(slot3) == 7
