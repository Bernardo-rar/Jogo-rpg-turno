"""Categorias de consumiveis."""

from enum import Enum, auto


class ConsumableCategory(Enum):
    """Tipo funcional do consumivel: cura, defesa, ofensivo, cleanse, fuga."""

    HEALING = auto()
    DEFENSE = auto()
    OFFENSIVE = auto()
    CLEANSE = auto()
    ESCAPE = auto()
