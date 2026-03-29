"""Testes para ShopState."""

from src.dungeon.loot.drop_table import LootDrop
from src.dungeon.map.map_generator import MapGenerator
from src.dungeon.run.run_state import RunState
from src.dungeon.shop.shop_state import ShopItem, ShopState
from tests.core.test_combat.conftest import _build_char


def _make_state(gold: int = 100) -> RunState:
    fm = MapGenerator().generate(seed=1)
    party = [_build_char("A")]
    state = RunState(seed=1, party=party, floor_map=fm)
    state.gold = gold
    return state


def _make_shop() -> ShopState:
    items = [
        ShopItem(item_id="health_potion", name="Health Potion", price=15, stock=3),
        ShopItem(item_id="smoke_bomb", name="Smoke Bomb", price=35, stock=1),
    ]
    return ShopState(items=items, sell_mult=0.5)


class TestShopBuy:

    def test_buy_deducts_gold(self) -> None:
        state = _make_state(gold=100)
        shop = _make_shop()
        result = shop.buy(0, state)
        assert result is True
        assert state.gold == 85

    def test_buy_reduces_stock(self) -> None:
        state = _make_state(gold=100)
        shop = _make_shop()
        shop.buy(0, state)
        assert shop.items[0].stock == 2

    def test_buy_adds_to_pending_loot(self) -> None:
        state = _make_state(gold=100)
        shop = _make_shop()
        shop.buy(0, state)
        assert len(state.pending_loot) == 1
        assert state.pending_loot[0].item_id == "health_potion"

    def test_buy_fails_insufficient_gold(self) -> None:
        state = _make_state(gold=5)
        shop = _make_shop()
        result = shop.buy(0, state)
        assert result is False
        assert state.gold == 5

    def test_buy_fails_out_of_stock(self) -> None:
        state = _make_state(gold=200)
        shop = _make_shop()
        shop.buy(1, state)
        result = shop.buy(1, state)
        assert result is False

    def test_buy_fails_invalid_index(self) -> None:
        state = _make_state(gold=100)
        shop = _make_shop()
        result = shop.buy(99, state)
        assert result is False

    def test_buy_multiple_items(self) -> None:
        state = _make_state(gold=100)
        shop = _make_shop()
        shop.buy(0, state)
        shop.buy(0, state)
        assert state.gold == 70
        assert len(state.pending_loot) == 2


class TestShopSell:

    def test_sell_adds_gold(self) -> None:
        state = _make_state(gold=0)
        state.pending_loot.append(
            LootDrop(item_type="consumable", item_id="health_potion"),
        )
        shop = _make_shop()
        earned = shop.sell(0, state)
        assert earned > 0
        assert state.gold == earned

    def test_sell_removes_from_pending_loot(self) -> None:
        state = _make_state(gold=0)
        state.pending_loot.append(
            LootDrop(item_type="consumable", item_id="health_potion"),
        )
        shop = _make_shop()
        shop.sell(0, state)
        assert len(state.pending_loot) == 0

    def test_sell_uses_multiplier(self) -> None:
        state = _make_state(gold=0)
        state.pending_loot.append(
            LootDrop(item_type="consumable", item_id="health_potion"),
        )
        shop = _make_shop()
        earned = shop.sell(0, state)
        assert earned == 7  # 15 * 0.5 = 7.5 -> 7

    def test_sell_fails_invalid_index(self) -> None:
        state = _make_state(gold=0)
        shop = _make_shop()
        earned = shop.sell(0, state)
        assert earned == 0

    def test_sell_unknown_item_uses_default_price(self) -> None:
        state = _make_state(gold=0)
        state.pending_loot.append(
            LootDrop(item_type="consumable", item_id="unknown_item"),
        )
        shop = _make_shop()
        earned = shop.sell(0, state)
        assert earned >= 0
