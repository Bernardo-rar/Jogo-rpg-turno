"""Testes de integracao: Accessory + Character stats."""

from __future__ import annotations

import pytest

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_modifiers import ClassModifiers
from src.core.characters.position import Position
from src.core.effects.modifiable_stat import ModifiableStat
from src.core.items.accessory import Accessory
from src.core.items.accessory_type import AccessoryType
from src.core.items.stat_bonus import StatBonus

MODS = ClassModifiers(
    hit_dice=10,
    mod_hp_flat=0,
    mod_hp_mult=6,
    mana_multiplier=6,
    mod_atk_physical=6,
    mod_atk_magical=4,
    mod_def_physical=5,
    mod_def_magical=4,
    regen_hp_mod=4,
    regen_mana_mod=3,
)

EMPTY_THRESHOLDS = ThresholdCalculator({})

RING_DEF = Accessory(
    name="Iron Ring",
    accessory_type=AccessoryType.RING,
    stat_bonuses=(
        StatBonus(stat=ModifiableStat.PHYSICAL_DEFENSE, flat=5),
    ),
)

AMULET_SPEED = Accessory(
    name="Cloak of Speed",
    accessory_type=AccessoryType.CLOAK,
    stat_bonuses=(
        StatBonus(stat=ModifiableStat.SPEED, flat=3),
    ),
)

RING_MAGIC = Accessory(
    name="Ring of Magic",
    accessory_type=AccessoryType.RING,
    stat_bonuses=(
        StatBonus(stat=ModifiableStat.MAGICAL_DEFENSE, flat=4),
        StatBonus(stat=ModifiableStat.MANA_REGEN, flat=2),
    ),
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


class TestAccessoryEquipUnequip:
    def test_no_accessories_by_default(self, attrs: Attributes, config: CharacterConfig) -> None:
        char = Character("Test", attrs, config)
        assert char.accessories == ()

    def test_equip_accessory(self, attrs: Attributes, config: CharacterConfig) -> None:
        char = Character("Test", attrs, config)
        assert char.equip_accessory(RING_DEF) is True
        assert RING_DEF in char.accessories

    def test_unequip_accessory(self, attrs: Attributes, config: CharacterConfig) -> None:
        char = Character("Test", attrs, config)
        char.equip_accessory(RING_DEF)
        assert char.unequip_accessory(RING_DEF) is True
        assert char.accessories == ()

    def test_unequip_missing_returns_false(self, attrs: Attributes, config: CharacterConfig) -> None:
        char = Character("Test", attrs, config)
        assert char.unequip_accessory(RING_DEF) is False

    def test_config_accessories_applied(self, attrs: Attributes) -> None:
        config = CharacterConfig(
            class_modifiers=MODS,
            threshold_calculator=EMPTY_THRESHOLDS,
            accessories=(RING_DEF,),
        )
        char = Character("Test", attrs, config)
        assert RING_DEF in char.accessories


class TestAccessorySlotLimit:
    def test_cannot_exceed_max_slots(self, attrs: Attributes, config: CharacterConfig) -> None:
        char = Character("Test", attrs, config)
        max_slots = char.max_accessory_slots
        for _ in range(max_slots):
            char.equip_accessory(RING_DEF)
        assert char.equip_accessory(AMULET_SPEED) is False

    def test_max_slots_is_at_least_two(self, attrs: Attributes, config: CharacterConfig) -> None:
        char = Character("Test", attrs, config)
        assert char.max_accessory_slots >= 2


class TestAccessoryStatBonuses:
    def test_physical_defense_bonus(self, attrs: Attributes, config: CharacterConfig) -> None:
        char = Character("Test", attrs, config)
        base_def = char.physical_defense
        char.equip_accessory(RING_DEF)
        assert char.physical_defense == base_def + 5

    def test_speed_bonus(self, attrs: Attributes, config: CharacterConfig) -> None:
        char = Character("Test", attrs, config)
        base_speed = char.speed
        char.equip_accessory(AMULET_SPEED)
        assert char.speed == base_speed + 3

    def test_multiple_accessories_stack(self, attrs: Attributes, config: CharacterConfig) -> None:
        char = Character("Test", attrs, config)
        base_def = char.physical_defense
        char.equip_accessory(RING_DEF)
        char.equip_accessory(RING_MAGIC)
        assert char.physical_defense == base_def + 5

    def test_unequip_removes_bonus(self, attrs: Attributes, config: CharacterConfig) -> None:
        char = Character("Test", attrs, config)
        base_def = char.physical_defense
        char.equip_accessory(RING_DEF)
        char.unequip_accessory(RING_DEF)
        assert char.physical_defense == base_def
