"""Testes para effect_phase - funcoes puras de tick de efeitos no combate."""

import pytest

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_modifiers import ClassModifiers
from src.core.combat.effect_phase import (
    apply_tick_results,
    process_effect_ticks,
    should_skip_turn,
)
from src.core.effects.ailments.ailment_factory import (
    create_burn,
    create_freeze,
    create_poison,
)
from src.core.effects.effect_manager import EffectManager
from src.core.effects.tick_result import TickResult

BASIC_MODS = ClassModifiers(
    hit_dice=10,
    vida_mod=0,
    mod_hp=8,
    mana_multiplier=6,
    mod_atk_physical=8,
    mod_atk_magical=6,
    mod_def_physical=5,
    mod_def_magical=3,
    regen_hp_mod=3,
    regen_mana_mod=2,
)


@pytest.fixture
def attrs() -> Attributes:
    return Attributes({
        AttributeType.STRENGTH: 10,
        AttributeType.DEXTERITY: 8,
        AttributeType.CONSTITUTION: 5,
        AttributeType.INTELLIGENCE: 3,
        AttributeType.WISDOM: 4,
        AttributeType.CHARISMA: 3,
        AttributeType.MIND: 4,
    })


@pytest.fixture
def threshold_calc() -> ThresholdCalculator:
    return ThresholdCalculator.from_json("data/attributes/thresholds.json")


@pytest.fixture
def character(attrs, threshold_calc) -> Character:
    return Character(
        name="TestHero",
        attributes=attrs,
        config=CharacterConfig(
            class_modifiers=BASIC_MODS,
            threshold_calculator=threshold_calc,
        ),
    )


class TestProcessEffectTicks:

    def test_empty_manager(self) -> None:
        manager = EffectManager()
        results = process_effect_ticks(manager)
        assert results == []

    def test_single_dot(self) -> None:
        manager = EffectManager()
        poison = create_poison(damage_per_tick=5, duration=3)
        manager.add_effect(poison)
        results = process_effect_ticks(manager)
        assert len(results) == 1
        assert results[0].damage == 5

    def test_multiple_effects(self) -> None:
        manager = EffectManager()
        poison = create_poison(damage_per_tick=5, duration=3)
        burn = create_burn(damage_per_tick=8, duration=2)
        manager.add_effect(poison)
        manager.add_effect(burn)
        results = process_effect_ticks(manager)
        assert len(results) == 2

    def test_expires_effect(self) -> None:
        manager = EffectManager()
        poison = create_poison(damage_per_tick=5, duration=1)
        manager.add_effect(poison)
        process_effect_ticks(manager)
        assert manager.count == 0


class TestApplyTickResults:

    def test_applies_damage(self, character) -> None:
        hp_before = character.current_hp
        results = [TickResult(damage=10, message="Poison")]
        apply_tick_results(character, results, round_number=1)
        assert character.current_hp == hp_before - 10

    def test_applies_healing(self, character) -> None:
        character.take_damage(20)
        hp_before = character.current_hp
        results = [TickResult(healing=10, message="Regen")]
        apply_tick_results(character, results, round_number=1)
        assert character.current_hp == hp_before + 10

    def test_applies_mana_restore(self, character) -> None:
        character.spend_mana(10)
        mana_before = character.current_mana
        results = [TickResult(mana_change=5, message="Mana regen")]
        apply_tick_results(character, results, round_number=1)
        assert character.current_mana == mana_before + 5

    def test_applies_mana_drain(self, character) -> None:
        mana_before = character.current_mana
        results = [TickResult(mana_change=-5, message="Mana drain")]
        apply_tick_results(character, results, round_number=1)
        assert character.current_mana == mana_before - 5

    def test_kills_character(self, character) -> None:
        character.take_damage(character.current_hp - 1)
        results = [TickResult(damage=999, message="Lethal DoT")]
        apply_tick_results(character, results, round_number=1)
        assert not character.is_alive

    def test_returns_log_entries(self, character) -> None:
        results = [TickResult(damage=10, message="Poison ticks")]
        entries = apply_tick_results(character, results, round_number=2)
        assert len(entries) == 1
        assert entries[0].round_number == 2

    def test_damage_log_format(self, character) -> None:
        results = [TickResult(damage=10, message="Poison ticks")]
        entries = apply_tick_results(character, results, round_number=1)
        assert entries[0].value == 10
        assert entries[0].character_name == character.name

    def test_skip_dead_character(self, character) -> None:
        character.take_damage(character.current_hp)
        results = [TickResult(damage=10, message="DoT on dead")]
        entries = apply_tick_results(character, results, round_number=1)
        assert len(entries) == 0

    def test_multiple_dots_cumulative(self, character) -> None:
        hp_before = character.current_hp
        results = [
            TickResult(damage=5, message="Poison"),
            TickResult(damage=8, message="Burn"),
        ]
        apply_tick_results(character, results, round_number=1)
        assert character.current_hp == hp_before - 13

    def test_tick_message_preserved(self, character) -> None:
        results = [TickResult(damage=5, message="Poison deals 5 damage")]
        entries = apply_tick_results(character, results, round_number=1)
        assert "Poison deals 5 damage" in entries[0].message

    def test_empty_results_empty_log(self, character) -> None:
        entries = apply_tick_results(character, [], round_number=1)
        assert entries == []

    def test_no_log_for_zero_effect_tick(self, character) -> None:
        results = [TickResult(message="Confused! Attacks may target randomly.")]
        entries = apply_tick_results(character, results, round_number=1)
        assert len(entries) == 0


class TestShouldSkipTurn:

    def test_false_empty(self) -> None:
        assert should_skip_turn([]) is False

    def test_false_normal_ticks(self) -> None:
        results = [TickResult(damage=5, message="Poison")]
        assert should_skip_turn(results) is False

    def test_true_freeze(self) -> None:
        results = [TickResult(skip_turn=True, message="Frozen")]
        assert should_skip_turn(results) is True

    def test_true_mixed(self) -> None:
        results = [
            TickResult(damage=5, message="Poison"),
            TickResult(skip_turn=True, message="Frozen"),
        ]
        assert should_skip_turn(results) is True

    def test_dot_and_skip_same_turn(self, character) -> None:
        hp_before = character.current_hp
        results = [
            TickResult(damage=10, message="Burn"),
            TickResult(skip_turn=True, message="Frozen"),
        ]
        apply_tick_results(character, results, round_number=1)
        assert character.current_hp == hp_before - 10
        assert should_skip_turn(results) is True

    def test_mana_drain_partial_when_insufficient(self, character) -> None:
        """Mana drain drena o que tiver disponivel, nao falha silenciosamente."""
        total_mana = character.current_mana
        character.spend_mana(total_mana - 3)
        results = [TickResult(mana_change=-10, message="Mana drain")]
        apply_tick_results(character, results, round_number=1)
        assert character.current_mana == 0
