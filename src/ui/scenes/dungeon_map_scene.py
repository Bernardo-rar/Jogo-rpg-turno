"""DungeonMapScene — mapa branching do dungeon."""

from __future__ import annotations

from typing import Callable

import pygame

from src.dungeon.map.floor_map import FloorMap
from src.dungeon.map.map_node import MapNode
from src.dungeon.map.room_type import RoomType
from src.ui import colors, layout
from src.ui.font_manager import FontManager

_ROOM_COLORS: dict[RoomType, tuple[int, int, int]] = {
    RoomType.COMBAT: (180, 60, 60),
    RoomType.ELITE: (220, 160, 40),
    RoomType.REST: (60, 180, 80),
    RoomType.BOSS: (160, 60, 200),
}
_VISITED_COLOR = (60, 60, 70)
_AVAILABLE_BORDER = colors.TEXT_YELLOW
_NODE_WIDTH = 140
_NODE_HEIGHT = 50
_LAYER_SPACING = 220
_NODE_SPACING = 80
_BASE_X = 120
_BASE_Y = 150


class DungeonMapScene:
    """Exibe o mapa e permite selecionar o próximo nó."""

    def __init__(
        self,
        fonts: FontManager,
        floor_map: FloorMap,
        current_node_id: str | None,
        on_complete: Callable[[dict], None],
    ) -> None:
        self._fonts = fonts
        self._map = floor_map
        self._current = current_node_id
        self._on_complete = on_complete
        self._available = self._resolve_available()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        idx = _key_to_index(event.key)
        if idx is not None and idx < len(self._available):
            node = self._available[idx]
            self._on_complete({
                "node_id": node.node_id,
                "room_type": node.room_type,
            })

    def update(self, dt_ms: int) -> bool:
        return True

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(colors.BG_DARK)
        _draw_header(surface, self._fonts)
        self._draw_layers(surface)
        self._draw_connections(surface)
        self._draw_available_list(surface)

    def _resolve_available(self) -> list[MapNode]:
        if self._current is None:
            return list(self._map.get_start_nodes())
        return list(self._map.get_available_next(self._current))

    def _draw_layers(self, surface: pygame.Surface) -> None:
        for layer in self._map.layers:
            for node in layer:
                self._draw_node(surface, node)
        self._draw_node(surface, self._map.boss_node)

    def _draw_node(self, surface: pygame.Surface, node: MapNode) -> None:
        x, y = _node_pos(node, self._map)
        rect = pygame.Rect(x, y, _NODE_WIDTH, _NODE_HEIGHT)
        is_available = node in self._available
        if node.visited:
            color = _VISITED_COLOR
        else:
            color = _ROOM_COLORS.get(node.room_type, (100, 100, 100))
        pygame.draw.rect(surface, color, rect, border_radius=6)
        if is_available:
            pygame.draw.rect(
                surface, _AVAILABLE_BORDER, rect, width=3, border_radius=6,
            )
        label = node.room_type.name
        text = self._fonts.small.render(label, True, colors.TEXT_WHITE)
        surface.blit(
            text,
            (x + _NODE_WIDTH // 2 - text.get_width() // 2,
             y + _NODE_HEIGHT // 2 - text.get_height() // 2),
        )

    def _draw_connections(self, surface: pygame.Surface) -> None:
        for layer in self._map.layers:
            for node in layer:
                sx, sy = _node_center(node, self._map)
                for conn_id in node.connections:
                    target = self._map.get_node(conn_id)
                    if target is None:
                        continue
                    tx, ty = _node_center(target, self._map)
                    line_color = (50, 50, 65)
                    pygame.draw.line(surface, line_color, (sx, sy), (tx, ty), 1)

    def _draw_available_list(self, surface: pygame.Surface) -> None:
        y = layout.WINDOW_HEIGHT - 120
        header = self._fonts.medium.render(
            "Escolha o proximo no:", True, colors.TEXT_WHITE,
        )
        surface.blit(header, (40, y))
        for i, node in enumerate(self._available):
            label = f"[{i + 1}] {node.room_type.name} ({node.node_id})"
            color = _ROOM_COLORS.get(node.room_type, colors.TEXT_WHITE)
            text = self._fonts.small.render(label, True, color)
            surface.blit(text, (40 + i * 300, y + 30))


def _draw_header(surface: pygame.Surface, fonts: FontManager) -> None:
    title = fonts.large.render("Dungeon Map", True, colors.TEXT_WHITE)
    surface.blit(title, (layout.WINDOW_WIDTH // 2 - title.get_width() // 2, 30))


def _node_pos(node: MapNode, floor_map: FloorMap) -> tuple[int, int]:
    layer_idx = node.layer
    layer_count = len(floor_map.layers)
    if node.room_type == RoomType.BOSS:
        layer_idx = layer_count
    x = _BASE_X + layer_idx * _LAYER_SPACING
    layer_nodes = _get_layer_nodes(node, floor_map)
    node_idx = 0
    for i, n in enumerate(layer_nodes):
        if n.node_id == node.node_id:
            node_idx = i
            break
    total = len(layer_nodes)
    total_height = total * _NODE_HEIGHT + (total - 1) * _NODE_SPACING
    start_y = _BASE_Y + (400 - total_height) // 2
    y = start_y + node_idx * (_NODE_HEIGHT + _NODE_SPACING)
    return x, y


def _node_center(node: MapNode, floor_map: FloorMap) -> tuple[int, int]:
    x, y = _node_pos(node, floor_map)
    return x + _NODE_WIDTH // 2, y + _NODE_HEIGHT // 2


def _get_layer_nodes(
    node: MapNode, floor_map: FloorMap,
) -> list[MapNode]:
    if node.room_type == RoomType.BOSS:
        return [floor_map.boss_node]
    for layer in floor_map.layers:
        if any(n.node_id == node.node_id for n in layer):
            return list(layer)
    return [node]


def _key_to_index(key: int) -> int | None:
    mapping = {
        pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2,
        pygame.K_4: 3, pygame.K_5: 4,
    }
    return mapping.get(key)
