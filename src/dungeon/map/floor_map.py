"""FloorMap — mapa de um floor do dungeon."""

from __future__ import annotations

from dataclasses import dataclass

from src.dungeon.map.map_node import MapNode


@dataclass
class FloorMap:
    """Mapa branching de um floor: layers de nós + boss final."""

    layers: tuple[tuple[MapNode, ...], ...]
    boss_node: MapNode

    def get_node(self, node_id: str) -> MapNode | None:
        """Busca nó por ID."""
        if self.boss_node.node_id == node_id:
            return self.boss_node
        for layer in self.layers:
            for node in layer:
                if node.node_id == node_id:
                    return node
        return None

    def get_start_nodes(self) -> tuple[MapNode, ...]:
        """Retorna nós da primeira camada (entradas do mapa)."""
        if not self.layers:
            return ()
        return self.layers[0]

    def get_available_next(self, node_id: str) -> tuple[MapNode, ...]:
        """Retorna nós conectados ao nó dado que não foram visitados."""
        node = self.get_node(node_id)
        if node is None:
            return ()
        result: list[MapNode] = []
        for conn_id in node.connections:
            target = self.get_node(conn_id)
            if target is not None and not target.visited:
                result.append(target)
        return tuple(result)

    def mark_visited(self, node_id: str) -> None:
        """Marca nó como visitado."""
        node = self.get_node(node_id)
        if node is not None:
            node.visited = True
