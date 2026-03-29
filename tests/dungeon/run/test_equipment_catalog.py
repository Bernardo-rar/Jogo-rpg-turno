"""Testes para EquipmentCatalogs — resolucao de LootDrop para item concreto."""

from __future__ import annotations

from src.core.combat.damage import DamageType
from src.core.combat.targeting import AttackRange
from src.core.items.accessory import Accessory
from src.core.items.accessory_type import AccessoryType
from src.core.items.armor import Armor
from src.core.items.armor_weight import ArmorWeight
from src.core.items.damage_kind import DamageKind
from src.core.items.weapon import Weapon
from src.core.items.weapon_category import WeaponCategory
from src.core.items.weapon_type import WeaponType
from src.dungeon.loot.drop_table import LootDrop
from src.dungeon.run.equipment_catalog import EquipmentCatalogs


def _sample_weapon() -> Weapon:
    return Weapon(
        name="Flame Sword",
        weapon_type=WeaponType.SWORD,
        damage_kind=DamageKind.SLASHING,
        damage_type=DamageType.PHYSICAL,
        weapon_die=8,
        attack_range=AttackRange.MELEE,
        category=WeaponCategory.MARTIAL,
    )


def _sample_armor() -> Armor:
    return Armor(
        name="Studded Leather",
        weight=ArmorWeight.LIGHT,
        ca_bonus=3,
        hp_bonus=0,
        mana_bonus=0,
        physical_defense_bonus=2,
        magical_defense_bonus=1,
    )


def _sample_accessory() -> Accessory:
    return Accessory(
        name="Ring of Power",
        accessory_type=AccessoryType.RING,
        stat_bonuses=(),
    )


def _make_catalogs() -> EquipmentCatalogs:
    return EquipmentCatalogs(
        weapons={"flame_sword": _sample_weapon()},
        armors={"studded_leather": _sample_armor()},
        accessories={"ring_of_power": _sample_accessory()},
    )


class TestResolveWeaponDrop:

    def test_resolve_weapon_drop(self) -> None:
        """Resolves weapon LootDrop to Weapon object."""
        catalogs = _make_catalogs()
        drop = LootDrop(item_type="weapon", item_id="flame_sword")
        result = catalogs.resolve_drop(drop)
        assert isinstance(result, Weapon)
        assert result.name == "Flame Sword"


class TestResolveArmorDrop:

    def test_resolve_armor_drop(self) -> None:
        """Resolves armor LootDrop to Armor object."""
        catalogs = _make_catalogs()
        drop = LootDrop(item_type="armor", item_id="studded_leather")
        result = catalogs.resolve_drop(drop)
        assert isinstance(result, Armor)
        assert result.name == "Studded Leather"


class TestResolveAccessoryDrop:

    def test_resolve_accessory_drop(self) -> None:
        """Resolves accessory LootDrop to Accessory object."""
        catalogs = _make_catalogs()
        drop = LootDrop(item_type="accessory", item_id="ring_of_power")
        result = catalogs.resolve_drop(drop)
        assert isinstance(result, Accessory)
        assert result.name == "Ring of Power"


class TestResolveUnknownReturnsNone:

    def test_resolve_unknown_id_returns_none(self) -> None:
        """Unknown item_id returns None."""
        catalogs = _make_catalogs()
        drop = LootDrop(item_type="weapon", item_id="nonexistent")
        result = catalogs.resolve_drop(drop)
        assert result is None


class TestResolveConsumableReturnsNone:

    def test_resolve_consumable_returns_none(self) -> None:
        """Consumable item_type returns None."""
        catalogs = _make_catalogs()
        drop = LootDrop(item_type="consumable", item_id="health_potion")
        result = catalogs.resolve_drop(drop)
        assert result is None
