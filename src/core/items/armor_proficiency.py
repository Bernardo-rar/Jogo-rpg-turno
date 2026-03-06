"""Proficiencia de armadura por classe."""

from __future__ import annotations

from src.core.items.armor import Armor
from src.core.items.armor_weight import ArmorWeight

_ALL = frozenset(ArmorWeight)
_LIGHT_MEDIUM = frozenset({ArmorWeight.LIGHT, ArmorWeight.MEDIUM})
_LIGHT = frozenset({ArmorWeight.LIGHT})

FIGHTER_ARMOR_PROF: frozenset[ArmorWeight] = _ALL
PALADIN_ARMOR_PROF: frozenset[ArmorWeight] = _ALL

CLERIC_ARMOR_PROF: frozenset[ArmorWeight] = _LIGHT_MEDIUM
BARBARIAN_ARMOR_PROF: frozenset[ArmorWeight] = _LIGHT_MEDIUM
RANGER_ARMOR_PROF: frozenset[ArmorWeight] = _LIGHT_MEDIUM
DRUID_ARMOR_PROF: frozenset[ArmorWeight] = _LIGHT_MEDIUM
ARTIFICER_ARMOR_PROF: frozenset[ArmorWeight] = _LIGHT_MEDIUM

MAGE_ARMOR_PROF: frozenset[ArmorWeight] = _LIGHT
MONK_ARMOR_PROF: frozenset[ArmorWeight] = _LIGHT
SORCERER_ARMOR_PROF: frozenset[ArmorWeight] = _LIGHT
WARLOCK_ARMOR_PROF: frozenset[ArmorWeight] = _LIGHT
ROGUE_ARMOR_PROF: frozenset[ArmorWeight] = _LIGHT
BARD_ARMOR_PROF: frozenset[ArmorWeight] = _LIGHT

DEFAULT_ARMOR_PROF: frozenset[ArmorWeight] = _LIGHT


def can_equip_armor(
    armor: Armor,
    proficiencies: frozenset[ArmorWeight],
) -> bool:
    """True se o peso da armadura esta nas proficiencias."""
    return armor.weight in proficiencies
