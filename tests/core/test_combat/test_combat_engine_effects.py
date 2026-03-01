"""Testes para integracao CombatEngine + Effects (tick, skip, death por DoT)."""

import pytest

from src.core.combat.basic_attack_handler import BasicAttackHandler
from src.core.combat.combat_engine import (
    CombatEngine,
    CombatEvent,
    CombatResult,
    TurnContext,
)
from src.core.combat.effect_phase import EffectLogEntry
from src.core.effects.ailments.ailment_factory import (
    create_burn,
    create_freeze,
    create_paralysis,
    create_poison,
)
from src.core.effects.buff_factory import create_flat_buff, create_flat_debuff
from src.core.effects.modifiable_stat import ModifiableStat

from tests.core.test_combat.conftest import _build_char as _make_char


class DoNothingHandler:
    def execute_turn(self, context: TurnContext) -> list[CombatEvent]:
        return []


class TestDotTicksInCombat:

    def test_dot_ticks_at_turn_start(self) -> None:
        hero = _make_char("Hero")
        enemy = _make_char("Enemy")
        poison = create_poison(damage_per_tick=5, duration=3)
        enemy.effect_manager.add_effect(poison)
        hp_before = enemy.current_hp
        engine = CombatEngine([hero], [enemy], DoNothingHandler())
        engine.run_round()
        assert enemy.current_hp < hp_before

    def test_dot_kills_before_action(self) -> None:
        hero = _make_char("Hero")
        enemy = _make_char("Enemy")
        enemy.take_damage(enemy.current_hp - 1)
        burn = create_burn(damage_per_tick=10, duration=3)
        enemy.effect_manager.add_effect(burn)
        engine = CombatEngine([hero], [enemy], DoNothingHandler())
        result = engine.run_round()
        assert not enemy.is_alive
        assert result == CombatResult.PARTY_VICTORY

    def test_dot_kills_last_enemy_ends_combat(self) -> None:
        hero = _make_char("Hero")
        enemy = _make_char("Enemy")
        enemy.take_damage(enemy.current_hp - 2)
        poison = create_poison(damage_per_tick=5, duration=3)
        enemy.effect_manager.add_effect(poison)
        engine = CombatEngine([hero], [enemy], DoNothingHandler())
        result = engine.run_round()
        assert result == CombatResult.PARTY_VICTORY

    def test_dot_kills_last_party_ends_combat(self) -> None:
        hero = _make_char("Hero")
        enemy = _make_char("Enemy")
        hero.take_damage(hero.current_hp - 1)
        burn = create_burn(damage_per_tick=10, duration=3)
        hero.effect_manager.add_effect(burn)
        engine = CombatEngine([hero], [enemy], DoNothingHandler())
        result = engine.run_round()
        assert result == CombatResult.PARTY_DEFEAT


class TestCcSkipTurn:

    def test_frozen_skips_turn(self) -> None:
        hero = _make_char("Hero", speed=5)
        enemy = _make_char("Enemy", speed=15)
        freeze = create_freeze(duration=2)
        hero.effect_manager.add_effect(freeze)
        events_recorded = []

        class SpyHandler:
            def execute_turn(self, context: TurnContext) -> list[CombatEvent]:
                events_recorded.append(context.combatant.name)
                return []

        engine = CombatEngine([hero], [enemy], SpyHandler())
        engine.run_round()
        assert "Hero" not in events_recorded
        assert "Enemy" in events_recorded

    def test_frozen_still_takes_dot(self) -> None:
        hero = _make_char("Hero")
        enemy = _make_char("Enemy")
        freeze = create_freeze(duration=2)
        poison = create_poison(damage_per_tick=5, duration=3)
        hero.effect_manager.add_effect(freeze)
        hero.effect_manager.add_effect(poison)
        hp_before = hero.current_hp
        engine = CombatEngine([hero], [enemy], DoNothingHandler())
        engine.run_round()
        assert hero.current_hp < hp_before


