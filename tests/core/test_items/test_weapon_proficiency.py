"""Testes para weapon_proficiency (can_equip + constantes por classe)."""

from src.core.combat.damage import DamageType
from src.core.combat.targeting import AttackRange
from src.core.items.damage_kind import DamageKind
from src.core.items.weapon import Weapon
from src.core.items.weapon_category import WeaponCategory
from src.core.items.weapon_proficiency import (
    CLERIC_PROFICIENCIES,
    DEFAULT_PROFICIENCIES,
    FIGHTER_PROFICIENCIES,
    MAGE_PROFICIENCIES,
    can_equip,
)
from src.core.items.weapon_type import WeaponType

SIMPLE_SWORD = Weapon(
    name="Short Sword",
    weapon_type=WeaponType.SWORD,
    damage_kind=DamageKind.SLASHING,
    damage_type=DamageType.PHYSICAL,
    weapon_die=6,
    attack_range=AttackRange.MELEE,
    category=WeaponCategory.SIMPLE,
)

MARTIAL_SWORD = Weapon(
    name="Longsword",
    weapon_type=WeaponType.SWORD,
    damage_kind=DamageKind.SLASHING,
    damage_type=DamageType.PHYSICAL,
    weapon_die=8,
    attack_range=AttackRange.MELEE,
    category=WeaponCategory.MARTIAL,
)

MAGICAL_STAFF = Weapon(
    name="Arcane Staff",
    weapon_type=WeaponType.STAFF,
    damage_kind=DamageKind.BLUDGEONING,
    damage_type=DamageType.MAGICAL,
    weapon_die=8,
    attack_range=AttackRange.RANGED,
    category=WeaponCategory.MAGICAL,
)


class TestCanEquip:

    def test_simple_weapon_with_simple_proficiency(self) -> None:
        assert can_equip(SIMPLE_SWORD, frozenset({WeaponCategory.SIMPLE}))

    def test_martial_without_martial_returns_false(self) -> None:
        assert not can_equip(MARTIAL_SWORD, frozenset({WeaponCategory.SIMPLE}))

    def test_martial_with_martial(self) -> None:
        assert can_equip(MARTIAL_SWORD, frozenset({WeaponCategory.MARTIAL}))

    def test_magical_with_magical(self) -> None:
        assert can_equip(MAGICAL_STAFF, frozenset({WeaponCategory.MAGICAL}))

    def test_magical_without_magical_returns_false(self) -> None:
        assert not can_equip(MAGICAL_STAFF, frozenset({WeaponCategory.SIMPLE}))


class TestClassProficiencies:

    def test_fighter_includes_simple_and_martial(self) -> None:
        assert WeaponCategory.SIMPLE in FIGHTER_PROFICIENCIES
        assert WeaponCategory.MARTIAL in FIGHTER_PROFICIENCIES

    def test_mage_includes_simple_and_magical(self) -> None:
        assert WeaponCategory.SIMPLE in MAGE_PROFICIENCIES
        assert WeaponCategory.MAGICAL in MAGE_PROFICIENCIES

    def test_cleric_includes_only_simple(self) -> None:
        assert CLERIC_PROFICIENCIES == frozenset({WeaponCategory.SIMPLE})

    def test_default_includes_only_simple(self) -> None:
        assert DEFAULT_PROFICIENCIES == frozenset({WeaponCategory.SIMPLE})
