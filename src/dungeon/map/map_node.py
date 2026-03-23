"""MapNode — nó do mapa branching do dungeon."""

from __future__ import annotations

from dataclasses import dataclass, field

from src.dungeon.map.room_type import RoomType


@dataclass
class MapNode:
    """Um nó no mapa do dungeon."""

    node_id: str
    layer: int
    room_type: RoomType
    connections: tuple[str, ...] = ()
    visited: bool = False
