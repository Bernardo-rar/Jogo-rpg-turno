"""Testes para Weapon frozen dataclass."""

import pytest

from src.core.combat.damage import DamageType
from src.core.combat.targeting import AttackRange
from src.core.elements.element_type import ElementType
from src.core.items.damage_kind import DamageKind
from src.core.items.weapon import Weapon
from src.core.items.weapon_category import WeaponCategory
from src.core.items.weapon_rarity import WeaponRarity
from src.core.items.weapon_type import WeaponType


def _make_longsword() -> Weapon:
    return Weapon(
        name="Longsword",
        weapon_type=WeaponType.SWORD,
        damage_kind=DamageKind.SLASHING,
        damage_type=DamageType.PHYSICAL,
        weapon_die=8,
        attack_range=AttackRange.MELEE,
        category=WeaponCategory.MARTIAL,
    )


class TestWeaponCreation:

    def test_create_physical_weapon(self) -> None:
        w = _make_longsword()
        assert w.name == "Longsword"
        assert w.weapon_type == WeaponType.SWORD
        assert w.damage_kind == DamageKind.SLASHING
        assert w.damage_type == DamageType.PHYSICAL
        assert w.weapon_die == 8

    def test_create_magical_weapon(self) -> None:
        w = Weapon(
            name="Arcane Staff",
            weapon_type=WeaponType.STAFF,
            damage_kind=DamageKind.BLUDGEONING,
            damage_type=DamageType.MAGICAL,
            weapon_die=8,
            attack_range=AttackRange.RANGED,
            category=WeaponCategory.MAGICAL,
        )
        assert w.damage_type == DamageType.MAGICAL
        assert w.attack_range == AttackRange.RANGED

    def test_default_rarity_is_common(self) -> None:
        w = _make_longsword()
        assert w.rarity == WeaponRarity.COMMON

    def test_default_element_is_none(self) -> None:
        w = _make_longsword()
        assert w.element is None

    def test_default_cha_requirement_is_zero(self) -> None:
        w = _make_longsword()
        assert w.cha_requirement == 0

    def test_weapon_is_frozen(self) -> None:
        w = _make_longsword()
        with pytest.raises(AttributeError):
            w.name = "Hacked"  # type: ignore[misc]


class TestWeaponWithOptionals:

    def test_elemental_weapon(self) -> None:
        w = Weapon(
            name="Flame Sword",
            weapon_type=WeaponType.SWORD,
            damage_kind=DamageKind.SLASHING,
            damage_type=DamageType.PHYSICAL,
            weapon_die=10,
            attack_range=AttackRange.MELEE,
            category=WeaponCategory.MARTIAL,
            rarity=WeaponRarity.UNCOMMON,
            element=ElementType.FIRE,
            cha_requirement=12,
        )
        assert w.element == ElementType.FIRE
        assert w.rarity == WeaponRarity.UNCOMMON
        assert w.cha_requirement == 12


MINIMAL_WEAPON_DICT: dict[str, object] = {
    "name": "Mace",
    "weapon_type": "MACE",
    "damage_kind": "BLUDGEONING",
    "damage_type": "PHYSICAL",
    "weapon_die": 6,
    "attack_range": "MELEE",
    "category": "SIMPLE",
}


class TestWeaponFromDict:

    def test_physical_weapon(self) -> None:
        data = {
            "name": "Dagger",
            "weapon_type": "DAGGER",
            "damage_kind": "PIERCING",
            "damage_type": "PHYSICAL",
            "weapon_die": 4,
            "attack_range": "MELEE",
            "category": "SIMPLE",
        }
        w = Weapon.from_dict(data)
        assert w.name == "Dagger"
        assert w.weapon_type == WeaponType.DAGGER
        assert w.damage_kind == DamageKind.PIERCING
        assert w.weapon_die == 4

    def test_magical_weapon_with_element(self) -> None:
        data = {
            "name": "Frost Staff",
            "weapon_type": "STAFF",
            "damage_kind": "BLUDGEONING",
            "damage_type": "MAGICAL",
            "weapon_die": 10,
            "attack_range": "RANGED",
            "category": "MAGICAL",
            "rarity": "UNCOMMON",
            "element": "ICE",
            "cha_requirement": 12,
        }
        w = Weapon.from_dict(data)
        assert w.element == ElementType.ICE
        assert w.rarity == WeaponRarity.UNCOMMON
        assert w.cha_requirement == 12

    def test_defaults_rarity_to_common(self) -> None:
        w = Weapon.from_dict(dict(MINIMAL_WEAPON_DICT))
        assert w.rarity == WeaponRarity.COMMON

    def test_defaults_element_to_none(self) -> None:
        w = Weapon.from_dict(dict(MINIMAL_WEAPON_DICT))
        assert w.element is None

    def test_invalid_weapon_type_raises(self) -> None:
        data = dict(MINIMAL_WEAPON_DICT, weapon_type="BANANA")
        with pytest.raises(KeyError):
            Weapon.from_dict(data)

    def test_invalid_damage_kind_raises(self) -> None:
        data = dict(MINIMAL_WEAPON_DICT, damage_kind="EXPLODING")
        with pytest.raises(KeyError):
            Weapon.from_dict(data)
