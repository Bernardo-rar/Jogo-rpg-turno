"""Testes para barreira integrada ao Character base."""

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_modifiers import ClassModifiers
from src.core.characters.position import Position

import pytest

SIMPLE_MODS = ClassModifiers(
    hit_dice=10,
    mod_hp_flat=0,
    mod_hp_mult=1,
    mana_multiplier=1,
    mod_atk_physical=2,
    mod_atk_magical=1,
    mod_def_physical=1,
    mod_def_magical=1,
    regen_hp_mod=0,
    regen_mana_mod=0,
)

EMPTY_THRESHOLDS = ThresholdCalculator({})
SIMPLE_CONFIG = CharacterConfig(
    class_modifiers=SIMPLE_MODS,
    threshold_calculator=EMPTY_THRESHOLDS,
    position=Position.FRONT,
)


@pytest.fixture
def attrs() -> Attributes:
    a = Attributes()
    for at in AttributeType:
        a.set(at, 10)
    return a


@pytest.fixture
def char(attrs: Attributes) -> Character:
    return Character("TestChar", attrs, SIMPLE_CONFIG)


class TestCharacterHasBarrier:
    def test_character_has_barrier(self, char: Character):
        assert char.barrier is not None

    def test_barrier_starts_empty(self, char: Character):
        assert char.barrier.current == 0

    def test_barrier_max_is_max_hp(self, char: Character):
        assert char.barrier.max_value == char.max_hp


class TestCharacterTakeDamageWithBarrier:
    def test_take_damage_uses_barrier(self, char: Character):
        # max_hp=40, so add(30) gives 30 barrier points
        char.barrier.add(30)
        char.take_damage(20)
        assert char.barrier.current == 10
        assert char.current_hp == char.max_hp

    def test_take_damage_overflow_hits_hp(self, char: Character):
        char.barrier.add(30)
        char.take_damage(50)
        assert char.barrier.current == 0
        assert char.current_hp == char.max_hp - 20

    def test_take_damage_no_barrier_direct_to_hp(self, char: Character):
        char.take_damage(15)
        assert char.current_hp == char.max_hp - 15

    def test_take_damage_returns_total_absorbed(self, char: Character):
        char.barrier.add(40)
        result = char.take_damage(30)
        assert result == 30

    def test_take_damage_returns_barrier_plus_hp(self, char: Character):
        char.barrier.add(20)
        result = char.take_damage(50)
        # 20 barrier + 30 HP = 50
        assert result == 50

    def test_take_damage_kills_through_barrier(self, char: Character):
        char.barrier.add(10)
        hp = char.max_hp
        char.take_damage(10 + hp)
        assert char.is_alive is False
