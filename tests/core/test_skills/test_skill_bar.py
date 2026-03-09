"""Testes para SkillBar."""

from __future__ import annotations

from src.core.combat.action_economy import ActionType
from src.core.skills.cooldown_tracker import CooldownTracker
from src.core.skills.skill import Skill
from src.core.skills.skill_bar import SkillBar
from src.core.skills.skill_effect import SkillEffect
from src.core.skills.skill_effect_type import SkillEffectType
from src.core.skills.spell_slot import SpellSlot
from src.core.skills.target_type import TargetType


def _make_skill(skill_id: str, slot_cost: int) -> Skill:
    return Skill(
        skill_id=skill_id, name=skill_id.title(), mana_cost=10,
        action_type=ActionType.ACTION, target_type=TargetType.SINGLE_ENEMY,
        effects=(SkillEffect(effect_type=SkillEffectType.DAMAGE, base_power=10),),
        slot_cost=slot_cost,
    )


class TestSkillBarCreation:
    def test_create_empty(self) -> None:
        bar = SkillBar(slots=())
        assert bar.slots == ()

    def test_create_with_slots(self) -> None:
        slot = SpellSlot(max_cost=8)
        bar = SkillBar(slots=(slot,))
        assert len(bar.slots) == 1

    def test_slots_returns_tuple(self) -> None:
        bar = SkillBar(slots=(SpellSlot(max_cost=8),))
        assert isinstance(bar.slots, tuple)


class TestSkillBarAllSkills:
    def test_empty_bar_no_skills(self) -> None:
        bar = SkillBar(slots=())
        assert bar.all_skills == []

    def test_skills_from_single_slot(self) -> None:
        sk = _make_skill("fireball", 5)
        slot = SpellSlot(max_cost=8, skills=(sk,))
        bar = SkillBar(slots=(slot,))
        assert len(bar.all_skills) == 1
        assert bar.all_skills[0].skill_id == "fireball"

    def test_skills_from_multiple_slots(self) -> None:
        sk1 = _make_skill("fireball", 5)
        sk2 = _make_skill("heal", 3)
        slot1 = SpellSlot(max_cost=8, skills=(sk1,))
        slot2 = SpellSlot(max_cost=8, skills=(sk2,))
        bar = SkillBar(slots=(slot1, slot2))
        ids = [s.skill_id for s in bar.all_skills]
        assert "fireball" in ids
        assert "heal" in ids

    def test_multiple_skills_in_one_slot(self) -> None:
        sk1 = _make_skill("a", 3)
        sk2 = _make_skill("b", 4)
        slot = SpellSlot(max_cost=10, skills=(sk1, sk2))
        bar = SkillBar(slots=(slot,))
        assert len(bar.all_skills) == 2


class TestSkillBarCooldown:
    def test_has_cooldown_tracker(self) -> None:
        bar = SkillBar(slots=())
        assert isinstance(bar.cooldown_tracker, CooldownTracker)

    def test_cooldown_tracker_functional(self) -> None:
        bar = SkillBar(slots=())
        bar.cooldown_tracker.start_cooldown("fireball", 3)
        assert bar.cooldown_tracker.is_ready("fireball") is False

    def test_cooldown_tick_works(self) -> None:
        bar = SkillBar(slots=())
        bar.cooldown_tracker.start_cooldown("fireball", 1)
        bar.cooldown_tracker.tick()
        assert bar.cooldown_tracker.is_ready("fireball") is True


class TestSkillBarReadySkills:
    def test_all_ready_by_default(self) -> None:
        sk = _make_skill("fireball", 5)
        slot = SpellSlot(max_cost=8, skills=(sk,))
        bar = SkillBar(slots=(slot,))
        assert len(bar.ready_skills) == 1

    def test_excludes_on_cooldown(self) -> None:
        sk = _make_skill("fireball", 5)
        slot = SpellSlot(max_cost=8, skills=(sk,))
        bar = SkillBar(slots=(slot,))
        bar.cooldown_tracker.start_cooldown("fireball", 3)
        assert len(bar.ready_skills) == 0

    def test_mixed_ready_and_cooldown(self) -> None:
        sk1 = _make_skill("fireball", 5)
        sk2 = _make_skill("heal", 3)
        slot = SpellSlot(max_cost=10, skills=(sk1, sk2))
        bar = SkillBar(slots=(slot,))
        bar.cooldown_tracker.start_cooldown("fireball", 2)
        ready_ids = [s.skill_id for s in bar.ready_skills]
        assert "heal" in ready_ids
        assert "fireball" not in ready_ids
