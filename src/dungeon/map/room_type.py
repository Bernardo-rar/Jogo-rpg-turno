"""RoomType — tipos de sala no mapa do dungeon."""

from enum import Enum, auto


class RoomType(Enum):
    """Tipo de sala de um nó do mapa."""

    COMBAT = auto()
    ELITE = auto()
    REST = auto()
    BOSS = auto()
    TREASURE = auto()
    EVENT = auto()
    CAMPFIRE = auto()
    SHOP = auto()
