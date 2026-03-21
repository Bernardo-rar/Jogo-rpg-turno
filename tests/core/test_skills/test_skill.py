"""Testes para Skill frozen dataclass."""

from __future__ import annotations

import pytest

from src.core.combat.action_economy import ActionType
from src.core.effects.modifiable_stat import ModifiableStat
from src.core.elements.element_type import ElementType
from src.core.skills.resource_cost import ResourceCost
from src.core.skills.skill import Skill
from src.core.skills.skill_effect import SkillEffect
from src.core.skills.skill_effect_type import SkillEffectType
from src.core.skills.target_type import TargetType


def _damage_effect() -> SkillEffect:
    return SkillEffect(
        effect_type=SkillEffectType.DAMAGE, base_power=30,
        element=ElementType.FIRE,
    )


def _heal_effect() -> SkillEffect:
    return SkillEffect(effect_type=SkillEffectType.HEAL, base_power=20)


class TestSkillCreation:
    def test_create_basic(self) -> None:
        sk = Skill(
            skill_id="fireball", name="Fireball", mana_cost=25,
            action_type=ActionType.ACTION, target_type=TargetType.SINGLE_ENEMY,
            effects=(_damage_effect(),), slot_cost=5,
        )
        assert sk.skill_id == "fireball"
        assert sk.name == "Fireball"
        assert sk.mana_cost == 25
        assert sk.slot_cost == 5

    def test_action_type(self) -> None:
        sk = Skill(
            skill_id="heal", name="Heal", mana_cost=15,
            action_type=ActionType.BONUS_ACTION,
            target_type=TargetType.SINGLE_ALLY,
            effects=(_heal_effect(),), slot_cost=3,
        )
        assert sk.action_type == ActionType.BONUS_ACTION

    def test_effects_tuple(self) -> None:
        e1 = _damage_effect()
        e2 = _heal_effect()
        sk = Skill(
            skill_id="combo", name="Combo", mana_cost=30,
            action_type=ActionType.ACTION, target_type=TargetType.SELF,
            effects=(e1, e2), slot_cost=8,
        )
        assert len(sk.effects) == 2

    def test_defaults(self) -> None:
        sk = Skill(
            skill_id="x", name="X", mana_cost=10,
            action_type=ActionType.ACTION, target_type=TargetType.SELF,
            effects=(), slot_cost=1,
        )
        assert sk.cooldown_turns == 0
        assert sk.stamina_cost == 0
        assert sk.required_level == 1
        assert sk.description == ""
        assert sk.class_id == ""
        assert sk.resource_costs == ()
        assert sk.reaction_trigger == ""
        assert sk.reaction_mode == ""

    def test_class_id_and_resource_costs(self) -> None:
        costs = (ResourceCost("action_points", 2),)
        sk = Skill(
            skill_id="power_strike", name="Power Strike", mana_cost=5,
            action_type=ActionType.ACTION, target_type=TargetType.SINGLE_ENEMY,
            effects=(_damage_effect(),), slot_cost=4,
            class_id="fighter", resource_costs=costs,
        )
        assert sk.class_id == "fighter"
        assert len(sk.resource_costs) == 1
        assert sk.resource_costs[0].resource_type == "action_points"
        assert sk.resource_costs[0].amount == 2

    def test_reaction_fields(self) -> None:
        sk = Skill(
            skill_id="parry", name="Parry", mana_cost=0,
            action_type=ActionType.REACTION, target_type=TargetType.SELF,
            effects=(), slot_cost=3,
            class_id="fighter",
            resource_costs=(ResourceCost("action_points", 1),),
            reaction_trigger="on_damage_received",
            reaction_mode="passive",
        )
        assert sk.action_type == ActionType.REACTION
        assert sk.reaction_trigger == "on_damage_received"
        assert sk.reaction_mode == "passive"

    def test_is_frozen(self) -> None:
        sk = Skill(
            skill_id="x", name="X", mana_cost=10,
            action_type=ActionType.ACTION, target_type=TargetType.SELF,
            effects=(), slot_cost=1,
        )
        with pytest.raises(AttributeError):
            sk.mana_cost = 99  # type: ignore[misc]

    def test_cooldown_and_stamina(self) -> None:
        sk = Skill(
            skill_id="revive", name="Revive", mana_cost=50,
            action_type=ActionType.ACTION,
            target_type=TargetType.SINGLE_ALLY,
            effects=(_heal_effect(),), slot_cost=10,
            cooldown_turns=5, stamina_cost=20,
        )
        assert sk.cooldown_turns == 5
        assert sk.stamina_cost == 20

    def test_required_level(self) -> None:
        sk = Skill(
            skill_id="meteor", name="Meteor", mana_cost=80,
            action_type=ActionType.ACTION,
            target_type=TargetType.ALL_ENEMIES,
            effects=(_damage_effect(),), slot_cost=15,
            required_level=8,
        )
        assert sk.required_level == 8


