"""Testes para ActionResolver — ataque basico, mover, defender, end turn."""

import pytest

from src.core.combat.action_economy import ActionEconomy, ActionType
from src.core.combat.action_resolver import resolve_player_action
from src.core.combat.combat_engine import EventType, TurnContext
from src.core.combat.player_action import PlayerAction, PlayerActionType
from src.core.characters.position import Position

from tests.core.test_combat.conftest import _build_char


def _make_context(
    combatant_name: str = "Hero",
    enemy_name: str = "Goblin",
    *,
    economy: ActionEconomy | None = None,
) -> TurnContext:
    hero = _build_char(combatant_name)
    goblin = _build_char(enemy_name)
    return TurnContext(
        combatant=hero,
        allies=[hero],
        enemies=[goblin],
        action_economy=economy or ActionEconomy(),
        round_number=1,
    )


class TestResolveBasicAttack:
    def test_deals_damage_to_target(self):
        ctx = _make_context()
        target = ctx.enemies[0]
        hp_before = target.current_hp
        action = PlayerAction(
            action_type=PlayerActionType.BASIC_ATTACK,
            target_name="Goblin",
        )
        events = resolve_player_action(action, ctx)
        assert len(events) == 1
        assert target.current_hp < hp_before

    def test_event_has_correct_actor_and_target(self):
        ctx = _make_context()
        action = PlayerAction(
            action_type=PlayerActionType.BASIC_ATTACK,
            target_name="Goblin",
        )
        events = resolve_player_action(action, ctx)
        assert events[0].actor_name == "Hero"
        assert events[0].target_name == "Goblin"

    def test_event_has_damage_result(self):
        ctx = _make_context()
        action = PlayerAction(
            action_type=PlayerActionType.BASIC_ATTACK,
            target_name="Goblin",
        )
        events = resolve_player_action(action, ctx)
        assert events[0].damage is not None
        assert events[0].damage.final_damage > 0

    def test_consumes_action(self):
        economy = ActionEconomy()
        ctx = _make_context(economy=economy)
        action = PlayerAction(
            action_type=PlayerActionType.BASIC_ATTACK,
            target_name="Goblin",
        )
        resolve_player_action(action, ctx)
        assert not economy.is_available(ActionType.ACTION)

    def test_no_action_available_returns_empty(self):
        economy = ActionEconomy()
        economy.use(ActionType.ACTION)
        ctx = _make_context(economy=economy)
        action = PlayerAction(
            action_type=PlayerActionType.BASIC_ATTACK,
            target_name="Goblin",
        )
        events = resolve_player_action(action, ctx)
        assert events == []

    def test_invalid_target_returns_empty(self):
        ctx = _make_context()
        action = PlayerAction(
            action_type=PlayerActionType.BASIC_ATTACK,
            target_name="NonExistent",
        )
        events = resolve_player_action(action, ctx)
        assert events == []

    def test_dead_target_returns_empty(self):
        ctx = _make_context()
        target = ctx.enemies[0]
        target.take_damage(target.current_hp)
        action = PlayerAction(
            action_type=PlayerActionType.BASIC_ATTACK,
            target_name="Goblin",
        )
        events = resolve_player_action(action, ctx)
        assert events == []


class TestResolveMove:
    def test_changes_position_front_to_back(self):
        ctx = _make_context()
        assert ctx.combatant.position == Position.FRONT
        action = PlayerAction(action_type=PlayerActionType.MOVE)
        resolve_player_action(action, ctx)
        assert ctx.combatant.position == Position.BACK

    def test_changes_position_back_to_front(self):
        ctx = _make_context()
        ctx.combatant.change_position(Position.BACK)
        action = PlayerAction(action_type=PlayerActionType.MOVE)
        resolve_player_action(action, ctx)
        assert ctx.combatant.position == Position.FRONT

    def test_consumes_bonus_action(self):
        economy = ActionEconomy()
        ctx = _make_context(economy=economy)
        action = PlayerAction(action_type=PlayerActionType.MOVE)
        resolve_player_action(action, ctx)
        assert not economy.is_available(ActionType.BONUS_ACTION)

    def test_returns_event(self):
        ctx = _make_context()
        action = PlayerAction(action_type=PlayerActionType.MOVE)
        events = resolve_player_action(action, ctx)
        assert len(events) == 1
        assert events[0].event_type == EventType.SKILL_USE

    def test_no_bonus_action_returns_empty(self):
        economy = ActionEconomy()
        economy.use(ActionType.BONUS_ACTION)
        ctx = _make_context(economy=economy)
        action = PlayerAction(action_type=PlayerActionType.MOVE)
        events = resolve_player_action(action, ctx)
        assert events == []


class TestResolveDefend:
    def test_applies_defense_buff(self):
        ctx = _make_context()
        phys_def_before = ctx.combatant.physical_defense
        action = PlayerAction(action_type=PlayerActionType.DEFEND)
        resolve_player_action(action, ctx)
        assert ctx.combatant.physical_defense > phys_def_before

    def test_consumes_reaction(self):
        economy = ActionEconomy()
        ctx = _make_context(economy=economy)
        action = PlayerAction(action_type=PlayerActionType.DEFEND)
        resolve_player_action(action, ctx)
        assert not economy.is_available(ActionType.REACTION)

    def test_returns_event(self):
        ctx = _make_context()
        action = PlayerAction(action_type=PlayerActionType.DEFEND)
        events = resolve_player_action(action, ctx)
        assert len(events) == 1
        assert events[0].event_type == EventType.BUFF

    def test_no_reaction_returns_empty(self):
        economy = ActionEconomy()
        economy.use(ActionType.REACTION)
        ctx = _make_context(economy=economy)
        action = PlayerAction(action_type=PlayerActionType.DEFEND)
        events = resolve_player_action(action, ctx)
        assert events == []


class TestResolveEndTurn:
    def test_returns_empty_events(self):
        ctx = _make_context()
        action = PlayerAction(action_type=PlayerActionType.END_TURN)
        events = resolve_player_action(action, ctx)
        assert events == []

    def test_does_not_consume_any_action(self):
        economy = ActionEconomy()
        ctx = _make_context(economy=economy)
        action = PlayerAction(action_type=PlayerActionType.END_TURN)
        resolve_player_action(action, ctx)
        assert economy.is_available(ActionType.ACTION)
        assert economy.is_available(ActionType.BONUS_ACTION)
        assert economy.is_available(ActionType.REACTION)
