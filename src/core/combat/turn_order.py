from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class Combatant(Protocol):
    """Qualquer entidade que participa do combate."""

    @property
    def name(self) -> str: ...

    @property
    def speed(self) -> int: ...

    @property
    def is_alive(self) -> bool: ...


class TurnOrder:
    """Gerencia a ordem de turnos baseada em speed dos combatentes."""

    def __init__(self, combatants: list[Combatant]) -> None:
        self._combatants = combatants
        self._index = 0
        self._order = self.get_order()

    def get_order(self) -> list[Combatant]:
        """Retorna combatentes vivos ordenados por speed (desc), nome (asc)."""
        alive = [c for c in self._combatants if c.is_alive]
        return sorted(alive, key=lambda c: (-c.speed, c.name))

    def next(self) -> Combatant | None:
        """Retorna proximo combatente vivo no snapshot da rodada."""
        while self._index < len(self._order):
            combatant = self._order[self._index]
            self._index += 1
            if combatant.is_alive:
                return combatant
        return None

    def reset(self) -> None:
        """Reinicia a iteracao e cria snapshot da ordem para a rodada."""
        self._order = self.get_order()
        self._index = 0

    def insert(self, combatant: Combatant) -> None:
        """Adds a combatant mid-combat. Takes effect on next reset."""
        self._combatants.append(combatant)

    @property
    def is_round_complete(self) -> bool:
        return self._index >= len(self._order)
