"""Shop loader — carrega inventario da loja do JSON."""

from __future__ import annotations

import json

from src.core._paths import resolve_data_path
from src.dungeon.shop.shop_state import ShopItem, ShopState

_SHOP_FILE = "data/dungeon/shop/shop_inventory.json"


def _parse_item(raw: dict) -> ShopItem:
    """Converte dict JSON em ShopItem."""
    return ShopItem(
        item_id=raw["item_id"],
        name=raw["name"],
        price=raw["price"],
        stock=raw["stock"],
    )


def load_shop(tier: int = 1) -> ShopState:
    """Carrega loja do JSON para o tier especificado."""
    path = resolve_data_path(_SHOP_FILE)
    raw = json.loads(path.read_text(encoding="utf-8"))
    tier_data = raw[f"tier{tier}"]
    items = [_parse_item(i) for i in tier_data["items"]]
    sell_mult = tier_data["sell_multiplier"]
    return ShopState(items=items, sell_mult=sell_mult)
