"""Testes para weapon_loader (carrega armas do JSON)."""

import pytest

from src.core.combat.damage import DamageType
from src.core.combat.targeting import AttackRange
from src.core.elements.element_type import ElementType
from src.core.items.weapon import Weapon
from src.core.items.weapon_category import WeaponCategory
from src.core.items.weapon_loader import load_weapons
from src.core.items.weapon_rarity import WeaponRarity
from src.core.items.weapon_type import WeaponType

EXPECTED_WEAPON_COUNT = 15


class TestLoadWeapons:

    def test_returns_dict(self) -> None:
        weapons = load_weapons()
        assert isinstance(weapons, dict)

    def test_has_expected_count(self) -> None:
        weapons = load_weapons()
        assert len(weapons) == EXPECTED_WEAPON_COUNT

    def test_all_values_are_weapon_instances(self) -> None:
        weapons = load_weapons()
        for w in weapons.values():
            assert isinstance(w, Weapon)

    def test_short_sword_is_physical_melee_simple(self) -> None:
        weapons = load_weapons()
        w = weapons["short_sword"]
        assert w.damage_type == DamageType.PHYSICAL
        assert w.attack_range == AttackRange.MELEE
        assert w.category == WeaponCategory.SIMPLE

    def test_arcane_staff_is_magical_ranged(self) -> None:
        weapons = load_weapons()
        w = weapons["arcane_staff"]
        assert w.damage_type == DamageType.MAGICAL
        assert w.attack_range == AttackRange.RANGED
        assert w.category == WeaponCategory.MAGICAL

    def test_flame_sword_has_fire_element(self) -> None:
        weapons = load_weapons()
        w = weapons["flame_sword"]
        assert w.element == ElementType.FIRE
        assert w.rarity == WeaponRarity.UNCOMMON

    def test_common_weapons_have_no_element(self) -> None:
        weapons = load_weapons()
        common = [w for w in weapons.values() if w.rarity == WeaponRarity.COMMON]
        assert all(w.element is None for w in common)

    def test_invalid_path_raises(self) -> None:
        with pytest.raises(FileNotFoundError):
            load_weapons("data/weapons/nonexistent.json")
