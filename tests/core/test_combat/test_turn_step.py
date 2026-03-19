"""Testes para TurnStepResult e API step-by-step do CombatEngine."""

import pytest

from src.core.combat.action_economy import ActionType
from src.core.combat.basic_attack_handler import BasicAttackHandler
from src.core.combat.combat_engine import (
    CombatEngine,
    CombatEvent,
    CombatResult,
    EventType,
    TurnContext,
)
from src.core.combat.turn_step import TurnStepResult
from src.core.effects.ailments.freeze import Freeze
from src.core.effects.ailments.poison import Poison

from tests.core.test_combat.conftest import _build_char


class DoNothingHandler:
    def execute_turn(self, context: TurnContext) -> list[CombatEvent]:
        return []


class TestTurnStepResult:
    def test_is_frozen_dataclass(self):
        result = TurnStepResult(
            can_act=True, context=None, effect_entries=(),
        )
        with pytest.raises(AttributeError):
            result.can_act = False  # type: ignore[misc]

    def test_default_skip_reason_is_empty(self):
        result = TurnStepResult(
            can_act=True, context=None, effect_entries=(),
        )
        assert result.skip_reason == ""


class TestPrepareTurn:
    def test_alive_combatant_can_act(self):
        engine = CombatEngine(
            [_build_char("Hero")], [_build_char("Goblin")],
            DoNothingHandler(),
        )
        engine.start_round()
        name = engine.get_next_combatant()
        step = engine.prepare_turn(name)
        assert step.can_act is True
        assert step.context is not None

    def test_context_has_combatant(self):
        engine = CombatEngine(
            [_build_char("Hero")], [_build_char("Goblin")],
            DoNothingHandler(),
        )
        engine.start_round()
        name = engine.get_next_combatant()
        step = engine.prepare_turn(name)
        assert step.context.combatant.name == name

    def test_context_has_correct_round(self):
        engine = CombatEngine(
            [_build_char("Hero")], [_build_char("Goblin")],
            DoNothingHandler(),
        )
        engine.start_round()
        name = engine.get_next_combatant()
        step = engine.prepare_turn(name)
        assert step.context.round_number == 1

    def test_context_action_economy_is_reset(self):
        engine = CombatEngine(
            [_build_char("Hero")], [_build_char("Goblin")],
            DoNothingHandler(),
        )
        engine.start_round()
        name = engine.get_next_combatant()
        step = engine.prepare_turn(name)
        economy = step.context.action_economy
        assert economy.is_available(ActionType.ACTION)
        assert economy.is_available(ActionType.BONUS_ACTION)
        assert economy.is_available(ActionType.REACTION)

    def test_dead_combatant_cannot_act(self):
        hero = _build_char("Hero")
        hero.take_damage(hero.current_hp)
        engine = CombatEngine(
            [hero], [_build_char("Goblin")], DoNothingHandler(),
        )
        engine.start_round()
        step = engine.prepare_turn("Hero")
        assert step.can_act is False
        assert step.context is None

    def test_cc_combatant_cannot_act(self):
        hero = _build_char("Hero")
        hero.effect_manager.add_effect(Freeze(duration=2))
        engine = CombatEngine(
            [hero], [_build_char("Goblin")], DoNothingHandler(),
        )
        engine.start_round()
        step = engine.prepare_turn("Hero")
        assert step.can_act is False
        assert step.skip_reason != ""

    def test_effect_ticks_are_recorded(self):
        hero = _build_char("Hero")
        hero.effect_manager.add_effect(Poison(duration=3, damage_per_tick=5))
        engine = CombatEngine(
            [hero], [_build_char("Goblin")], DoNothingHandler(),
        )
        engine.start_round()
        step = engine.prepare_turn("Hero")
        assert len(step.effect_entries) > 0

    def test_effect_entries_added_to_engine_log(self):
        hero = _build_char("Hero")
        hero.effect_manager.add_effect(Poison(duration=3, damage_per_tick=5))
        engine = CombatEngine(
            [hero], [_build_char("Goblin")], DoNothingHandler(),
        )
        engine.start_round()
        engine.prepare_turn("Hero")
        assert len(engine.effect_log) > 0


class TestResolveTurn:
    def test_records_events(self):
        engine = CombatEngine(
            [_build_char("Hero")], [_build_char("Goblin")],
            DoNothingHandler(),
        )
        engine.start_round()
        engine.get_next_combatant()
        events = [
            CombatEvent(
                round_number=1, actor_name="Hero",
                target_name="Goblin", value=10,
            ),
        ]
        engine.resolve_turn(events)
        assert len(engine.events) == 1

    def test_detects_victory(self):
        goblin = _build_char("Goblin")
        goblin.take_damage(goblin.current_hp)
        engine = CombatEngine(
            [_build_char("Hero")], [goblin], DoNothingHandler(),
        )
        engine.start_round()
        engine.get_next_combatant()
        result = engine.resolve_turn([])
        assert result == CombatResult.PARTY_VICTORY

    def test_detects_defeat(self):
        hero = _build_char("Hero")
        hero.take_damage(hero.current_hp)
        engine = CombatEngine(
            [hero], [_build_char("Goblin")], DoNothingHandler(),
        )
        engine.start_round()
        engine.get_next_combatant()
        result = engine.resolve_turn([])
        assert result == CombatResult.PARTY_DEFEAT

    def test_returns_none_when_ongoing(self):
        engine = CombatEngine(
            [_build_char("Hero")], [_build_char("Goblin")],
            DoNothingHandler(),
        )
        engine.start_round()
        engine.get_next_combatant()
        result = engine.resolve_turn([])
        assert result is None


class TestStartRound:
    def test_increments_round_number(self):
        engine = CombatEngine(
            [_build_char("Hero")], [_build_char("Goblin")],
            DoNothingHandler(),
        )
        engine.start_round()
        assert engine.round_number == 1

    def test_second_start_round_increments_again(self):
        engine = CombatEngine(
            [_build_char("Hero")], [_build_char("Goblin")],
            DoNothingHandler(),
        )
        engine.start_round()
        engine.start_round()
        assert engine.round_number == 2


class TestGetNextCombatant:
    def test_returns_first_combatant_name(self):
        engine = CombatEngine(
            [_build_char("Hero")], [_build_char("Goblin")],
            DoNothingHandler(),
        )
        engine.start_round()
        name = engine.get_next_combatant()
        assert name in ("Hero", "Goblin")

    def test_returns_none_when_exhausted(self):
        engine = CombatEngine(
            [_build_char("Hero")], [_build_char("Goblin")],
            DoNothingHandler(),
        )
        engine.start_round()
        engine.get_next_combatant()
        engine.get_next_combatant()
        assert engine.get_next_combatant() is None


class TestBackwardCompatibility:
    def test_run_round_still_works(self):
        engine = CombatEngine(
            [_build_char("A")], [_build_char("Z")],
            BasicAttackHandler(),
        )
        result = engine.run_round()
        assert result is None
        assert engine.round_number == 1
        assert len(engine.events) == 2

    def test_run_combat_still_works(self):
        engine = CombatEngine(
            [_build_char("Alpha")], [_build_char("Zeta")],
            BasicAttackHandler(),
        )
        result = engine.run_combat()
        assert result == CombatResult.PARTY_VICTORY
