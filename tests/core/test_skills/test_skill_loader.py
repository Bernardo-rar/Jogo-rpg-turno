"""Testes para skill_loader."""

from __future__ import annotations

import pytest

from src.core.classes.class_id import ClassId
from src.core.combat.action_economy import ActionType
from src.core.elements.element_type import ElementType
from src.core.skills.skill_loader import load_class_skills, load_skills
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
        assert fb.mana_cost == 13
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


class TestLoadClassSkills:
    @pytest.mark.parametrize("class_id", [c.value for c in ClassId])
    def test_loads_six_skills_per_class(self, class_id: str) -> None:
        skills = load_class_skills(class_id)
        assert len(skills) == 6

    @pytest.mark.parametrize("class_id", [c.value for c in ClassId])
    def test_all_skills_have_class_id(self, class_id: str) -> None:
        skills = load_class_skills(class_id)
        for skill in skills.values():
            assert skill.class_id == class_id

    def test_fighter_power_strike_has_resource_cost(self) -> None:
        skills = load_class_skills("fighter")
        ps = skills["power_strike"]
        assert len(ps.resource_costs) == 1
        assert ps.resource_costs[0].resource_type == "action_points"
        assert ps.resource_costs[0].amount == 2

    def test_fighter_parry_is_reaction(self) -> None:
        skills = load_class_skills("fighter")
        parry = skills["parry"]
        assert parry.action_type == ActionType.REACTION
        assert parry.reaction_trigger == "on_damage_received"
        assert parry.reaction_mode == "passive"

    def test_mage_fire_bolt_has_fire_element(self) -> None:
        skills = load_class_skills("mage")
        fb = skills["fire_bolt"]
        assert fb.effects[0].element == ElementType.FIRE
