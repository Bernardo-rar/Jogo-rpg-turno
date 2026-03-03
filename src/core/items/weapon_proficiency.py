"""Proficiencia de armas por classe."""

from __future__ import annotations

from src.core.items.weapon import Weapon
from src.core.items.weapon_category import WeaponCategory

FIGHTER_PROFICIENCIES: frozenset[WeaponCategory] = frozenset({
    WeaponCategory.SIMPLE,
    WeaponCategory.MARTIAL,
})

MAGE_PROFICIENCIES: frozenset[WeaponCategory] = frozenset({
    WeaponCategory.SIMPLE,
    WeaponCategory.MAGICAL,
})

CLERIC_PROFICIENCIES: frozenset[WeaponCategory] = frozenset({
    WeaponCategory.SIMPLE,
})

DEFAULT_PROFICIENCIES: frozenset[WeaponCategory] = frozenset({
    WeaponCategory.SIMPLE,
})


def can_equip(
    weapon: Weapon,
    proficiencies: frozenset[WeaponCategory],
) -> bool:
    """True se a categoria da arma esta nas proficiencias."""
    return weapon.category in proficiencies
