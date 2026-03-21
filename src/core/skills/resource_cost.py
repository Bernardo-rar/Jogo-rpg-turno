"""ResourceCost frozen dataclass - custo de recurso de classe para uma skill."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResourceCost:
    """Custo de recurso de classe (AP, Fury, Holy Power, etc).

    resource_type mapeia para o atributo do combatant via getattr.
    amount=0 significa 'check only' (para toggles).
    """

    resource_type: str
    amount: int

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> ResourceCost:
        """Cria ResourceCost a partir de dict (JSON)."""
        return cls(
            resource_type=str(data["resource_type"]),
            amount=int(data["amount"]),  # type: ignore[arg-type]
        )
