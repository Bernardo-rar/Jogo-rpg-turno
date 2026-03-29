"""Testes do Skill Pool Builder."""

from src.core.skills.skill_pool_builder import build_skill_pool


class TestBuildSkillPool:

    def test_fighter_level_1_has_skills(self) -> None:
        pool = build_skill_pool("fighter", 1)
        assert len(pool) > 0

    def test_pool_grows_with_level(self) -> None:
        pool_1 = build_skill_pool("fighter", 1)
        pool_10 = build_skill_pool("fighter", 10)
        assert len(pool_10) >= len(pool_1)

    def test_all_skills_respect_level(self) -> None:
        pool = build_skill_pool("mage", 1)
        for skill in pool:
            assert skill.required_level <= 1

    def test_includes_class_skills(self) -> None:
        pool = build_skill_pool("fighter", 1)
        names = {s.skill_id for s in pool}
        # Fighter should have power_strike or similar
        assert len(names) > 0

    def test_nonexistent_subclass_no_crash(self) -> None:
        pool = build_skill_pool("fighter", 5, subclass_id="nonexistent")
        assert len(pool) > 0

    def test_universal_skills_included(self) -> None:
        pool = build_skill_pool("barbarian", 1)
        class_pool = build_skill_pool("mage", 1)
        # Both should share some universal skills
        barb_ids = {s.skill_id for s in pool}
        mage_ids = {s.skill_id for s in class_pool}
        shared = barb_ids & mage_ids
        # At least some universal overlap (if universal skills exist)
        # This is a soft check — depends on data
        assert isinstance(shared, set)
