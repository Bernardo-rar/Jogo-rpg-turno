"""ClassResourceSnapshot — dados de recurso de classe para a UI."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class ResourceDisplayType(Enum):
    """Como o recurso deve ser exibido na UI."""

    BAR = auto()
    COUNTER = auto()
    TOGGLE = auto()


@dataclass(frozen=True)
class ClassResourceSnapshot:
    """Snapshot imutavel de um recurso de classe para rendering."""

    name: str
    display_type: ResourceDisplayType
    current: int
    maximum: int
    color: tuple[int, int, int]
    label: str = ""