class TestEffectDuration:

    def test_effect_expires_after_duration(self) -> None:
        hero = _make_char("Hero")
        enemy = _make_char("Enemy")
        poison = create_poison(damage_per_tick=3, duration=2)
        enemy.effect_manager.add_effect(poison)
        engine = CombatEngine([hero], [enemy], DoNothingHandler())
        engine.run_round()
        engine.run_round()
        assert enemy.effect_manager.count == 0

    def test_multiple_rounds_effects_tick_each(self) -> None:
        hero = _make_char("Hero")
        enemy = _make_char("Enemy")
        poison = create_poison(damage_per_tick=3, duration=3)
        enemy.effect_manager.add_effect(poison)
        hp_before = enemy.current_hp
        engine = CombatEngine([hero], [enemy], DoNothingHandler())
        engine.run_round()
        engine.run_round()
        assert enemy.current_hp == hp_before - 6


class TestBuffsInCombat:

    def test_buff_modifies_attack_in_combat(self) -> None:
        hero = _make_char("Hero")
        enemy = _make_char("Enemy")
        buff = create_flat_buff(ModifiableStat.PHYSICAL_ATTACK, 100, 3)
        hero.effect_manager.add_effect(buff)
        hp_before = enemy.current_hp
        engine = CombatEngine([hero], [enemy], BasicAttackHandler())
        engine.run_round()
        damage_dealt = hp_before - enemy.current_hp
        assert damage_dealt > 10

    def test_debuff_modifies_defense_in_combat(self) -> None:
        hero = _make_char("Hero")
        enemy = _make_char("Enemy")
        debuff = create_flat_debuff(ModifiableStat.PHYSICAL_DEFENSE, 20, 3)
        enemy.effect_manager.add_effect(debuff)
        hp_before = enemy.current_hp
        engine = CombatEngine([hero], [enemy], BasicAttackHandler())
        engine.run_round()
        damage_dealt = hp_before - enemy.current_hp
        assert damage_dealt > 10


class TestEngineEffectLog:

    def test_dot_damage_logged(self) -> None:
        hero = _make_char("Hero")
        enemy = _make_char("Enemy")
        poison = create_poison(damage_per_tick=5, duration=3)
        enemy.effect_manager.add_effect(poison)
        engine = CombatEngine([hero], [enemy], DoNothingHandler())
        engine.run_round()
        tick_entries = [
            e for e in engine.effect_log if not e.is_skip
        ]
        assert len(tick_entries) > 0

    def test_skip_turn_logged(self) -> None:
        hero = _make_char("Hero")
        enemy = _make_char("Enemy")
        freeze = create_freeze(duration=2)
        hero.effect_manager.add_effect(freeze)
        engine = CombatEngine([hero], [enemy], DoNothingHandler())
        engine.run_round()
        skip_entries = [
            e for e in engine.effect_log if e.is_skip
        ]
        assert len(skip_entries) > 0

    def test_engine_effect_log_property(self) -> None:
        hero = _make_char("Hero")
        enemy = _make_char("Enemy")
        engine = CombatEngine([hero], [enemy], DoNothingHandler())
        assert engine.effect_log == []


class TestRegressionNoEffects:

    def test_combat_no_effects_unchanged(self) -> None:
        hero = _make_char("Hero")
        enemy = _make_char("Enemy")
        engine = CombatEngine([hero], [enemy], BasicAttackHandler())
        result = engine.run_combat()
        assert result in (CombatResult.PARTY_VICTORY, CombatResult.PARTY_DEFEAT)

    def test_characters_tick_independently(self) -> None:
        hero = _make_char("Hero")
        enemy = _make_char("Enemy")
        poison = create_poison(damage_per_tick=3, duration=2)
        enemy.effect_manager.add_effect(poison)
        hero_hp = hero.current_hp
        engine = CombatEngine([hero], [enemy], DoNothingHandler())
        engine.run_round()
        assert hero.current_hp == hero_hp

    def test_effect_added_mid_combat_ticks_next_turn(self) -> None:
        hero = _make_char("Hero", speed=15)
        enemy = _make_char("Enemy", speed=5)

        class ApplyPoisonHandler:
            def __init__(self):
                self.applied = False

            def execute_turn(self, context: TurnContext) -> list[CombatEvent]:
                if context.combatant.name == "Hero" and not self.applied:
                    poison = create_poison(damage_per_tick=5, duration=3)
                    context.enemies[0].effect_manager.add_effect(poison)
                    self.applied = True
                return []

        handler = ApplyPoisonHandler()
        engine = CombatEngine([hero], [enemy], handler)
        engine.run_round()
        hp_after_r1 = enemy.current_hp
        engine.run_round()
        assert enemy.current_hp < hp_after_r1
