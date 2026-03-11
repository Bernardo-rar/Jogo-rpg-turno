from __future__ import annotations

import pytest

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_modifiers import ClassModifiers
from src.core.characters.position import Position
from src.core.classes.druid.animal_form import AnimalForm, load_animal_form_modifiers
from src.core.classes.druid.druid import Druid
from src.core.classes.druid.druid_config import load_druid_config
from src.core.classes.druid.field_condition import (
    FieldConditionType,
    load_field_condition_configs,
)

_CONFIG = load_druid_config()
_FORMS = load_animal_form_modifiers()
_FIELDS = load_field_condition_configs()

DRUID_MODS = ClassModifiers(
    hit_dice=8,
    vida_mod=0,
    mod_hp=6,
    mana_multiplier=10,
    mod_atk_physical=5,
    mod_atk_magical=7,
    mod_def_physical=4,
    mod_def_magical=5,
    regen_hp_mod=5,
    regen_mana_mod=5,
)

EMPTY_THRESHOLDS = ThresholdCalculator({})
DRUID_CONFIG = CharacterConfig(
    class_modifiers=DRUID_MODS,
    threshold_calculator=EMPTY_THRESHOLDS,
    position=Position.FRONT,
)


@pytest.fixture
def attrs() -> Attributes:
    return Attributes({
        AttributeType.STRENGTH: 5,
        AttributeType.DEXTERITY: 6,
        AttributeType.CONSTITUTION: 7,
        AttributeType.INTELLIGENCE: 8,
        AttributeType.WISDOM: 7,
        AttributeType.CHARISMA: 6,
        AttributeType.MIND: 8,
    })


@pytest.fixture
def druid(attrs: Attributes) -> Druid:
    return Druid("Verdantis", attrs, DRUID_CONFIG)


# --- LSP ---


class TestDruidIsCharacter:
    def test_is_instance_of_character(self, druid: Druid) -> None:
        assert isinstance(druid, Character)

    def test_has_name(self, druid: Druid) -> None:
        assert druid.name == "Verdantis"

    def test_has_hp(self, druid: Druid) -> None:
        assert druid.max_hp > 0

    def test_has_mana(self, druid: Druid) -> None:
        assert druid.max_mana > 0

    def test_take_damage_works(self, druid: Druid) -> None:
        actual = druid.take_damage(10)
        assert actual > 0
        assert druid.current_hp < druid.max_hp

    def test_is_alive(self, druid: Druid) -> None:
        assert druid.is_alive

    def test_speed_positive(self, druid: Druid) -> None:
        assert druid.speed > 0


# --- Stats Base (HUMANOID) ---


class TestDruidStats:
    def test_max_hp_formula(self, druid: Druid, attrs: Attributes) -> None:
        con = attrs.get(AttributeType.CONSTITUTION)
        expected = ((8 + con + 0) * 2) * 6
        assert druid.max_hp == expected

    def test_max_mana_formula(self, druid: Druid, attrs: Attributes) -> None:
        mind = attrs.get(AttributeType.MIND)
        expected = 10 * mind * 5
        assert druid.max_mana == expected

    def test_magical_attack_includes_nature_bonus(
        self, druid: Druid
    ) -> None:
        base_char = Character("Base", druid._attributes, DRUID_CONFIG)
        base_mag = base_char.magical_attack
        expected = int(base_mag * (1.0 + _CONFIG.nature_atk_bonus))
        assert druid.magical_attack == expected

    def test_hp_regen_includes_passive_bonus(self, druid: Druid) -> None:
        base_char = Character("Base", druid._attributes, DRUID_CONFIG)
        base_regen = base_char.hp_regen
        expected = int(base_regen * (1.0 + _CONFIG.hp_regen_bonus))
        assert druid.hp_regen == expected

    def test_mana_regen_includes_passive_bonus(self, druid: Druid) -> None:
        base_char = Character("Base", druid._attributes, DRUID_CONFIG)
        base_regen = base_char.mana_regen
        expected = int(base_regen * (1.0 + _CONFIG.mana_regen_bonus))
        assert druid.mana_regen == expected


# --- ShapeShift ---


