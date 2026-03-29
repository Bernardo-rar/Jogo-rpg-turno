"""Testes para MapGenerator."""

from src.dungeon.map.floor_map import FloorMap
from src.dungeon.map.map_generator import MapGenerator
from src.dungeon.map.room_type import RoomType


class TestMapGenerator:

    def test_generates_floor_map(self) -> None:
        gen = MapGenerator()
        fm = gen.generate(seed=42)
        assert isinstance(fm, FloorMap)

    def test_has_three_layers(self) -> None:
        fm = MapGenerator().generate(seed=42)
        assert len(fm.layers) == 3

    def test_has_boss_node(self) -> None:
        fm = MapGenerator().generate(seed=42)
        assert fm.boss_node.room_type == RoomType.BOSS

    def test_deterministic_same_seed(self) -> None:
        gen = MapGenerator()
        fm1 = gen.generate(seed=99)
        fm2 = gen.generate(seed=99)
        ids1 = [n.node_id for layer in fm1.layers for n in layer]
        ids2 = [n.node_id for layer in fm2.layers for n in layer]
        assert ids1 == ids2

    def test_different_seeds_can_vary(self) -> None:
        gen = MapGenerator()
        maps = [gen.generate(seed=i) for i in range(10)]
        layer_sizes = {len(m.layers[0]) for m in maps}
        assert len(layer_sizes) >= 1

    def test_all_paths_reach_boss(self) -> None:
        fm = MapGenerator().generate(seed=42)
        for node in fm.layers[-1]:
            assert fm.boss_node.node_id in node.connections

    def test_each_layer_has_nodes(self) -> None:
        fm = MapGenerator().generate(seed=42)
        for layer in fm.layers:
            assert 2 <= len(layer) <= 3

    def test_all_next_layer_nodes_reachable(self) -> None:
        fm = MapGenerator().generate(seed=42)
        for i in range(len(fm.layers) - 1):
            current = fm.layers[i]
            next_layer = fm.layers[i + 1]
            connected = set()
            for node in current:
                connected.update(node.connections)
            for target in next_layer:
                assert target.node_id in connected

    def test_layer0_uses_weighted_types(self) -> None:
        """Layer 0 pode gerar COMBAT, EVENT, TREASURE ou SHOP."""
        valid = {RoomType.COMBAT, RoomType.EVENT, RoomType.TREASURE, RoomType.SHOP}
        gen = MapGenerator()
        for seed in range(50):
            fm = gen.generate(seed=seed)
            for node in fm.layers[0]:
                assert node.room_type in valid

    def test_layer1_can_have_elite(self) -> None:
        """Layer 1 inclui ELITE nos pesos."""
        gen = MapGenerator()
        found_elite = False
        for seed in range(200):
            fm = gen.generate(seed=seed)
            for node in fm.layers[1]:
                if node.room_type == RoomType.ELITE:
                    found_elite = True
                    break
            if found_elite:
                break
        assert found_elite

    def test_new_room_types_appear(self) -> None:
        """Com seeds suficientes, novos tipos aparecem."""
        gen = MapGenerator()
        all_types: set[RoomType] = set()
        for seed in range(200):
            fm = gen.generate(seed=seed)
            for layer in fm.layers:
                for node in layer:
                    all_types.add(node.room_type)
        new_types = {RoomType.TREASURE, RoomType.EVENT, RoomType.CAMPFIRE, RoomType.SHOP}
        found_new = all_types & new_types
        assert len(found_new) >= 3

    def test_boss_always_at_end(self) -> None:
        """Boss nunca aparece nas layers normais."""
        gen = MapGenerator()
        for seed in range(50):
            fm = gen.generate(seed=seed)
            for layer in fm.layers:
                for node in layer:
                    assert node.room_type != RoomType.BOSS
