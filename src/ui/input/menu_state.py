"""MenuLevel e MenuOption — tipos de dados do menu hierarquico."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class MenuLevel(Enum):
    """Nivel do menu hierarquico."""

    ACTION_TYPE = auto()
    SPECIFIC_ACTION = auto()
    TARGET_SELECT = auto()


@dataclass(frozen=True)
class MenuOption:
    """Opcao visivel no menu com tecla, label e disponibilidade."""

    key: int
    label: str
    available: bool = True
    reason: str = ""
