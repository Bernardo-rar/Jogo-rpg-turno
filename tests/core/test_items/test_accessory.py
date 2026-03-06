"""Testes para Accessory frozen dataclass."""

from __future__ import annotations

import pytest

from src.core.effects.modifiable_stat import ModifiableStat
from src.core.items.accessory import Accessory
from src.core.items.accessory_type import AccessoryType
from src.core.items.item_rarity import ItemRarity
from src.core.items.stat_bonus import StatBonus


class TestAccessoryCreation:
    def test_create_basic(self) -> None:
        bonus = StatBonus(stat=ModifiableStat.PHYSICAL_DEFENSE, flat=3)
        acc = Accessory(
            name="Iron Ring",
            accessory_type=AccessoryType.RING,
            stat_bonuses=(bonus,),
        )
        assert acc.name == "Iron Ring"
        assert acc.accessory_type == AccessoryType.RING
        assert len(acc.stat_bonuses) == 1

    def test_defaults(self) -> None:
        acc = Accessory(
            name="Ring",
            accessory_type=AccessoryType.RING,
            stat_bonuses=(),
        )
        assert acc.rarity == ItemRarity.COMMON
        assert acc.cha_requirement == 0

    def test_is_frozen(self) -> None:
        acc = Accessory(
            name="Ring",
            accessory_type=AccessoryType.RING,
            stat_bonuses=(),
        )
        with pytest.raises(AttributeError):
            acc.name = "X"  # type: ignore[misc]

    def test_multiple_stat_bonuses(self) -> None:
        bonuses = (
            StatBonus(stat=ModifiableStat.MAGICAL_DEFENSE, flat=5),
            StatBonus(stat=ModifiableStat.MANA_REGEN, flat=2),
        )
        acc = Accessory(
            name="Amulet of Wisdom",
            accessory_type=AccessoryType.AMULET,
            stat_bonuses=bonuses,
        )
        assert len(acc.stat_bonuses) == 2


class TestAccessoryFromDict:
    def test_from_dict_basic(self) -> None:
        data: dict[str, object] = {
            "name": "Iron Ring",
            "accessory_type": "RING",
            "stat_bonuses": [{"stat": "PHYSICAL_DEFENSE", "flat": 3}],
        }
        acc = Accessory.from_dict(data)
        assert acc.name == "Iron Ring"
        assert acc.accessory_type == AccessoryType.RING
        assert acc.stat_bonuses[0].flat == 3

    def test_from_dict_with_rarity(self) -> None:
        data: dict[str, object] = {
            "name": "Amulet",
            "accessory_type": "AMULET",
            "stat_bonuses": [{"stat": "MAGICAL_DEFENSE", "flat": 5}],
            "rarity": "UNCOMMON",
            "cha_requirement": 12,
        }
        acc = Accessory.from_dict(data)
        assert acc.rarity == ItemRarity.UNCOMMON
        assert acc.cha_requirement == 12

    def test_from_dict_multiple_bonuses(self) -> None:
        data: dict[str, object] = {
            "name": "Amulet",
            "accessory_type": "AMULET",
            "stat_bonuses": [
                {"stat": "MAGICAL_DEFENSE", "flat": 5},
                {"stat": "MANA_REGEN", "flat": 2},
            ],
        }
        acc = Accessory.from_dict(data)
        assert len(acc.stat_bonuses) == 2

    def test_from_dict_invalid_type_raises(self) -> None:
        data: dict[str, object] = {
            "name": "Bad",
            "accessory_type": "SWORD",
            "stat_bonuses": [],
        }
        with pytest.raises(KeyError):
            Accessory.from_dict(data)
