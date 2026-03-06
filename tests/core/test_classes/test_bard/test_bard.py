from __future__ import annotations

import pytest

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_modifiers import ClassModifiers
from src.core.characters.position import Position
from src.core.classes.bard.bard import Bard
from src.core.classes.bard.bard_config import load_bard_config

_CONFIG = load_bard_config()

BARD_MODS = ClassModifiers(
    hit_dice=8,
    vida_mod=0,
    mod_hp=6,
    mana_multiplier=8,
    mod_atk_physical=4,
    mod_atk_magical=6,
    mod_def_physical=4,
    mod_def_magical=5,
    regen_hp_mod=4,
    regen_mana_mod=4,
)

EMPTY_THRESHOLDS = ThresholdCalculator({})
BARD_CONFIG = CharacterConfig(
    class_modifiers=BARD_MODS,
    threshold_calculator=EMPTY_THRESHOLDS,
    position=Position.BACK,
)


@pytest.fixture
def attrs() -> Attributes:
    return Attributes({
        AttributeType.STRENGTH: 4,
        AttributeType.DEXTERITY: 12,
        AttributeType.CONSTITUTION: 5,
        AttributeType.INTELLIGENCE: 6,
        AttributeType.WISDOM: 5,
        AttributeType.CHARISMA: 10,
        AttributeType.MIND: 5,
    })


@pytest.fixture
def bard(attrs: Attributes) -> Bard:
    return Bard("Melody", attrs, BARD_CONFIG)


# --- LSP ---


class TestBardIsCharacter:
    def test_is_instance_of_character(self, bard: Bard) -> None:
        assert isinstance(bard, Character)

    def test_has_name(self, bard: Bard) -> None:
        assert bard.name == "Melody"

    def test_has_hp(self, bard: Bard) -> None:
        assert bard.max_hp > 0

    def test_has_mana(self, bard: Bard) -> None:
        assert bard.max_mana > 0

    def test_take_damage_works(self, bard: Bard) -> None:
        actual = bard.take_damage(10)
        assert actual > 0
        assert bard.current_hp < bard.max_hp

    def test_is_alive(self, bard: Bard) -> None:
        assert bard.is_alive

    def test_heal_works(self, bard: Bard) -> None:
        bard.take_damage(20)
        healed = bard.heal(10)
        assert healed > 0


# --- Stats ---


class TestBardStats:
    def test_max_hp_formula(self, bard: Bard, attrs: Attributes) -> None:
        con = attrs.get(AttributeType.CONSTITUTION)
        expected = ((8 + con + 0) * 2) * 6
        assert bard.max_hp == expected

    def test_max_mana_formula(self, bard: Bard, attrs: Attributes) -> None:
        mind = attrs.get(AttributeType.MIND)
        expected = 8 * mind * 10
        assert bard.max_mana == expected

    def test_physical_attack(self, bard: Bard) -> None:
        assert bard.physical_attack > 0

    def test_magical_attack(self, bard: Bard) -> None:
        assert bard.magical_attack > 0

    def test_physical_defense(self, bard: Bard) -> None:
        assert bard.physical_defense > 0

    def test_magical_defense(self, bard: Bard) -> None:
        assert bard.magical_defense > 0


# --- Groove Integration ---


class TestBardGroove:
    def test_groove_starts_at_zero(self, bard: Bard) -> None:
        assert bard.groove.stacks == 0

    def test_register_skill_use_gains_stacks(self, bard: Bard) -> None:
        bard.register_skill_use()
        assert bard.groove.stacks == 1

    def test_tick_groove_decays_stacks(self, bard: Bard) -> None:
        bard.register_skill_use()
        bard.register_skill_use()
        bard.tick_groove()
        assert bard.groove.stacks == 1

    def test_groove_buff_bonus(self, bard: Bard) -> None:
        bard.register_skill_use()
        assert bard.groove_buff_bonus > 0

    def test_groove_debuff_bonus(self, bard: Bard) -> None:
        bard.register_skill_use()
        assert bard.groove_debuff_bonus > 0

    def test_groove_crit_bonus(self, bard: Bard) -> None:
        bard.register_skill_use()
        assert bard.groove_crit_bonus > 0


# --- Crescendo Integration ---


class TestBardCrescendo:
    def test_crescendo_at_max_stacks(self, bard: Bard) -> None:
        for _ in range(10):
            bard.register_skill_use()
        assert bard.groove.trigger_crescendo() is True
        assert bard.groove.is_crescendo is True

    def test_tick_groove_also_ticks_crescendo(self, bard: Bard) -> None:
        for _ in range(10):
            bard.register_skill_use()
        bard.groove.trigger_crescendo()
        bard.tick_groove()
        bard.tick_groove()
        assert bard.groove.is_crescendo is False


# --- Passivas ---


class TestBardPassives:
    def test_buff_effectiveness_bonus(self, bard: Bard) -> None:
        assert bard.buff_effectiveness_bonus == pytest.approx(
            _CONFIG.buff_effectiveness_bonus
        )

    def test_debuff_effectiveness_bonus(self, bard: Bard) -> None:
        assert bard.debuff_effectiveness_bonus == pytest.approx(
            _CONFIG.debuff_effectiveness_bonus
        )

    def test_extra_bonus_actions(self, bard: Bard) -> None:
        assert bard.extra_bonus_actions == _CONFIG.extra_bonus_actions


# --- Speed ---


class TestBardSpeed:
    def test_speed_has_passive_bonus(self, bard: Bard) -> None:
        base_char = Character("Base", bard._attributes, BARD_CONFIG)
        base_speed = base_char.speed
        passive = int(base_speed * _CONFIG.speed_bonus_pct)
        assert bard.speed == base_speed + passive

    def test_speed_with_groove_stacks(self, bard: Bard) -> None:
        speed_before = bard.speed
        for _ in range(10):
            bard.register_skill_use()
        assert bard.speed > speed_before

    def test_speed_groove_bonus_scales(self, bard: Bard) -> None:
        base_char = Character("Base", bard._attributes, BARD_CONFIG)
        base_speed = base_char.speed
        passive = int(base_speed * _CONFIG.speed_bonus_pct)
        for _ in range(5):
            bard.register_skill_use()
        groove_bonus = int(base_speed * bard.groove.speed_bonus)
        assert bard.speed == base_speed + passive + groove_bonus


# --- Level Up ---


class TestBardLevelUp:
    def test_on_level_up_no_error(self, bard: Bard) -> None:
        bard.on_level_up()

    def test_stats_scale_with_level(self, attrs: Attributes) -> None:
        config_l1 = CharacterConfig(
            class_modifiers=BARD_MODS,
            threshold_calculator=EMPTY_THRESHOLDS,
            position=Position.BACK,
            level=1,
        )
        config_l5 = CharacterConfig(
            class_modifiers=BARD_MODS,
            threshold_calculator=EMPTY_THRESHOLDS,
            position=Position.BACK,
            level=5,
        )
        b1 = Bard("B1", attrs, config_l1)
        b5 = Bard("B5", attrs, config_l5)
        assert b5.max_hp > b1.max_hp