class TestDruidShapeShift:
    def test_starts_as_humanoid(self, druid: Druid) -> None:
        assert druid.current_form == AnimalForm.HUMANOID

    def test_transform_to_bear(self, druid: Druid) -> None:
        assert druid.transform(AnimalForm.BEAR) is True
        assert druid.current_form == AnimalForm.BEAR

    def test_transform_costs_mana(self, druid: Druid) -> None:
        mana_before = druid.current_mana
        druid.transform(AnimalForm.BEAR)
        assert druid.current_mana == mana_before - _CONFIG.transform_mana_cost

    def test_transform_fails_insufficient_mana(self, druid: Druid) -> None:
        druid.spend_mana(druid.current_mana)
        assert druid.transform(AnimalForm.BEAR) is False
        assert druid.current_form == AnimalForm.HUMANOID

    def test_transform_to_same_form_fails(self, druid: Druid) -> None:
        assert druid.transform(AnimalForm.HUMANOID) is False

    def test_bear_increases_physical_defense(self, druid: Druid) -> None:
        base_def = druid.physical_defense
        druid.transform(AnimalForm.BEAR)
        assert druid.physical_defense > base_def

    def test_bear_decreases_speed(self, druid: Druid) -> None:
        base_speed = druid.speed
        druid.transform(AnimalForm.BEAR)
        assert druid.speed < base_speed

    def test_wolf_increases_physical_attack(self, druid: Druid) -> None:
        base_atk = druid.physical_attack
        druid.transform(AnimalForm.WOLF)
        assert druid.physical_attack > base_atk

    def test_eagle_increases_speed(self, druid: Druid) -> None:
        base_speed = druid.speed
        druid.transform(AnimalForm.EAGLE)
        assert druid.speed > base_speed

    def test_eagle_increases_magical_attack(self, druid: Druid) -> None:
        base_mag = druid.magical_attack
        druid.transform(AnimalForm.EAGLE)
        assert druid.magical_attack > base_mag

    def test_serpent_increases_magical_attack(self, druid: Druid) -> None:
        base_mag = druid.magical_attack
        druid.transform(AnimalForm.SERPENT)
        assert druid.magical_attack > base_mag

    def test_bear_increases_magical_defense(self, druid: Druid) -> None:
        base_mdef = druid.magical_defense
        druid.transform(AnimalForm.BEAR)
        assert druid.magical_defense > base_mdef

    def test_revert_form_returns_to_humanoid(self, druid: Druid) -> None:
        druid.transform(AnimalForm.BEAR)
        druid.revert_form()
        assert druid.current_form == AnimalForm.HUMANOID

    def test_revert_form_free_no_mana_cost(self, druid: Druid) -> None:
        druid.transform(AnimalForm.BEAR)
        mana_after_transform = druid.current_mana
        druid.revert_form()
        assert druid.current_mana == mana_after_transform

    def test_stats_reset_after_revert(self, druid: Druid) -> None:
        base_def = druid.physical_defense
        druid.transform(AnimalForm.BEAR)
        druid.revert_form()
        assert druid.physical_defense == base_def

    def test_transform_from_one_form_to_another(self, druid: Druid) -> None:
        druid.transform(AnimalForm.BEAR)
        assert druid.transform(AnimalForm.WOLF) is True
        assert druid.current_form == AnimalForm.WOLF

    def test_bear_hp_regen_boost(self, druid: Druid) -> None:
        base_regen = druid.hp_regen
        druid.transform(AnimalForm.BEAR)
        assert druid.hp_regen > base_regen


# --- Field Conditions ---


