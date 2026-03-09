"""Inventory - gerencia slots de consumiveis."""

from __future__ import annotations

from dataclasses import replace

from src.core.items.consumable import Consumable
from src.core.items.inventory_slot import InventorySlot

MAX_CONSUMABLE_SLOTS = 20


class Inventory:
    """Inventario de consumiveis com stacking e limite de slots."""

    def __init__(self, max_slots: int = MAX_CONSUMABLE_SLOTS) -> None:
        self._slots: dict[str, InventorySlot] = {}
        self._max_slots = max_slots

    @property
    def slots(self) -> tuple[InventorySlot, ...]:
        """Retorna todos os slots ocupados."""
        return tuple(self._slots.values())

    @property
    def available_slots(self) -> int:
        """Quantos slots livres restam."""
        return self._max_slots - len(self._slots)

    @property
    def is_full(self) -> bool:
        """Se o inventario esta cheio (sem slots livres)."""
        return len(self._slots) >= self._max_slots

    def add_item(self, consumable: Consumable, quantity: int = 1) -> bool:
        """Adiciona consumivel. Retorna False se nao couber."""
        cid = consumable.consumable_id
        if cid in self._slots:
            return self._add_to_existing(cid, quantity)
        if self.is_full:
            return False
        self._slots[cid] = InventorySlot(consumable=consumable, quantity=quantity)
        return True

    def remove_item(self, consumable_id: str, quantity: int = 1) -> bool:
        """Remove quantidade do consumivel. Retorna False se insuficiente."""
        if consumable_id not in self._slots:
            return False
        slot = self._slots[consumable_id]
        if slot.quantity < quantity:
            return False
        return self._update_or_remove(consumable_id, slot, quantity)

    def get_slot(self, consumable_id: str) -> InventorySlot | None:
        """Retorna o slot do consumivel ou None."""
        return self._slots.get(consumable_id)

    def has_item(self, consumable_id: str) -> bool:
        """Se o inventario contem o consumivel."""
        return consumable_id in self._slots

    def get_quantity(self, consumable_id: str) -> int:
        """Retorna quantidade do consumivel (0 se nao existir)."""
        slot = self._slots.get(consumable_id)
        return slot.quantity if slot else 0

    def _add_to_existing(self, cid: str, quantity: int) -> bool:
        """Incrementa quantidade de um slot existente."""
        slot = self._slots[cid]
        new_qty = slot.quantity + quantity
        if new_qty > slot.consumable.max_stack:
            return False
        self._slots[cid] = replace(slot, quantity=new_qty)
        return True

    def _update_or_remove(
        self, cid: str, slot: InventorySlot, quantity: int,
    ) -> bool:
        """Atualiza quantidade ou remove slot se zerou."""
        new_qty = slot.quantity - quantity
        if new_qty == 0:
            del self._slots[cid]
        else:
            self._slots[cid] = replace(slot, quantity=new_qty)
        return True
