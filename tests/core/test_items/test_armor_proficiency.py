"""Testes para armor_proficiency."""

from __future__ import annotations

from src.core.items.armor import Armor
from src.core.items.armor_proficiency import (
    BARBARIAN_ARMOR_PROF,
    BARD_ARMOR_PROF,
    FIGHTER_ARMOR_PROF,
    MAGE_ARMOR_PROF,
    PALADIN_ARMOR_PROF,
    can_equip_armor,
)
from src.core.items.armor_weight import ArmorWeight
from src.core.items.item_rarity import ItemRarity


def _make_armor(weight: ArmorWeight) -> Armor:
    return Armor(
        name="Test", weight=weight,
        ca_bonus=0, hp_bonus=0, mana_bonus=0,
        physical_defense_bonus=0, magical_defense_bonus=0,
    )


class TestArmorProficiency:
    def test_fighter_can_equip_heavy(self) -> None:
        assert can_equip_armor(_make_armor(ArmorWeight.HEAVY), FIGHTER_ARMOR_PROF)

    def test_fighter_can_equip_light(self) -> None:
        assert can_equip_armor(_make_armor(ArmorWeight.LIGHT), FIGHTER_ARMOR_PROF)

    def test_mage_can_equip_light(self) -> None:
        assert can_equip_armor(_make_armor(ArmorWeight.LIGHT), MAGE_ARMOR_PROF)

    def test_mage_cannot_equip_medium(self) -> None:
        assert not can_equip_armor(_make_armor(ArmorWeight.MEDIUM), MAGE_ARMOR_PROF)

    def test_mage_cannot_equip_heavy(self) -> None:
        assert not can_equip_armor(_make_armor(ArmorWeight.HEAVY), MAGE_ARMOR_PROF)

    def test_paladin_can_equip_all(self) -> None:
        for weight in ArmorWeight:
            assert can_equip_armor(_make_armor(weight), PALADIN_ARMOR_PROF)

    def test_barbarian_can_equip_medium(self) -> None:
        assert can_equip_armor(_make_armor(ArmorWeight.MEDIUM), BARBARIAN_ARMOR_PROF)

    def test_bard_light_only(self) -> None:
        assert can_equip_armor(_make_armor(ArmorWeight.LIGHT), BARD_ARMOR_PROF)
        assert not can_equip_armor(_make_armor(ArmorWeight.HEAVY), BARD_ARMOR_PROF)
