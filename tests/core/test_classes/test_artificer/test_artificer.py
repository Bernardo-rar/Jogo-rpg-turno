from __future__ import annotations

import pytest

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_modifiers import ClassModifiers
from src.core.characters.position import Position
from src.core.classes.artificer.artificer import Artificer
from src.core.classes.artificer.artificer_config import load_artificer_config
from src.core.classes.artificer.tech_suit import TechSuit, load_suit_config

_CONFIG = load_artificer_config()
_SUIT = load_suit_config()

ARTIFICER_MODS = ClassModifiers(
    hit_dice=8,
    vida_mod=0,
    mod_hp=6,
    mana_multiplier=10,
    mod_atk_physical=4,
    mod_atk_magical=8,
    mod_def_physical=4,
    mod_def_magical=5,
    regen_hp_mod=3,
    regen_mana_mod=6,
)

EMPTY_THRESHOLDS = ThresholdCalculator({})
ARTIFICER_CONFIG = CharacterConfig(
    class_modifiers=ARTIFICER_MODS,
    threshold_calculator=EMPTY_THRESHOLDS,
    position=Position.BACK,
)


@pytest.fixture
def attrs() -> Attributes:
    return Attributes({
        AttributeType.STRENGTH: 4,
        AttributeType.DEXTERITY: 5,
        AttributeType.CONSTITUTION: 5,
        AttributeType.INTELLIGENCE: 12,
        AttributeType.WISDOM: 6,
        AttributeType.CHARISMA: 4,
        AttributeType.MIND: 8,
    })


@pytest.fixture
def artificer(attrs: Attributes) -> Artificer:
    return Artificer("Tesla", attrs, ARTIFICER_CONFIG)


# --- LSP ---


class TestArtificerIsCharacter:
    def test_is_instance_of_character(self, artificer: Artificer) -> None:
        assert isinstance(artificer, Character)

    def test_has_name(self, artificer: Artificer) -> None:
        assert artificer.name == "Tesla"

    def test_has_hp(self, artificer: Artificer) -> None:
        assert artificer.max_hp > 0

    def test_has_mana(self, artificer: Artificer) -> None:
        assert artificer.max_mana > 0

    def test_take_damage_works(self, artificer: Artificer) -> None:
        actual = artificer.take_damage(10)
        assert actual > 0
        assert artificer.current_hp < artificer.max_hp

    def test_is_alive(self, artificer: Artificer) -> None:
        assert artificer.is_alive

    def test_heal_works(self, artificer: Artificer) -> None:
        artificer.take_damage(20)
        healed = artificer.heal(10)
        assert healed > 0


# --- Stats ---


class TestArtificerStats:
    def test_max_hp_formula(
        self, artificer: Artificer, attrs: Attributes
    ) -> None:
        con = attrs.get(AttributeType.CONSTITUTION)
        expected = ((8 + con + 0) * 2) * 6
        assert artificer.max_hp == expected

    def test_max_mana_formula(
        self, artificer: Artificer, attrs: Attributes
    ) -> None:
        mind = attrs.get(AttributeType.MIND)
        expected = 10 * mind * 10
        assert artificer.max_mana == expected

    def test_physical_attack(self, artificer: Artificer) -> None:
        assert artificer.physical_attack > 0

    def test_magical_attack(self, artificer: Artificer) -> None:
        assert artificer.magical_attack > 0

    def test_physical_defense(self, artificer: Artificer) -> None:
        assert artificer.physical_defense > 0

    def test_magical_defense(self, artificer: Artificer) -> None:
        assert artificer.magical_defense > 0


# --- TechSuit Integration ---


class TestArtificerTechSuit:
    def test_has_tech_suit(self, artificer: Artificer) -> None:
        assert artificer.tech_suit is not None

    def test_magical_attack_boosted_at_full_mana(
        self, artificer: Artificer
    ) -> None:
        base_char = Character(
            "Base", artificer._attributes, ARTIFICER_CONFIG
        )
        ratio = TechSuit.mana_ratio(
            artificer.current_mana, artificer.max_mana
        )
        expected = int(
            base_char.magical_attack
            * artificer.tech_suit.atk_multiplier(ratio)
        )
        assert artificer.magical_attack == expected

    def test_magical_attack_drops_with_mana(
        self, artificer: Artificer
    ) -> None:
        full_atk = artificer.magical_attack
        artificer.spend_mana(artificer.max_mana)
        assert artificer.magical_attack < full_atk

    def test_physical_defense_boosted_at_full_mana(
        self, artificer: Artificer
    ) -> None:
        base_char = Character(
            "Base", artificer._attributes, ARTIFICER_CONFIG
        )
        ratio = TechSuit.mana_ratio(
            artificer.current_mana, artificer.max_mana
        )
        expected = int(
            base_char.physical_defense
            * artificer.tech_suit.phys_def_multiplier(ratio)
        )
        assert artificer.physical_defense == expected

    def test_physical_defense_drops_with_mana(
        self, artificer: Artificer
    ) -> None:
        full_def = artificer.physical_defense
        artificer.spend_mana(artificer.max_mana)
        assert artificer.physical_defense < full_def

    def test_magical_defense_boosted_at_full_mana(
        self, artificer: Artificer
    ) -> None:
        base_char = Character(
            "Base", artificer._attributes, ARTIFICER_CONFIG
        )
        base_mag_def = base_char.magical_defense
        passive = 1.0 + _CONFIG.magical_defense_bonus
        ratio = TechSuit.mana_ratio(
            artificer.current_mana, artificer.max_mana
        )
        suit_mult = artificer.tech_suit.mag_def_multiplier(ratio)
        expected = int(base_mag_def * passive * suit_mult)
        assert artificer.magical_defense == expected

    def test_magical_defense_drops_with_mana(
        self, artificer: Artificer
    ) -> None:
        full_def = artificer.magical_defense
        artificer.spend_mana(artificer.max_mana)
        assert artificer.magical_defense < full_def


# --- Passivas ---


class TestArtificerPassives:
    def test_mana_regen_has_bonus(self, artificer: Artificer) -> None:
        base_char = Character(
            "Base", artificer._attributes, ARTIFICER_CONFIG
        )
        expected = int(
            base_char.mana_regen * (1.0 + _CONFIG.mana_regen_bonus)
        )
        assert artificer.mana_regen == expected

    def test_scroll_potentiation(self, artificer: Artificer) -> None:
        assert artificer.scroll_potentiation == pytest.approx(
            _CONFIG.scroll_potentiation
        )


# --- Level Up ---


class TestArtificerLevelUp:
    def test_on_level_up_no_error(self, artificer: Artificer) -> None:
        artificer.on_level_up()

    def test_stats_scale_with_level(self, attrs: Attributes) -> None:
        config_l1 = CharacterConfig(
            class_modifiers=ARTIFICER_MODS,
            threshold_calculator=EMPTY_THRESHOLDS,
            position=Position.BACK,
            level=1,
        )
        config_l5 = CharacterConfig(
            class_modifiers=ARTIFICER_MODS,
            threshold_calculator=EMPTY_THRESHOLDS,
            position=Position.BACK,
            level=5,
        )
        a1 = Artificer("A1", attrs, config_l1)
        a5 = Artificer("A5", attrs, config_l5)
        assert a5.max_hp > a1.max_hp
