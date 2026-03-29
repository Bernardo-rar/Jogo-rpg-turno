"""Shop state — estado mutavel de uma loja."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from src.dungeon.loot.drop_table import LootDrop

if TYPE_CHECKING:
    from src.dungeon.run.run_state import RunState

_DEFAULT_SELL_PRICE = 5


@dataclass
class ShopItem:
    """Um item disponivel para compra na loja."""

    item_id: str
    name: str
    price: int
    stock: int


class ShopState:
    """Estado da loja: itens, precos, estoque."""

    def __init__(
        self,
        items: list[ShopItem],
        sell_mult: float,
    ) -> None:
        self._items = items
        self._sell_mult = sell_mult

    @property
    def items(self) -> list[ShopItem]:
        """Itens disponiveis na loja."""
        return self._items

    @property
    def sell_multiplier(self) -> float:
        """Multiplicador de venda."""
        return self._sell_mult

    def buy(self, index: int, run_state: RunState) -> bool:
        """Compra item por indice. Retorna True se sucesso."""
        if not self._is_valid_buy(index, run_state):
            return False
        item = self._items[index]
        run_state.gold -= item.price
        item.stock -= 1
        drop = LootDrop(item_type="consumable", item_id=item.item_id)
        run_state.pending_loot.append(drop)
        return True

    def _is_valid_buy(
        self,
        index: int,
        run_state: RunState,
    ) -> bool:
        """Valida se a compra e possivel."""
        if index < 0 or index >= len(self._items):
            return False
        item = self._items[index]
        if item.stock <= 0:
            return False
        return run_state.gold >= item.price

    def sell(self, loot_index: int, run_state: RunState) -> int:
        """Vende item do pending_loot. Retorna gold ganho."""
        if loot_index < 0 or loot_index >= len(run_state.pending_loot):
            return 0
        drop = run_state.pending_loot.pop(loot_index)
        earned = self._calculate_sell_price(drop.item_id)
        run_state.gold += earned
        return earned

    def _calculate_sell_price(self, item_id: str) -> int:
        """Calcula preco de venda baseado no preco de compra."""
        for item in self._items:
            if item.item_id == item_id:
                return int(item.price * self._sell_mult)
        return int(_DEFAULT_SELL_PRICE * self._sell_mult)
