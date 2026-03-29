"""EquipmentCatalogs — resolve LootDrop para item concreto."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from src.dungeon.loot.drop_table import LootDrop

if TYPE_CHECKING:
    from src.core.items.accessory import Accessory
    from src.core.items.armor import Armor
    from src.core.items.weapon import Weapon


@dataclass(frozen=True)
class EquipmentCatalogs:
    """Bundle de catalogos de armas, armaduras e acessorios."""

    weapons: dict[str, Weapon]
    armors: dict[str, Armor]
    accessories: dict[str, Accessory]

    def resolve_drop(self, drop: LootDrop) -> Weapon | Armor | Accessory | None:
        """Resolve LootDrop para item concreto via item_type + item_id."""
        resolver = _RESOLVERS.get(drop.item_type)
        if resolver is None:
            return None
        return resolver(self, drop.item_id)

    def find_weapon_id(self, weapon: Weapon) -> str | None:
        """Busca item_id de uma weapon no catalogo."""
        return _reverse_lookup(self.weapons, weapon)

    def find_armor_id(self, armor: Armor) -> str | None:
        """Busca item_id de uma armor no catalogo."""
        return _reverse_lookup(self.armors, armor)

    def find_accessory_id(self, accessory: Accessory) -> str | None:
        """Busca item_id de um accessory no catalogo."""
        return _reverse_lookup(self.accessories, accessory)

    def _resolve_weapon(self, item_id: str) -> Weapon | None:
        return self.weapons.get(item_id)

    def _resolve_armor(self, item_id: str) -> Armor | None:
        return self.armors.get(item_id)

    def _resolve_accessory(self, item_id: str) -> Accessory | None:
        return self.accessories.get(item_id)


def _reverse_lookup(catalog: dict, item: object) -> str | None:
    """Busca reversa: item -> item_id."""
    for item_id, stored in catalog.items():
        if stored is item or stored == item:
            return item_id
    return None


_RESOLVERS: dict[str, object] = {
    "weapon": EquipmentCatalogs._resolve_weapon,
    "armor": EquipmentCatalogs._resolve_armor,
    "accessory": EquipmentCatalogs._resolve_accessory,
}