class TestSkillFromDict:
    def test_from_dict_basic(self) -> None:
        data: dict[str, object] = {
            "name": "Fireball",
            "mana_cost": 25,
            "action_type": "ACTION",
            "target_type": "SINGLE_ENEMY",
            "effects": [
                {"effect_type": "DAMAGE", "base_power": 30, "element": "FIRE"},
            ],
            "slot_cost": 5,
        }
        sk = Skill.from_dict("fireball", data)
        assert sk.skill_id == "fireball"
        assert sk.name == "Fireball"
        assert sk.mana_cost == 25
        assert sk.action_type == ActionType.ACTION
        assert sk.target_type == TargetType.SINGLE_ENEMY
        assert len(sk.effects) == 1
        assert sk.effects[0].element == ElementType.FIRE

    def test_from_dict_with_cooldown(self) -> None:
        data: dict[str, object] = {
            "name": "Defense Buff",
            "mana_cost": 20,
            "action_type": "BONUS_ACTION",
            "target_type": "SINGLE_ALLY",
            "effects": [
                {
                    "effect_type": "BUFF", "base_power": 10,
                    "stat": "PHYSICAL_DEFENSE", "duration": 3,
                },
            ],
            "slot_cost": 3,
            "cooldown_turns": 2,
        }
        sk = Skill.from_dict("defense_buff", data)
        assert sk.cooldown_turns == 2
        assert sk.effects[0].stat == ModifiableStat.PHYSICAL_DEFENSE

    def test_from_dict_defaults(self) -> None:
        data: dict[str, object] = {
            "name": "Zap",
            "mana_cost": 5,
            "action_type": "ACTION",
            "target_type": "SINGLE_ENEMY",
            "effects": [{"effect_type": "DAMAGE", "base_power": 10}],
            "slot_cost": 1,
        }
        sk = Skill.from_dict("zap", data)
        assert sk.cooldown_turns == 0
        assert sk.stamina_cost == 0
        assert sk.required_level == 1
        assert sk.description == ""

    def test_from_dict_multi_effect(self) -> None:
        data: dict[str, object] = {
            "name": "Fire Strike",
            "mana_cost": 30,
            "action_type": "ACTION",
            "target_type": "SINGLE_ENEMY",
            "effects": [
                {"effect_type": "DAMAGE", "base_power": 20},
                {"effect_type": "APPLY_AILMENT", "ailment_id": "burn", "duration": 3},
            ],
            "slot_cost": 7,
        }
        sk = Skill.from_dict("fire_strike", data)
        assert len(sk.effects) == 2
        assert sk.effects[1].ailment_id == "burn"

    def test_from_dict_all_fields(self) -> None:
        data: dict[str, object] = {
            "name": "Revive",
            "mana_cost": 50,
            "action_type": "ACTION",
            "target_type": "SINGLE_ALLY",
            "effects": [{"effect_type": "HEAL", "base_power": 100}],
            "slot_cost": 10,
            "cooldown_turns": 5,
            "stamina_cost": 20,
            "required_level": 6,
            "description": "Revive um aliado caido",
        }
        sk = Skill.from_dict("revive", data)
        assert sk.stamina_cost == 20
        assert sk.required_level == 6
        assert sk.description == "Revive um aliado caido"

    def test_from_dict_new_fields_default_empty(self) -> None:
        data: dict[str, object] = {
            "name": "Zap",
            "mana_cost": 5,
            "action_type": "ACTION",
            "target_type": "SINGLE_ENEMY",
            "effects": [{"effect_type": "DAMAGE", "base_power": 10}],
            "slot_cost": 1,
        }
        sk = Skill.from_dict("zap", data)
        assert sk.class_id == ""
        assert sk.resource_costs == ()
        assert sk.reaction_trigger == ""
        assert sk.reaction_mode == ""

    def test_from_dict_with_class_id_and_resource_costs(self) -> None:
        data: dict[str, object] = {
            "name": "Power Strike",
            "mana_cost": 5,
            "action_type": "ACTION",
            "target_type": "SINGLE_ENEMY",
            "effects": [{"effect_type": "DAMAGE", "base_power": 40}],
            "slot_cost": 4,
            "class_id": "fighter",
            "resource_costs": [
                {"resource_type": "action_points", "amount": 2},
            ],
        }
        sk = Skill.from_dict("power_strike", data)
        assert sk.class_id == "fighter"
        assert len(sk.resource_costs) == 1
        assert sk.resource_costs[0].resource_type == "action_points"
        assert sk.resource_costs[0].amount == 2

    def test_from_dict_with_reaction_fields(self) -> None:
        data: dict[str, object] = {
            "name": "Parry",
            "mana_cost": 0,
            "action_type": "REACTION",
            "target_type": "SELF",
            "effects": [
                {"effect_type": "BUFF", "base_power": 15,
                 "stat": "PHYSICAL_DEFENSE", "duration": 1},
            ],
            "slot_cost": 3,
            "class_id": "fighter",
            "resource_costs": [
                {"resource_type": "action_points", "amount": 1},
            ],
            "reaction_trigger": "on_damage_received",
            "reaction_mode": "passive",
        }
        sk = Skill.from_dict("parry", data)
        assert sk.reaction_trigger == "on_damage_received"
        assert sk.reaction_mode == "passive"
        assert sk.resource_costs[0].amount == 1
