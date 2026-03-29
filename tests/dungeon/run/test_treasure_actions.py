"""Testes para treasure_actions."""

from random import Random

from src.dungeon.loot.drop_table import LootDrop
from src.dungeon.map.floor_map import FloorMap
from src.dungeon.map.map_generator import MapGenerator
from src.dungeon.run.run_state import RunState
from src.dungeon.run.treasure_actions import TreasureResult, resolve_treasure
from tests.core.test_combat.conftest import _build_char


def _make_state() -> RunState:
    fm = MapGenerator().generate(seed=1)
    party = [_build_char("A"), _build_char("B")]
    return RunState(seed=1, party=party, floor_map=fm)


class TestResolveTreasure:

    def test_returns_treasure_result(self) -> None:
        state = _make_state()
        rng = Random(42)
        result = resolve_treasure(state, rng)
        assert isinstance(result, TreasureResult)

    def test_gold_within_tier1_range(self) -> None:
        state = _make_state()
        rng = Random(42)
        result = resolve_treasure(state, rng)
        assert 20 <= result.gold_earned <= 50

    def test_drops_are_tuple_of_loot_drop(self) -> None:
        state = _make_state()
        rng = Random(42)
        result = resolve_treasure(state, rng)
        assert isinstance(result.drops, tuple)
        for drop in result.drops:
            assert isinstance(drop, LootDrop)

    def test_drop_count_within_range(self) -> None:
        state = _make_state()
        rng = Random(42)
        result = resolve_treasure(state, rng)
        assert 1 <= len(result.drops) <= 2

    def test_gold_added_to_run_state(self) -> None:
        state = _make_state()
        initial_gold = state.gold
        rng = Random(42)
        result = resolve_treasure(state, rng)
        assert state.gold == initial_gold + result.gold_earned

    def test_drops_added_to_pending_loot(self) -> None:
        state = _make_state()
        rng = Random(42)
        result = resolve_treasure(state, rng)
        assert len(state.pending_loot) == len(result.drops)

    def test_deterministic_with_same_seed(self) -> None:
        state1 = _make_state()
        state2 = _make_state()
        r1 = resolve_treasure(state1, Random(99))
        r2 = resolve_treasure(state2, Random(99))
        assert r1.gold_earned == r2.gold_earned
        assert r1.drops == r2.drops
