"""Testes para FloorMap."""

from src.dungeon.map.floor_map import FloorMap
from src.dungeon.map.map_node import MapNode
from src.dungeon.map.room_type import RoomType


def _simple_map() -> FloorMap:
    n0 = MapNode("L0_N0", 0, RoomType.COMBAT, connections=("L1_N0", "L1_N1"))
    n1 = MapNode("L0_N1", 0, RoomType.COMBAT, connections=("L1_N1",))
    n2 = MapNode("L1_N0", 1, RoomType.ELITE, connections=("BOSS",))
    n3 = MapNode("L1_N1", 1, RoomType.REST, connections=("BOSS",))
    boss = MapNode("BOSS", 2, RoomType.BOSS)
    return FloorMap(layers=((n0, n1), (n2, n3)), boss_node=boss)


class TestFloorMap:

    def test_get_node_found(self) -> None:
        m = _simple_map()
        assert m.get_node("L0_N0") is not None

    def test_get_node_boss(self) -> None:
        m = _simple_map()
        assert m.get_node("BOSS") is m.boss_node

    def test_get_node_not_found(self) -> None:
        m = _simple_map()
        assert m.get_node("NOPE") is None

    def test_get_start_nodes(self) -> None:
        m = _simple_map()
        starts = m.get_start_nodes()
        assert len(starts) == 2
        assert starts[0].node_id == "L0_N0"

    def test_get_available_next(self) -> None:
        m = _simple_map()
        nexts = m.get_available_next("L0_N0")
        ids = {n.node_id for n in nexts}
        assert ids == {"L1_N0", "L1_N1"}

    def test_get_available_next_excludes_visited(self) -> None:
        m = _simple_map()
        m.mark_visited("L1_N0")
        nexts = m.get_available_next("L0_N0")
        ids = {n.node_id for n in nexts}
        assert ids == {"L1_N1"}

    def test_mark_visited(self) -> None:
        m = _simple_map()
        m.mark_visited("L0_N0")
        assert m.get_node("L0_N0").visited is True
