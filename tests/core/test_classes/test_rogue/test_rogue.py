from __future__ import annotations

import pytest

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_modifiers import ClassModifiers
from src.core.characters.position import Position
from src.core.classes.rogue.rogue import Rogue
from src.core.classes.rogue.rogue_config import load_rogue_config

_CONFIG = load_rogue_config()

ROGUE_MODS = ClassModifiers(
    hit_dice=8,
    vida_mod=0,
    mod_hp=6,
    mana_multiplier=6,
    mod_atk_physical=8,
    mod_atk_magical=4,
    mod_def_physical=4,
    mod_def_magical=3,
    regen_hp_mod=3,
    regen_mana_mod=3,
)

EMPTY_THRESHOLDS = ThresholdCalculator({})
ROGUE_CONFIG = CharacterConfig(
    class_modifiers=ROGUE_MODS,
    threshold_calculator=EMPTY_THRESHOLDS,
    position=Position.FRONT,
)


@pytest.fixture
def attrs() -> Attributes:
    return Attributes({
        AttributeType.STRENGTH: 6,
        AttributeType.DEXTERITY: 12,
        AttributeType.CONSTITUTION: 5,
        AttributeType.INTELLIGENCE: 4,
        AttributeType.WISDOM: 3,
        AttributeType.CHARISMA: 4,
        AttributeType.MIND: 3,
    })


@pytest.fixture
def rogue(attrs: Attributes) -> Rogue:
    return Rogue("Shadow", attrs, ROGUE_CONFIG)


# --- LSP ---


class TestRogueIsCharacter:
    def test_is_instance_of_character(self, rogue: Rogue) -> None:
        assert isinstance(rogue, Character)

    def test_has_name(self, rogue: Rogue) -> None:
        assert rogue.name == "Shadow"

    def test_has_hp(self, rogue: Rogue) -> None:
        assert rogue.max_hp > 0

    def test_has_mana(self, rogue: Rogue) -> None:
        assert rogue.max_mana > 0

    def test_take_damage_works(self, rogue: Rogue) -> None:
        actual = rogue.take_damage(10)
        assert actual > 0
        assert rogue.current_hp < rogue.max_hp

    def test_is_alive(self, rogue: Rogue) -> None:
        assert rogue.is_alive

    def test_heal_works(self, rogue: Rogue) -> None:
        rogue.take_damage(20)
        healed = rogue.heal(10)
        assert healed > 0


# --- Stats ---


class TestRogueStats:
    def test_max_hp_formula(self, rogue: Rogue, attrs: Attributes) -> None:
        con = attrs.get(AttributeType.CONSTITUTION)
        expected = ((8 + con + 0) * 2) * 6
        assert rogue.max_hp == expected

    def test_max_mana_formula(self, rogue: Rogue, attrs: Attributes) -> None:
        mind = attrs.get(AttributeType.MIND)
        expected = 6 * mind * 10
        assert rogue.max_mana == expected

    def test_physical_attack(self, rogue: Rogue) -> None:
        assert rogue.physical_attack > 0

    def test_magical_attack(self, rogue: Rogue) -> None:
        assert rogue.magical_attack > 0

    def test_physical_defense(self, rogue: Rogue) -> None:
        assert rogue.physical_defense > 0

    def test_magical_defense(self, rogue: Rogue) -> None:
        assert rogue.magical_defense > 0


# --- Stealth Integration ---


class TestRogueStealth:
    def test_not_in_stealth_by_default(self, rogue: Rogue) -> None:
        assert rogue.guaranteed_crit is False

    def test_enter_stealth(self, rogue: Rogue) -> None:
        assert rogue.enter_stealth() is True
        assert rogue.stealth.is_active is True

    def test_guaranteed_crit_when_stealthed(self, rogue: Rogue) -> None:
        rogue.enter_stealth()
        assert rogue.guaranteed_crit is True

    def test_break_stealth(self, rogue: Rogue) -> None:
        rogue.enter_stealth()
        assert rogue.break_stealth() is True
        assert rogue.guaranteed_crit is False

    def test_taking_damage_breaks_stealth(self, rogue: Rogue) -> None:
        rogue.enter_stealth()
        rogue.take_damage(5)
        assert rogue.stealth.is_active is False

    def test_take_damage_returns_correct_amount(self, rogue: Rogue) -> None:
        actual = rogue.take_damage(10)
        assert actual > 0


