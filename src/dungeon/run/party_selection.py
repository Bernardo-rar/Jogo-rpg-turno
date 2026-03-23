"""PartySelection — lógica de seleção de party."""

from __future__ import annotations

from src.core.classes.class_id import ClassId
from src.dungeon.run.party_factory import is_frontliner

_MAX_PARTY_SIZE = 4


class PartySelection:
    """Gerencia seleção de classes para a party."""

    def __init__(self, available: tuple[ClassId, ...]) -> None:
        self._available = available
        self._selected: list[ClassId] = []

    @property
    def available(self) -> tuple[ClassId, ...]:
        return self._available

    @property
    def selected(self) -> tuple[ClassId, ...]:
        return tuple(self._selected)

    def select(self, class_id: ClassId) -> bool:
        """Adiciona classe à seleção. Retorna False se inválido."""
        if class_id in self._selected:
            return False
        if len(self._selected) >= _MAX_PARTY_SIZE:
            return False
        if class_id not in self._available:
            return False
        self._selected.append(class_id)
        return True

    def deselect(self, class_id: ClassId) -> bool:
        """Remove classe da seleção."""
        if class_id not in self._selected:
            return False
        self._selected.remove(class_id)
        return True

    def is_valid(self) -> bool:
        """True se 4 selecionados com pelo menos 1 front-liner."""
        if len(self._selected) != _MAX_PARTY_SIZE:
            return False
        return any(is_frontliner(c) for c in self._selected)
