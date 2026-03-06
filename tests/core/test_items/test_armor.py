"""Testes para Armor frozen dataclass."""

from __future__ import annotations

import pytest

from src.core.items.armor import Armor
from src.core.items.armor_weight import ArmorWeight
from src.core.items.item_rarity import ItemRarity


class TestArmorCreation:
    def test_create_basic_armor(self) -> None:
        armor = Armor(
            name="Chain Mail",
            weight=ArmorWeight.MEDIUM,
            ca_bonus=4,
            hp_bonus=10,
            mana_bonus=0,
            physical_defense_bonus=2,
            magical_defense_bonus=1,
        )
        assert armor.name == "Chain Mail"
        assert armor.weight == ArmorWeight.MEDIUM
        assert armor.ca_bonus == 4

    def test_defaults(self) -> None:
        armor = Armor(
            name="Leather",
            weight=ArmorWeight.LIGHT,
            ca_bonus=2,
            hp_bonus=0,
            mana_bonus=0,
            physical_defense_bonus=1,
            magical_defense_bonus=0,
        )
        assert armor.rarity == ItemRarity.COMMON
        assert armor.cha_requirement == 0

    def test_is_frozen(self) -> None:
        armor = Armor(
            name="Plate",
            weight=ArmorWeight.HEAVY,
            ca_bonus=6,
            hp_bonus=30,
            mana_bonus=0,
            physical_defense_bonus=4,
            magical_defense_bonus=2,
        )
        with pytest.raises(AttributeError):
            armor.ca_bonus = 10  # type: ignore[misc]


class TestArmorFromDict:
    def test_from_dict_basic(self) -> None:
        data: dict[str, object] = {
            "name": "Scale Mail",
            "weight": "MEDIUM",
            "ca_bonus": 3,
            "hp_bonus": 5,
            "mana_bonus": 0,
            "physical_defense_bonus": 2,
            "magical_defense_bonus": 0,
        }
        armor = Armor.from_dict(data)
        assert armor.name == "Scale Mail"
        assert armor.weight == ArmorWeight.MEDIUM
        assert armor.ca_bonus == 3
        assert armor.hp_bonus == 5
        assert armor.rarity == ItemRarity.COMMON

    def test_from_dict_with_rarity(self) -> None:
        data: dict[str, object] = {
            "name": "Mage Robes",
            "weight": "LIGHT",
            "ca_bonus": 1,
            "hp_bonus": 0,
            "mana_bonus": 50,
            "physical_defense_bonus": 0,
            "magical_defense_bonus": 3,
            "rarity": "UNCOMMON",
            "cha_requirement": 12,
        }
        armor = Armor.from_dict(data)
        assert armor.rarity == ItemRarity.UNCOMMON
        assert armor.cha_requirement == 12
        assert armor.mana_bonus == 50

    def test_from_dict_invalid_weight_raises(self) -> None:
        data: dict[str, object] = {
            "name": "Bad",
            "weight": "SUPER_HEAVY",
            "ca_bonus": 0,
            "hp_bonus": 0,
            "mana_bonus": 0,
            "physical_defense_bonus": 0,
            "magical_defense_bonus": 0,
        }
        with pytest.raises(KeyError):
            Armor.from_dict(data)
