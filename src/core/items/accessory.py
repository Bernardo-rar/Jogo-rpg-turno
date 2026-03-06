"""Accessory frozen dataclass."""

from __future__ import annotations

from dataclasses import dataclass

from src.core.items.accessory_type import AccessoryType
from src.core.items.item_rarity import ItemRarity
from src.core.items.stat_bonus import StatBonus

_DEFAULT_RARITY = ItemRarity.COMMON
_DEFAULT_CHA_REQUIREMENT = 0


@dataclass(frozen=True)
class Accessory:
    """Acessorio equipavel com bonus de stats."""

    name: str
    accessory_type: AccessoryType
    stat_bonuses: tuple[StatBonus, ...]
    rarity: ItemRarity = ItemRarity.COMMON
    cha_requirement: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> Accessory:
        """Cria Accessory a partir de dict (JSON)."""
        raw_bonuses = data.get("stat_bonuses", [])
        bonuses = tuple(
            StatBonus.from_dict(b) for b in raw_bonuses  # type: ignore[union-attr]
        )
        return cls(
            name=str(data["name"]),
            accessory_type=AccessoryType[str(data["accessory_type"])],
            stat_bonuses=bonuses,
            rarity=ItemRarity[str(data.get("rarity", _DEFAULT_RARITY.name))],
            cha_requirement=int(data.get("cha_requirement", _DEFAULT_CHA_REQUIREMENT)),  # type: ignore[arg-type]
        )
