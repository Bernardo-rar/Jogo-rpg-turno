"""Tests for reaction system enums and data types."""

from __future__ import annotations

import pytest

from src.core.combat.reaction_system import (
    PreparedReaction,
    ReactionMode,
    ReactionTrigger,
)
from src.core.combat.action_economy import ActionType
from src.core.skills.resource_cost import ResourceCost
from src.core.skills.skill import Skill
from src.core.skills.skill_effect import SkillEffect
from src.core.skills.skill_effect_type import SkillEffectType
from src.core.skills.target_type import TargetType


def _parry_skill() -> Skill:
    return Skill(
        skill_id="parry", name="Parry", mana_cost=0,
        action_type=ActionType.REACTION, target_type=TargetType.SELF,
        effects=(
            SkillEffect(effect_type=SkillEffectType.BUFF, base_power=15,
                        stat=None, duration=1),
        ),
        slot_cost=3, class_id="fighter",
        resource_costs=(ResourceCost("action_points", 1),),
        reaction_trigger="on_damage_received",
        reaction_mode="passive",
    )


class TestReactionTrigger:
    def test_on_damage_received_exists(self) -> None:
        assert ReactionTrigger.ON_DAMAGE_RECEIVED.value == "on_damage_received"

    def test_on_ally_damaged_exists(self) -> None:
        assert ReactionTrigger.ON_ALLY_DAMAGED.value == "on_ally_damaged"

    def test_on_enemy_attack_exists(self) -> None:
        assert ReactionTrigger.ON_ENEMY_ATTACK.value == "on_enemy_attack"

    def test_on_enemy_cast_exists(self) -> None:
        assert ReactionTrigger.ON_ENEMY_CAST.value == "on_enemy_cast"

    def test_from_string(self) -> None:
        trigger = ReactionTrigger("on_damage_received")
        assert trigger == ReactionTrigger.ON_DAMAGE_RECEIVED


class TestReactionMode:
    def test_passive_exists(self) -> None:
        assert ReactionMode.PASSIVE.value == "passive"

    def test_prepared_exists(self) -> None:
        assert ReactionMode.PREPARED.value == "prepared"

    def test_toggle_exists(self) -> None:
        assert ReactionMode.TOGGLE.value == "toggle"


class TestPreparedReaction:
    def test_create(self) -> None:
        skill = _parry_skill()
        reaction = PreparedReaction(
            skill=skill,
            combatant_name="Fighter1",
            trigger=ReactionTrigger.ON_DAMAGE_RECEIVED,
        )
        assert reaction.skill == skill
        assert reaction.combatant_name == "Fighter1"
        assert reaction.trigger == ReactionTrigger.ON_DAMAGE_RECEIVED

    def test_is_frozen(self) -> None:
        skill = _parry_skill()
        reaction = PreparedReaction(
            skill=skill,
            combatant_name="Fighter1",
            trigger=ReactionTrigger.ON_DAMAGE_RECEIVED,
        )
        with pytest.raises(AttributeError):
            reaction.combatant_name = "X"  # type: ignore[misc]
