"""Test dungeon — linear map with ALL room types in sequence.

Run: python -m scripts.play_test_dungeon
"""

from src.dungeon.map.floor_map import FloorMap
from src.dungeon.map.map_generator import MapGenerator
from src.dungeon.map.map_node import MapNode
from src.dungeon.map.room_type import RoomType
from src.ui.run_app import RunApp


def _build_test_map() -> FloorMap:
    """Creates a linear map: combat->shop->event->treasure->campfire->rest->elite->boss."""
    nodes = [
        MapNode("T_COMBAT", 0, RoomType.COMBAT),
        MapNode("T_SHOP", 1, RoomType.SHOP),
        MapNode("T_EVENT", 2, RoomType.EVENT),
        MapNode("T_TREASURE", 3, RoomType.TREASURE),
        MapNode("T_CAMPFIRE", 4, RoomType.CAMPFIRE),
        MapNode("T_REST", 5, RoomType.REST),
        MapNode("T_ELITE", 6, RoomType.ELITE),
    ]
    boss = MapNode("BOSS", 7, RoomType.BOSS)
    for i in range(len(nodes) - 1):
        nodes[i].connections = (nodes[i + 1].node_id,)
    nodes[-1].connections = (boss.node_id,)
    layers = tuple((n,) for n in nodes)
    return FloorMap(layers=layers, boss_node=boss)


def _patched_generate(self, seed: int) -> FloorMap:
    """Replaces MapGenerator.generate with our test map."""
    return _build_test_map()


def main() -> None:
    MapGenerator.generate = _patched_generate
    RunApp().start()


if __name__ == "__main__":
    main()
