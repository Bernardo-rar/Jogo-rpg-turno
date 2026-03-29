"""MapGenerator — gera mapa branching de um floor."""

from __future__ import annotations

from random import Random

from src.dungeon.map.floor_map import FloorMap
from src.dungeon.map.map_node import MapNode
from src.dungeon.map.room_type import RoomType

_MIN_NODES_PER_LAYER = 2
_MAX_NODES_PER_LAYER = 3
_NUM_LAYERS = 3
_BOSS_NODE_ID = "BOSS"

_LAYER_WEIGHTS: tuple[dict[RoomType, int], ...] = (
    {
        RoomType.COMBAT: 50,
        RoomType.EVENT: 25,
        RoomType.TREASURE: 15,
        RoomType.SHOP: 10,
    },
    {
        RoomType.COMBAT: 35,
        RoomType.ELITE: 20,
        RoomType.EVENT: 20,
        RoomType.SHOP: 15,
        RoomType.CAMPFIRE: 5,
        RoomType.TREASURE: 5,
    },
    {
        RoomType.COMBAT: 30,
        RoomType.REST: 20,
        RoomType.CAMPFIRE: 15,
        RoomType.ELITE: 15,
        RoomType.EVENT: 10,
        RoomType.TREASURE: 5,
        RoomType.SHOP: 5,
    },
)


class MapGenerator:
    """Gera FloorMap determinístico a partir de seed."""

    def generate(self, seed: int) -> FloorMap:
        """Gera mapa com 3 layers + boss."""
        rng = Random(seed)
        layers: list[tuple[MapNode, ...]] = []
        for layer_idx in range(_NUM_LAYERS):
            nodes = _generate_layer(rng, layer_idx)
            layers.append(nodes)
        _connect_layers(rng, layers)
        boss = MapNode(
            node_id=_BOSS_NODE_ID,
            layer=_NUM_LAYERS,
            room_type=RoomType.BOSS,
        )
        _connect_to_boss(layers[-1], boss)
        return FloorMap(layers=tuple(layers), boss_node=boss)


def _generate_layer(
    rng: Random,
    layer_idx: int,
) -> tuple[MapNode, ...]:
    """Gera nós para uma camada via weighted random."""
    count = rng.randint(_MIN_NODES_PER_LAYER, _MAX_NODES_PER_LAYER)
    weights_map = _LAYER_WEIGHTS[layer_idx]
    room_types = _pick_room_types(rng, weights_map, count)
    return _build_nodes(layer_idx, room_types)


def _pick_room_types(
    rng: Random,
    weights_map: dict[RoomType, int],
    count: int,
) -> list[RoomType]:
    """Seleciona N room types via weighted random."""
    types = list(weights_map.keys())
    weights = list(weights_map.values())
    return rng.choices(types, weights=weights, k=count)


def _build_nodes(
    layer_idx: int,
    room_types: list[RoomType],
) -> tuple[MapNode, ...]:
    """Constroi MapNodes a partir de room types."""
    return tuple(
        MapNode(
            node_id=f"L{layer_idx}_N{i}",
            layer=layer_idx,
            room_type=rt,
        )
        for i, rt in enumerate(room_types)
    )


def _connect_layers(
    rng: Random,
    layers: list[tuple[MapNode, ...]],
) -> None:
    """Conecta nós entre camadas adjacentes."""
    for i in range(len(layers) - 1):
        current = layers[i]
        next_layer = layers[i + 1]
        _connect_two_layers(rng, current, next_layer)


def _connect_two_layers(
    rng: Random,
    current: tuple[MapNode, ...],
    next_layer: tuple[MapNode, ...],
) -> None:
    """Cada nó conecta a 1-2 nós da próxima camada."""
    next_ids = [n.node_id for n in next_layer]
    connected_targets: set[str] = set()
    for node in current:
        count = rng.randint(1, min(2, len(next_ids)))
        targets = rng.sample(next_ids, count)
        connected_targets.update(targets)
        node.connections = tuple(targets)
    _ensure_all_reachable(rng, current, next_layer, connected_targets)


def _ensure_all_reachable(
    rng: Random,
    current: tuple[MapNode, ...],
    next_layer: tuple[MapNode, ...],
    connected: set[str],
) -> None:
    """Garante que todo nó da próxima camada é alcançável."""
    for target_node in next_layer:
        if target_node.node_id not in connected:
            source = rng.choice(current)
            conns = list(source.connections)
            conns.append(target_node.node_id)
            source.connections = tuple(conns)


def _connect_to_boss(
    last_layer: tuple[MapNode, ...],
    boss: MapNode,
) -> None:
    """Todos os nós da última camada conectam ao boss."""
    for node in last_layer:
        conns = list(node.connections)
        conns.append(boss.node_id)
        node.connections = tuple(conns)
