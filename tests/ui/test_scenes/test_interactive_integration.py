"""Testes de integracao — combate interativo end-to-end."""

from __future__ import annotations

from src.core.combat.combat_engine import CombatResult
from src.core.combat.player_action import PlayerAction, PlayerActionType
from src.ui.scenes.interactive_combat import TurnPhase
from src.ui.scenes.interactive_combat_factory import create_interactive_combat

from tests.core.test_combat.conftest import _build_char


def _run_until_waiting(scene, max_steps: int = 50) -> None:
    """Avanca ate WAITING_INPUT ou COMBAT_OVER."""
    for _ in range(max_steps):
        scene.update(16)
        if scene.phase in (TurnPhase.WAITING_INPUT, TurnPhase.COMBAT_OVER):
            return


def _submit_end_turn(scene) -> None:
    scene.submit_player_action(
        PlayerAction(action_type=PlayerActionType.END_TURN),
    )


class TestFullTurnBasicAttack:
    def test_basic_attack_deals_damage(self) -> None:
        party = [_build_char("Hero")]
        enemies = [_build_char("Goblin")]
        scene = create_interactive_combat(party, enemies)
        _run_until_waiting(scene)
        assert scene.phase == TurnPhase.WAITING_INPUT
        goblin_hp_before = enemies[0].current_hp
        action = PlayerAction(
            action_type=PlayerActionType.BASIC_ATTACK,
            target_name="Goblin",
        )
        scene.submit_player_action(action)
        assert enemies[0].current_hp < goblin_hp_before


class TestFullTurnEndTurn:
    def test_end_turn_advances_round(self) -> None:
        party = [_build_char("Hero")]
        enemies = [_build_char("Goblin")]
        scene = create_interactive_combat(party, enemies)
        _run_until_waiting(scene)
        _submit_end_turn(scene)
        scene.update(16)
        _run_until_waiting(scene)
        assert scene.phase == TurnPhase.WAITING_INPUT


class TestAITurnExecutes:
    def test_ai_attacks_party(self) -> None:
        party = [_build_char("Hero")]
        enemies = [_build_char("Goblin")]
        scene = create_interactive_combat(party, enemies)
        hero_hp = party[0].current_hp
        _run_until_waiting(scene)
        _submit_end_turn(scene)
        scene.update(16)
        _run_until_waiting(scene)
        assert party[0].current_hp <= hero_hp


class TestCombatRunsToCompletion:
    def test_combat_ends_eventually(self) -> None:
        party = [_build_char("Hero")]
        enemies = [_build_char("Goblin")]
        scene = create_interactive_combat(party, enemies)
        for _ in range(500):
            scene.update(16)
            if scene.phase == TurnPhase.WAITING_INPUT:
                action = PlayerAction(
                    action_type=PlayerActionType.BASIC_ATTACK,
                    target_name="Goblin",
                )
                scene.submit_player_action(action)
                _submit_end_turn(scene)
            if scene.phase == TurnPhase.COMBAT_OVER:
                break
        assert scene.phase == TurnPhase.COMBAT_OVER


class TestEngineBackwardCompat:
    def test_run_combat_still_works(self) -> None:
        from src.core.combat.basic_attack_handler import BasicAttackHandler
        from src.core.combat.combat_engine import CombatEngine

        party = [_build_char("A")]
        enemies = [_build_char("B")]
        engine = CombatEngine(party, enemies, BasicAttackHandler())
        result = engine.run_combat()
        assert result in (CombatResult.PARTY_VICTORY, CombatResult.PARTY_DEFEAT)
