"""Weapon frozen dataclass."""

from __future__ import annotations

from dataclasses import dataclass

from src.core.combat.damage import DamageType
from src.core.combat.targeting import AttackRange
from src.core.elements.element_type import ElementType
from src.core.items.damage_kind import DamageKind
from src.core.items.weapon_category import WeaponCategory
from src.core.items.weapon_rarity import WeaponRarity
from src.core.items.weapon_type import WeaponType

DEFAULT_CHA_REQUIREMENT = 0
_DEFAULT_RARITY = WeaponRarity.COMMON


@dataclass(frozen=True)
class Weapon:
    """Arma equipavel com dados de dano, tipo e categoria."""

    name: str
    weapon_type: WeaponType
    damage_kind: DamageKind
    damage_type: DamageType
    weapon_die: int
    attack_range: AttackRange
    category: WeaponCategory
    rarity: WeaponRarity = WeaponRarity.COMMON
    element: ElementType | None = None
    cha_requirement: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> Weapon:
        """Cria Weapon a partir de dict (JSON). Enum fields parseados por name."""
        element_name = data.get("element")
        element = ElementType[str(element_name)] if element_name else None
        return cls(
            name=str(data["name"]),
            weapon_type=WeaponType[str(data["weapon_type"])],
            damage_kind=DamageKind[str(data["damage_kind"])],
            damage_type=DamageType[str(data["damage_type"])],
            weapon_die=int(data["weapon_die"]),  # type: ignore[arg-type]
            attack_range=AttackRange[str(data["attack_range"])],
            category=WeaponCategory[str(data["category"])],
            rarity=WeaponRarity[str(data.get("rarity", _DEFAULT_RARITY.name))],
            element=element,
            cha_requirement=int(data.get("cha_requirement", DEFAULT_CHA_REQUIREMENT)),  # type: ignore[arg-type]
        )
