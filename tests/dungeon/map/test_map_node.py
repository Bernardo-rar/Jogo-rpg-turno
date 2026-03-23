"""Testes para MapNode."""

from src.dungeon.map.map_node import MapNode
from src.dungeon.map.room_type import RoomType


class TestMapNode:

    def test_create_basic(self) -> None:
        node = MapNode(node_id="L0_N0", layer=0, room_type=RoomType.COMBAT)
        assert node.node_id == "L0_N0"
        assert node.layer == 0
        assert node.room_type == RoomType.COMBAT

    def test_default_not_visited(self) -> None:
        node = MapNode(node_id="L0_N0", layer=0, room_type=RoomType.COMBAT)
        assert node.visited is False

    def test_default_empty_connections(self) -> None:
        node = MapNode(node_id="L0_N0", layer=0, room_type=RoomType.COMBAT)
        assert node.connections == ()

    def test_mutable_visited(self) -> None:
        node = MapNode(node_id="L0_N0", layer=0, room_type=RoomType.COMBAT)
        node.visited = True
        assert node.visited is True
