"""Armor frozen dataclass."""

from __future__ import annotations

from dataclasses import dataclass

from src.core.items.armor_weight import ArmorWeight
from src.core.items.item_rarity import ItemRarity

_DEFAULT_RARITY = ItemRarity.COMMON
_DEFAULT_CHA_REQUIREMENT = 0


@dataclass(frozen=True)
class Armor:
    """Armadura equipavel com bonus de defesa, HP e mana."""

    name: str
    weight: ArmorWeight
    ca_bonus: int
    hp_bonus: int
    mana_bonus: int
    physical_defense_bonus: int
    magical_defense_bonus: int
    rarity: ItemRarity = ItemRarity.COMMON
    cha_requirement: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> Armor:
        """Cria Armor a partir de dict (JSON)."""
        return cls(
            name=str(data["name"]),
            weight=ArmorWeight[str(data["weight"])],
            ca_bonus=int(data["ca_bonus"]),  # type: ignore[arg-type]
            hp_bonus=int(data["hp_bonus"]),  # type: ignore[arg-type]
            mana_bonus=int(data["mana_bonus"]),  # type: ignore[arg-type]
            physical_defense_bonus=int(data["physical_defense_bonus"]),  # type: ignore[arg-type]
            magical_defense_bonus=int(data["magical_defense_bonus"]),  # type: ignore[arg-type]
            rarity=ItemRarity[str(data.get("rarity", _DEFAULT_RARITY.name))],
            cha_requirement=int(data.get("cha_requirement", _DEFAULT_CHA_REQUIREMENT)),  # type: ignore[arg-type]
        )
