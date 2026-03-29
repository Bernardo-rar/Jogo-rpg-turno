"""Testes do auto-fill de loadout."""

from src.core.combat.action_economy import ActionType
from src.core.skills.auto_fill import auto_fill_loadout
from src.core.skills.loadout_manager import LoadoutManager
from src.core.skills.skill import Skill
from src.core.skills.target_type import TargetType


def _skill(sid: str, cost: int = 3, action: ActionType = ActionType.ACTION) -> Skill:
    return Skill(
        skill_id=sid, name=sid.title(), mana_cost=5,
        action_type=action, target_type=TargetType.SINGLE_ENEMY,
        effects=(), slot_cost=cost,
    )


class TestAutoFill:

    def test_fills_main_slots(self) -> None:
        pool = [_skill("s1", 3), _skill("s2", 4), _skill("s3", 5)]
        mgr = LoadoutManager(slot_count=2, budget=10)
        auto_fill_loadout(pool, mgr)
        total = sum(len(s.skills) for s in mgr.slots)
        assert total == 3

    def test_fills_reaction(self) -> None:
        pool = [
            _skill("s1", 3),
            _skill("parry", 3, ActionType.REACTION),
        ]
        mgr = LoadoutManager(slot_count=1, budget=10)
        auto_fill_loadout(pool, mgr)
        assert mgr.reaction is not None
        assert mgr.reaction.skill_id == "parry"

    def test_fills_passives(self) -> None:
        pool = [
            _skill("s1", 3),
            _skill("p1", 2, ActionType.PASSIVE),
            _skill("p2", 2, ActionType.PASSIVE),
        ]
        mgr = LoadoutManager(slot_count=1, budget=10)
        auto_fill_loadout(pool, mgr)
        assert len(mgr.passives) == 2

    def test_higher_cost_skills_prioritized(self) -> None:
        pool = [_skill("cheap", 2), _skill("expensive", 8)]
        mgr = LoadoutManager(slot_count=1, budget=10)
        auto_fill_loadout(pool, mgr)
        skills = mgr.slots[0].skills
        assert skills[0].skill_id == "expensive"

    def test_respects_budget(self) -> None:
        pool = [_skill(f"s{i}", 6) for i in range(5)]
        mgr = LoadoutManager(slot_count=2, budget=6)
        auto_fill_loadout(pool, mgr)
        for slot in mgr.slots:
            total = sum(s.slot_cost for s in slot.skills)
            assert total <= 6

    def test_no_duplicates(self) -> None:
        pool = [_skill("s1", 3), _skill("s2", 3)]
        mgr = LoadoutManager(slot_count=3, budget=10)
        auto_fill_loadout(pool, mgr)
        all_ids = []
        for slot in mgr.slots:
            all_ids.extend(s.skill_id for s in slot.skills)
        assert len(all_ids) == len(set(all_ids))
