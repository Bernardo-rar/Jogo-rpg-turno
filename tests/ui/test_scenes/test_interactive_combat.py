"""Testes para InteractiveCombatScene — state machine de combate interativo."""

from __future__ import annotations

from src.core.combat.action_economy import ActionEconomy
from src.core.combat.combat_engine import (
    CombatEngine,
    CombatEvent,
    CombatResult,
    TurnContext,
    TurnHandler,
)
from src.core.combat.player_action import PlayerAction, PlayerActionType
from src.ui.scenes.interactive_combat import (
    InteractiveCombatScene,
    TurnPhase,
)

from tests.core.test_combat.conftest import _build_char


class _StubHandler:
    """Handler que registra chamadas e retorna eventos vazios."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    def execute_turn(self, context: TurnContext) -> list[CombatEvent]:
        self.calls.append(context.combatant.name)
        return []


class _KillHandler:
    """Handler que mata todos os inimigos no primeiro turno."""

    def execute_turn(self, context: TurnContext) -> list[CombatEvent]:
        for enemy in context.enemies:
            if enemy.is_alive:
                enemy.take_damage(enemy.max_hp + 100)
        return []


def _make_scene(
    party_names: list[str] | None = None,
    enemy_names: list[str] | None = None,
    handler: TurnHandler | None = None,
) -> tuple[InteractiveCombatScene, CombatEngine]:
    party_names = party_names or ["Hero"]
    enemy_names = enemy_names or ["Goblin"]
    party = [_build_char(n) for n in party_names]
    enemies = [_build_char(n) for n in enemy_names]
    handler = handler or _StubHandler()
    engine = CombatEngine(party, enemies, handler)
    party_set = frozenset(party_names)
    scene = InteractiveCombatScene(
        engine=engine,
        party_names=party_set,
        ai_handler=handler,
    )
    return scene, engine


class TestTurnPhaseTransitions:
    def test_starts_in_starting_round(self) -> None:
        scene, _ = _make_scene()
        assert scene.phase == TurnPhase.STARTING_ROUND

    def test_first_update_starts_round(self) -> None:
        scene, _ = _make_scene()
        scene.update(16)
        assert scene.phase != TurnPhase.STARTING_ROUND

    def test_party_turn_goes_to_waiting_input(self) -> None:
        scene, _ = _make_scene()
        scene.update(16)
        assert scene.phase == TurnPhase.WAITING_INPUT

    def test_enemy_first_goes_to_ai_turn(self) -> None:
        scene, _ = _make_scene(
            party_names=["SlowHero"],
            enemy_names=["FastGoblin"],
        )
        scene.update(16)
        if scene.active_combatant not in ("SlowHero",):
            assert scene.phase == TurnPhase.AI_TURN


class TestPlayerInput:
    def test_select_end_turn_produces_action(self) -> None:
        scene, _ = _make_scene()
        scene.update(16)
        assert scene.phase == TurnPhase.WAITING_INPUT
        action = PlayerAction(action_type=PlayerActionType.END_TURN)
        scene.submit_player_action(action)
        assert scene.phase != TurnPhase.WAITING_INPUT

    def test_submit_action_ignored_outside_waiting(self) -> None:
        scene, _ = _make_scene()
        action = PlayerAction(action_type=PlayerActionType.END_TURN)
        scene.submit_player_action(action)
        assert scene.phase == TurnPhase.STARTING_ROUND

    def test_end_turn_advances_round(self) -> None:
        scene, engine = _make_scene()
        scene.update(16)
        round_before = engine.round_number
        action = PlayerAction(action_type=PlayerActionType.END_TURN)
        scene.submit_player_action(action)
        scene.update(16)
        assert engine.round_number > round_before


class TestAITurn:
    def test_ai_handler_called_for_enemies(self) -> None:
        handler = _StubHandler()
        scene, _ = _make_scene(handler=handler)
        for _ in range(50):
            scene.update(16)
            if scene.phase == TurnPhase.WAITING_INPUT:
                scene.submit_player_action(
                    PlayerAction(action_type=PlayerActionType.END_TURN),
                )
        assert "Goblin" in handler.calls


class TestCombatEnd:
    def test_victory_transitions_to_combat_over(self) -> None:
        handler = _KillHandler()
        scene, engine = _make_scene(handler=handler)
        for _ in range(100):
            scene.update(16)
            if scene.phase == TurnPhase.WAITING_INPUT:
                scene.submit_player_action(
                    PlayerAction(action_type=PlayerActionType.END_TURN),
                )
            if scene.phase == TurnPhase.COMBAT_OVER:
                break
        assert scene.phase == TurnPhase.COMBAT_OVER

    def test_result_available_after_combat_over(self) -> None:
        handler = _KillHandler()
        scene, engine = _make_scene(handler=handler)
        for _ in range(100):
            scene.update(16)
            if scene.phase == TurnPhase.WAITING_INPUT:
                scene.submit_player_action(
                    PlayerAction(action_type=PlayerActionType.END_TURN),
                )
            if scene.phase == TurnPhase.COMBAT_OVER:
                break
        assert engine.result is not None


class TestActiveState:
    def test_active_combatant_set_during_turn(self) -> None:
        scene, _ = _make_scene()
        scene.update(16)
        assert scene.active_combatant is not None

    def test_context_available_during_waiting(self) -> None:
        scene, _ = _make_scene()
        scene.update(16)
        assert scene.phase == TurnPhase.WAITING_INPUT
        assert scene.current_context is not None

    def test_economy_available_during_waiting(self) -> None:
        scene, _ = _make_scene()
        scene.update(16)
        assert scene.phase == TurnPhase.WAITING_INPUT
        ctx = scene.current_context
        assert isinstance(ctx.action_economy, ActionEconomy)


class TestEndTurnShortcut:
    def test_shortcut_end_turn_advances(self) -> None:
        scene, engine = _make_scene()
        scene.update(16)
        assert scene.phase == TurnPhase.WAITING_INPUT
        round_before = engine.round_number
        scene.shortcut_end_turn()
        scene.update(16)
        assert engine.round_number > round_before

    def test_shortcut_ignored_outside_waiting(self) -> None:
        scene, _ = _make_scene()
        scene.shortcut_end_turn()
        assert scene.phase == TurnPhase.STARTING_ROUND
