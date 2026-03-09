"""Testes para skill_loader."""

from __future__ import annotations

from src.core.combat.action_economy import ActionType
from src.core.elements.element_type import ElementType
from src.core.skills.skill_loader import load_skills
from src.core.skills.target_type import TargetType


class TestLoadSkills:
    def test_loads_all_skills(self) -> None:
        skills = load_skills()
        assert len(skills) >= 10

    def test_returns_dict(self) -> None:
        skills = load_skills()
        assert isinstance(skills, dict)
        assert "fireball" in skills

    def test_fireball_fields(self) -> None:
        skills = load_skills()
        fb = skills["fireball"]
        assert fb.skill_id == "fireball"
        assert fb.name == "Fireball"
        assert fb.mana_cost == 25
        assert fb.action_type == ActionType.ACTION
        assert fb.target_type == TargetType.SINGLE_ENEMY
        assert fb.slot_cost == 5

    def test_fireball_has_fire_element(self) -> None:
        skills = load_skills()
        fb = skills["fireball"]
        assert fb.effects[0].element == ElementType.FIRE

    def test_revive_has_cooldown(self) -> None:
        skills = load_skills()
        rev = skills["revive"]
        assert rev.cooldown_turns == 8
        assert rev.required_level == 5

    def test_poison_strike_has_two_effects(self) -> None:
        skills = load_skills()
        ps = skills["poison_strike"]
        assert len(ps.effects) == 2
