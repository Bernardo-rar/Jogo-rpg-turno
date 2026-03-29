"""Testes do LoadoutManager."""

from src.core.combat.action_economy import ActionType
from src.core.skills.loadout_manager import LoadoutManager
from src.core.skills.skill import Skill
from src.core.skills.skill_effect_type import SkillEffectType
from src.core.skills.target_type import TargetType


def _skill(sid: str, cost: int = 3, action: ActionType = ActionType.ACTION) -> Skill:
    return Skill(
        skill_id=sid, name=sid.title(), mana_cost=5,
        action_type=action, target_type=TargetType.SINGLE_ENEMY,
        effects=(), slot_cost=cost,
    )


class TestAddSkill:

    def test_add_skill_to_slot(self) -> None:
        mgr = LoadoutManager(slot_count=3, budget=10)
        sk = _skill("fire_bolt", cost=3)
        assert mgr.add_skill(0, sk) is True
        assert len(mgr.slots[0].skills) == 1

    def test_budget_overflow_rejected(self) -> None:
        mgr = LoadoutManager(slot_count=1, budget=5)
        sk = _skill("big_spell", cost=6)
        assert mgr.add_skill(0, sk) is False

    def test_duplicate_rejected(self) -> None:
        mgr = LoadoutManager(slot_count=2, budget=10)
        sk = _skill("fire_bolt", cost=3)
        mgr.add_skill(0, sk)
        assert mgr.add_skill(1, sk) is False

    def test_invalid_slot_index(self) -> None:
        mgr = LoadoutManager(slot_count=2, budget=10)
        assert mgr.add_skill(5, _skill("x")) is False


class TestRemoveSkill:

    def test_remove_skill(self) -> None:
        mgr = LoadoutManager(slot_count=1, budget=10)
        mgr.add_skill(0, _skill("fire_bolt"))
        assert mgr.remove_skill(0, "fire_bolt") is True
        assert len(mgr.slots[0].skills) == 0

    def test_remove_allows_readd(self) -> None:
        mgr = LoadoutManager(slot_count=2, budget=10)
        sk = _skill("fire_bolt")
        mgr.add_skill(0, sk)
        mgr.remove_skill(0, "fire_bolt")
        assert mgr.add_skill(1, sk) is True


class TestReaction:

    def test_set_reaction(self) -> None:
        mgr = LoadoutManager(slot_count=1, budget=10)
        sk = _skill("parry", action=ActionType.REACTION)
        assert mgr.set_reaction(sk) is True
        assert mgr.reaction is sk

    def test_non_reaction_rejected(self) -> None:
        mgr = LoadoutManager(slot_count=1, budget=10)
        sk = _skill("fire", action=ActionType.ACTION)
        assert mgr.set_reaction(sk) is False


class TestPassive:

    def test_add_passive(self) -> None:
        mgr = LoadoutManager(slot_count=1, budget=10)
        sk = _skill("iron_will", action=ActionType.PASSIVE)
        assert mgr.add_passive(sk) is True
        assert len(mgr.passives) == 1

    def test_passive_limit(self) -> None:
        mgr = LoadoutManager(slot_count=1, budget=10)
        mgr.add_passive(_skill("p1", action=ActionType.PASSIVE))
        mgr.add_passive(_skill("p2", action=ActionType.PASSIVE))
        assert mgr.add_passive(_skill("p3", action=ActionType.PASSIVE)) is False

    def test_non_passive_rejected(self) -> None:
        mgr = LoadoutManager(slot_count=1, budget=10)
        sk = _skill("fire", action=ActionType.ACTION)
        assert mgr.add_passive(sk) is False


class TestBuildSkillBar:

    def test_builds_skill_bar(self) -> None:
        mgr = LoadoutManager(slot_count=2, budget=10)
        mgr.add_skill(0, _skill("s1", cost=3))
        mgr.add_skill(0, _skill("s2", cost=3))
        mgr.add_skill(1, _skill("s3", cost=4))
        bar = mgr.build_skill_bar()
        assert len(bar.all_skills) == 3

    def test_includes_reaction_and_passives(self) -> None:
        mgr = LoadoutManager(slot_count=1, budget=10)
        mgr.add_skill(0, _skill("s1", cost=3))
        mgr.set_reaction(_skill("r1", action=ActionType.REACTION))
        mgr.add_passive(_skill("p1", action=ActionType.PASSIVE))
        bar = mgr.build_skill_bar()
        assert len(bar.all_skills) == 3