# --- Passivas ---


class TestRoguePassives:
    def test_free_item_use_is_true(self, rogue: Rogue) -> None:
        assert rogue.free_item_use is True

    def test_crit_bonus_scales_with_dex(
        self, rogue: Rogue, attrs: Attributes
    ) -> None:
        dex = attrs.get(AttributeType.DEXTERITY)
        expected = dex * _CONFIG.crit_bonus_per_dex
        assert rogue.crit_chance_bonus == pytest.approx(expected)

    def test_poison_damage_bonus(self, rogue: Rogue) -> None:
        assert rogue.poison_damage_bonus == _CONFIG.poison_damage_bonus

    def test_extra_skill_slots(self, rogue: Rogue) -> None:
        assert rogue.extra_skill_slots == _CONFIG.extra_skill_slots


# --- Speed ---


class TestRogueSpeed:
    def test_speed_has_passive_bonus(self, rogue: Rogue) -> None:
        base_char = Character("Base", rogue._attributes, ROGUE_CONFIG)
        base_speed = base_char.speed
        passive = int(base_speed * _CONFIG.speed_bonus_pct)
        assert rogue.speed == base_speed + passive

    def test_speed_with_crit_boost(self, rogue: Rogue) -> None:
        speed_before = rogue.speed
        rogue.on_crit()
        assert rogue.speed > speed_before

    def test_crit_boost_decays_over_turns(self, rogue: Rogue) -> None:
        rogue.on_crit()
        speed_boosted = rogue.speed
        rogue.tick_crit_speed_boost()
        assert rogue.speed == speed_boosted

    def test_crit_boost_expires(self, rogue: Rogue) -> None:
        rogue.on_crit()
        speed_before_boost = Character(
            "Base", rogue._attributes, ROGUE_CONFIG
        ).speed
        passive = int(speed_before_boost * _CONFIG.speed_bonus_pct)
        expected_base = speed_before_boost + passive
        for _ in range(_CONFIG.crit_speed_boost_duration):
            rogue.tick_crit_speed_boost()
        assert rogue.speed == expected_base

    def test_crit_boost_refreshes_on_new_crit(self, rogue: Rogue) -> None:
        rogue.on_crit()
        rogue.tick_crit_speed_boost()
        rogue.on_crit()
        speed_boosted = rogue.speed
        rogue.tick_crit_speed_boost()
        assert rogue.speed == speed_boosted


# --- Crit Speed Boost ---


class TestRogueCritSpeedBoost:
    def test_on_crit_sets_boost_duration(self, rogue: Rogue) -> None:
        rogue.on_crit()
        assert rogue._crit_speed_remaining == _CONFIG.crit_speed_boost_duration

    def test_tick_decrements_boost(self, rogue: Rogue) -> None:
        rogue.on_crit()
        rogue.tick_crit_speed_boost()
        expected = _CONFIG.crit_speed_boost_duration - 1
        assert rogue._crit_speed_remaining == expected

    def test_tick_noop_when_no_boost(self, rogue: Rogue) -> None:
        rogue.tick_crit_speed_boost()
        assert rogue._crit_speed_remaining == 0


# --- Level Up ---


class TestRogueLevelUp:
    def test_on_level_up_no_error(self, rogue: Rogue) -> None:
        rogue.on_level_up()

    def test_stats_scale_with_level(self, attrs: Attributes) -> None:
        config_l1 = CharacterConfig(
            class_modifiers=ROGUE_MODS,
            threshold_calculator=EMPTY_THRESHOLDS,
            position=Position.FRONT,
            level=1,
        )
        config_l5 = CharacterConfig(
            class_modifiers=ROGUE_MODS,
            threshold_calculator=EMPTY_THRESHOLDS,
            position=Position.FRONT,
            level=5,
        )
        r1 = Rogue("R1", attrs, config_l1)
        r5 = Rogue("R5", attrs, config_l5)
        assert r5.max_hp > r1.max_hp
