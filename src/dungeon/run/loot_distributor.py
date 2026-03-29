"""Distribui consumiveis do pending_loot para o inventario da party."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.characters.character import Character
    from src.core.items.consumable import Consumable
    from src.dungeon.loot.drop_table import LootDrop


def distribute_consumables(
    party: list[Character],
    pending_loot: list[LootDrop],
    consumable_catalog: dict[str, Consumable],
) -> list[LootDrop]:
    """Move consumiveis do pending_loot para o inventario do lider.

    Retorna os drops que NAO foram consumiveis (equipamentos etc.).
    """
    remaining: list[LootDrop] = []
    leader = _find_leader(party)
    for drop in pending_loot:
        if drop.item_type != "consumable":
            remaining.append(drop)
            continue
        if leader is None:
            remaining.append(drop)
            continue
        if not _add_to_inventory(leader, drop, consumable_catalog):
            remaining.append(drop)
    return remaining


def _find_leader(party: list[Character]) -> Character | None:
    """Retorna o primeiro personagem vivo com inventario."""
    for char in party:
        if char.is_alive and char.inventory is not None:
            return char
    return None


def _add_to_inventory(
    char: Character,
    drop: LootDrop,
    catalog: dict[str, Consumable],
) -> bool:
    """Tenta adicionar consumivel ao inventario. Retorna True se sucesso."""
    consumable = catalog.get(drop.item_id)
    if consumable is None:
        return False
    inv = char.inventory
    if inv is None:
        return False
    return inv.add_item(consumable, drop.quantity)
