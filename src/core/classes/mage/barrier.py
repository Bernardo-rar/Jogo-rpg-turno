from __future__ import annotations

BARRIER_EFFICIENCY = 2


class Barrier:
    """Barreira magica que absorve dano antes do HP.

    Criada gastando mana. 1 mana = BARRIER_EFFICIENCY pontos de barreira.
    Absorve dano ate ser depletada.
    """

    def __init__(self) -> None:
        self._current = 0

    @property
    def current(self) -> int:
        return self._current

    @property
    def is_active(self) -> bool:
        return self._current > 0

    def add(self, amount: int) -> None:
        """Adiciona pontos de barreira."""
        self._current += amount

    def absorb(self, damage: int) -> int:
        """Absorve dano. Retorna dano restante que passa pela barreira."""
        absorbed = min(damage, self._current)
        self._current -= absorbed
        return damage - absorbed
