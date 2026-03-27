"""Testes para RunState."""

import pytest

from src.dungeon.loot.drop_table import LootDrop
from src.dungeon.modifiers.run_modifier import (
    ModifierCategory,
    ModifierEffect,
    RunModifier,
)
from src.dungeon.map.floor_map import FloorMap
from src.dungeon.map.map_generator import MapGenerator
from src.dungeon.map.map_node import MapNode
from src.dungeon.map.room_type import RoomType
from src.dungeon.run.run_state import RunState
from tests.core.test_combat.conftest import _build_char


def _make_state(alive: bool = True) -> RunState:
    fm = MapGenerator().generate(seed=1)
    party = [_build_char("A"), _build_char("B")]
    if not alive:
        for c in party:
            c.take_damage(c.max_hp)
    return RunState(seed=1, party=party, floor_map=fm)


class TestRunState:

    def test_is_party_alive_all_alive(self) -> None:
        state = _make_state(alive=True)
        assert state.is_party_alive is True

    def test_is_party_alive_all_dead(self) -> None:
        state = _make_state(alive=False)
        assert state.is_party_alive is False

    def test_is_party_alive_one_alive(self) -> None:
        state = _make_state(alive=True)
        state.party[0].take_damage(state.party[0].max_hp)
        assert state.is_party_alive is True

    def test_alive_members(self) -> None:
        state = _make_state(alive=True)
        state.party[0].take_damage(state.party[0].max_hp)
        assert len(state.alive_members) == 1

    def test_default_values(self) -> None:
        state = _make_state()
        assert state.current_node_id is None
        assert state.rooms_cleared == 0

    def test_gold_starts_at_zero(self) -> None:
        state = _make_state()
        assert state.gold == 0

    def test_gold_is_mutable(self) -> None:
        state = _make_state()
        state.gold += 50
        assert state.gold == 50

    def test_pending_loot_starts_empty(self) -> None:
        state = _make_state()
        assert state.pending_loot == []

    def test_pending_loot_accepts_drops(self) -> None:
        state = _make_state()
        drop = LootDrop(
            item_type="consumable", item_id="health_potion",
        )
        state.pending_loot.append(drop)
        assert len(state.pending_loot) == 1
        assert state.pending_loot[0].item_id == "health_potion"

    def test_run_state_with_modifiers_aggregates(self) -> None:
        mod_a = RunModifier(
            modifier_id="frail", name="Frail", description="test",
            category=ModifierCategory.DIFFICULTY,
            effect=ModifierEffect(gold_mult=1.15, score_mult=1.1),
        )
        mod_b = RunModifier(
            modifier_id="inflation", name="Inflation", description="test",
            category=ModifierCategory.ECONOMY,
            effect=ModifierEffect(gold_mult=1.25, score_mult=1.05),
        )
        state = _make_state()
        state.active_modifiers = [mod_a, mod_b]
        agg = state.aggregated_effects
        assert agg.gold_mult == pytest.approx(1.4375)
        assert agg.score_mult == pytest.approx(1.155)
