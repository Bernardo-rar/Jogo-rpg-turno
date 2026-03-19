"""Testes para PlayerAction dataclass."""

import pytest

from src.core.combat.player_action import PlayerAction, PlayerActionType


class TestPlayerActionType:
    def test_has_six_types(self):
        assert len(list(PlayerActionType)) == 6

    def test_basic_attack_exists(self):
        assert PlayerActionType.BASIC_ATTACK is not None

    def test_end_turn_exists(self):
        assert PlayerActionType.END_TURN is not None


class TestPlayerAction:
    def test_basic_attack_creation(self):
        action = PlayerAction(
            action_type=PlayerActionType.BASIC_ATTACK,
            target_name="Goblin A",
        )
        assert action.action_type == PlayerActionType.BASIC_ATTACK
        assert action.target_name == "Goblin A"

    def test_skill_creation(self):
        action = PlayerAction(
            action_type=PlayerActionType.SKILL,
            target_name="Goblin B",
            skill_id="fireball",
        )
        assert action.skill_id == "fireball"

    def test_item_creation(self):
        action = PlayerAction(
            action_type=PlayerActionType.ITEM,
            target_name="Hero",
            consumable_id="health_potion",
        )
        assert action.consumable_id == "health_potion"

    def test_move_creation(self):
        action = PlayerAction(action_type=PlayerActionType.MOVE)
        assert action.action_type == PlayerActionType.MOVE
        assert action.target_name == ""

    def test_defend_creation(self):
        action = PlayerAction(action_type=PlayerActionType.DEFEND)
        assert action.action_type == PlayerActionType.DEFEND

    def test_end_turn_creation(self):
        action = PlayerAction(action_type=PlayerActionType.END_TURN)
        assert action.action_type == PlayerActionType.END_TURN

    def test_is_frozen(self):
        action = PlayerAction(action_type=PlayerActionType.BASIC_ATTACK)
        with pytest.raises(AttributeError):
            action.action_type = PlayerActionType.SKILL  # type: ignore[misc]

    def test_defaults_are_empty_strings(self):
        action = PlayerAction(action_type=PlayerActionType.END_TURN)
        assert action.target_name == ""
        assert action.skill_id == ""
        assert action.consumable_id == ""