class TestDruidFieldCondition:
    def test_no_field_initially(self, druid: Druid) -> None:
        assert druid.active_field is None

    def test_field_remaining_turns_zero_when_none(self, druid: Druid) -> None:
        assert druid.field_remaining_turns == 0

    def test_create_snow_condition(self, druid: Druid) -> None:
        assert druid.create_field_condition(FieldConditionType.SNOW) is True
        assert druid.active_field == FieldConditionType.SNOW

    def test_create_field_costs_mana(self, druid: Druid) -> None:
        mana_before = druid.current_mana
        druid.create_field_condition(FieldConditionType.SNOW)
        assert druid.current_mana == mana_before - _CONFIG.field_mana_cost

    def test_create_field_fails_insufficient_mana(self, druid: Druid) -> None:
        druid.spend_mana(druid.current_mana)
        assert druid.create_field_condition(FieldConditionType.SNOW) is False
        assert druid.active_field is None

    def test_field_has_duration(self, druid: Druid) -> None:
        druid.create_field_condition(FieldConditionType.SNOW)
        snow_cfg = _FIELDS[FieldConditionType.SNOW]
        assert druid.field_remaining_turns == snow_cfg.default_duration

    def test_tick_decrements_duration(self, druid: Druid) -> None:
        druid.create_field_condition(FieldConditionType.SNOW)
        initial = druid.field_remaining_turns
        druid.tick_field_condition()
        assert druid.field_remaining_turns == initial - 1

    def test_field_auto_clears_at_zero(self, druid: Druid) -> None:
        druid.create_field_condition(FieldConditionType.SANDSTORM)
        duration = _FIELDS[FieldConditionType.SANDSTORM].default_duration
        for _ in range(duration):
            druid.tick_field_condition()
        assert druid.active_field is None
        assert druid.field_remaining_turns == 0

    def test_new_field_replaces_old(self, druid: Druid) -> None:
        druid.create_field_condition(FieldConditionType.SNOW)
        druid.create_field_condition(FieldConditionType.RAIN)
        assert druid.active_field == FieldConditionType.RAIN

    def test_clear_field_condition(self, druid: Druid) -> None:
        druid.create_field_condition(FieldConditionType.FOG)
        druid.clear_field_condition()
        assert druid.active_field is None

    def test_active_field_config_none_when_no_field(
        self, druid: Druid
    ) -> None:
        assert druid.active_field_config is None

    def test_active_field_config_returns_config(self, druid: Druid) -> None:
        druid.create_field_condition(FieldConditionType.SNOW)
        cfg = druid.active_field_config
        assert cfg is not None
        assert cfg.element_resistance == "FIRE"

    def test_tick_on_no_field_is_noop(self, druid: Druid) -> None:
        druid.tick_field_condition()
        assert druid.active_field is None


# --- Healing Bonus ---


class TestDruidHealingBonus:
    def test_heal_is_enhanced(self, druid: Druid) -> None:
        druid.take_damage(50)
        hp_before = druid.current_hp
        druid.heal(20)
        healed = druid.current_hp - hp_before
        # Druid enhances first, then super().heal() applies CON bonus (CON=7)
        enhanced = int(20 * (1.0 + _CONFIG.healing_bonus))
        expected = int(enhanced * (1 + 7 * 0.05))
        assert healed == expected

    def test_heal_still_capped_at_max_hp(self, druid: Druid) -> None:
        druid.take_damage(5)
        druid.heal(9999)
        assert druid.current_hp == druid.max_hp


# --- Form + Field Interaction ---


class TestDruidInteractions:
    def test_bear_form_with_field_active(self, druid: Druid) -> None:
        druid.transform(AnimalForm.BEAR)
        druid.create_field_condition(FieldConditionType.SNOW)
        assert druid.current_form == AnimalForm.BEAR
        assert druid.active_field == FieldConditionType.SNOW

    def test_regen_stacks_form_and_passive(self, druid: Druid) -> None:
        base_char = Character("Base", druid._attributes, DRUID_CONFIG)
        raw_regen = base_char.hp_regen
        druid.transform(AnimalForm.BEAR)
        bear_mod = _FORMS[AnimalForm.BEAR].hp_regen_multiplier
        passive = 1.0 + _CONFIG.hp_regen_bonus
        expected = int(raw_regen * bear_mod * passive)
        assert druid.hp_regen == expected


# --- Level Up ---


class TestDruidLevelUp:
    def test_on_level_up_does_not_crash(self, druid: Druid) -> None:
        druid.on_level_up()

    def test_stats_scale_with_level(self, attrs: Attributes) -> None:
        config_l1 = CharacterConfig(
            class_modifiers=DRUID_MODS,
            threshold_calculator=EMPTY_THRESHOLDS,
            position=Position.FRONT,
            level=1,
        )
        config_l5 = CharacterConfig(
            class_modifiers=DRUID_MODS,
            threshold_calculator=EMPTY_THRESHOLDS,
            position=Position.FRONT,
            level=5,
        )
        d1 = Druid("D1", attrs, config_l1)
        d5 = Druid("D5", attrs, config_l5)
        assert d5.max_hp > d1.max_hp
