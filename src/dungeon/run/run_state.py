"""RunState — estado mutável de uma run roguelite."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.characters.character import Character
    from src.dungeon.map.floor_map import FloorMap


@dataclass
class RunState:
    """Estado da run atual: party, mapa, progresso."""

    seed: int
    party: list[Character]
    floor_map: FloorMap
    current_node_id: str | None = None
    rooms_cleared: int = 0

    @property
    def is_party_alive(self) -> bool:
        """True se pelo menos 1 membro da party está vivo."""
        return any(c.is_alive for c in self.party)

    @property
    def alive_members(self) -> list[Character]:
        """Retorna membros vivos da party."""
        return [c for c in self.party if c.is_alive]
