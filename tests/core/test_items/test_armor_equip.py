"""Testes de integracao: Armor + Character stats."""

from __future__ import annotations

import pytest

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_modifiers import ClassModifiers
from src.core.characters.position import Position
from src.core.items.armor import Armor
from src.core.items.armor_weight import ArmorWeight

MODS = ClassModifiers(
    hit_dice=10,
    vida_mod=0,
    mod_hp=6,
    mana_multiplier=6,
    mod_atk_physical=6,
    mod_atk_magical=4,
    mod_def_physical=5,
    mod_def_magical=4,
    regen_hp_mod=4,
    regen_mana_mod=3,
)

EMPTY_THRESHOLDS = ThresholdCalculator({})

PLATE = Armor(
    name="Plate Armor",
    weight=ArmorWeight.HEAVY,
    ca_bonus=6,
    hp_bonus=30,
    mana_bonus=0,
    physical_defense_bonus=4,
    magical_defense_bonus=2,
)

MAGE_ROBES = Armor(
    name="Mage Robes",
    weight=ArmorWeight.LIGHT,
    ca_bonus=1,
    hp_bonus=0,
    mana_bonus=50,
    physical_defense_bonus=0,
    magical_defense_bonus=3,
)


@pytest.fixture
def attrs() -> Attributes:
    return Attributes({
        AttributeType.STRENGTH: 8,
        AttributeType.DEXTERITY: 6,
        AttributeType.CONSTITUTION: 8,
        AttributeType.INTELLIGENCE: 5,
        AttributeType.WISDOM: 5,
        AttributeType.CHARISMA: 5,
        AttributeType.MIND: 5,
    })


@pytest.fixture
def config() -> CharacterConfig:
    return CharacterConfig(
        class_modifiers=MODS,
        threshold_calculator=EMPTY_THRESHOLDS,
        position=Position.FRONT,
    )


class TestArmorEquipUnequip:
    def test_no_armor_by_default(self, attrs: Attributes, config: CharacterConfig) -> None:
        char = Character("Test", attrs, config)
        assert char.armor is None

    def test_equip_armor(self, attrs: Attributes, config: CharacterConfig) -> None:
        char = Character("Test", attrs, config)
        char.equip_armor(PLATE)
        assert char.armor == PLATE

    def test_unequip_returns_old(self, attrs: Attributes, config: CharacterConfig) -> None:
        char = Character("Test", attrs, config)
        char.equip_armor(PLATE)
        old = char.unequip_armor()
        assert old == PLATE
        assert char.armor is None

    def test_unequip_when_empty_returns_none(self, attrs: Attributes, config: CharacterConfig) -> None:
        char = Character("Test", attrs, config)
        assert char.unequip_armor() is None

    def test_config_armor_applied(self, attrs: Attributes) -> None:
        config = CharacterConfig(
            class_modifiers=MODS,
            threshold_calculator=EMPTY_THRESHOLDS,
            armor=PLATE,
        )
        char = Character("Test", attrs, config)
        assert char.armor == PLATE


class TestArmorStatBonuses:
    def test_hp_bonus(self, attrs: Attributes, config: CharacterConfig) -> None:
        char = Character("Test", attrs, config)
        base_hp = char.max_hp
        char.equip_armor(PLATE)
        assert char.max_hp == base_hp + PLATE.hp_bonus

    def test_mana_bonus(self, attrs: Attributes, config: CharacterConfig) -> None:
        char = Character("Test", attrs, config)
        base_mana = char.max_mana
        char.equip_armor(MAGE_ROBES)
        assert char.max_mana == base_mana + MAGE_ROBES.mana_bonus

    def test_physical_defense_bonus(self, attrs: Attributes, config: CharacterConfig) -> None:
        char = Character("Test", attrs, config)
        base_def = char.physical_defense
        char.equip_armor(PLATE)
        assert char.physical_defense == base_def + PLATE.physical_defense_bonus

    def test_magical_defense_bonus(self, attrs: Attributes, config: CharacterConfig) -> None:
        char = Character("Test", attrs, config)
        base_def = char.magical_defense
        char.equip_armor(PLATE)
        assert char.magical_defense == base_def + PLATE.magical_defense_bonus

    def test_unequip_removes_bonus(self, attrs: Attributes, config: CharacterConfig) -> None:
        char = Character("Test", attrs, config)
        base_hp = char.max_hp
        char.equip_armor(PLATE)
        char.unequip_armor()
        assert char.max_hp == base_hp


class TestArmorClass:
    def test_armor_class_without_armor(self, attrs: Attributes, config: CharacterConfig) -> None:
        char = Character("Test", attrs, config)
        dex = attrs.get(AttributeType.DEXTERITY)
        expected = 0 + dex + config.level
        assert char.armor_class == expected

    def test_armor_class_with_armor(self, attrs: Attributes, config: CharacterConfig) -> None:
        char = Character("Test", attrs, config)
        char.equip_armor(PLATE)
        dex = attrs.get(AttributeType.DEXTERITY)
        expected = PLATE.ca_bonus + dex + config.level
        assert char.armor_class == expected
