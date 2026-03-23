"""Testes para RunState."""

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
