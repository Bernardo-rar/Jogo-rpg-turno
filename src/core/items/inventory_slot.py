"""InventorySlot frozen dataclass - um slot do inventario com item e quantidade."""

from __future__ import annotations

from dataclasses import dataclass

from src.core.items.consumable import Consumable


@dataclass(frozen=True)
class InventorySlot:
    """Um slot do inventario: referencia a um consumivel e sua quantidade."""

    consumable: Consumable
    quantity: int
