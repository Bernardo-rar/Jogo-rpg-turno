"""Barreira magica que absorve dano antes do HP."""

from __future__ import annotations


class Barrier:
    """Barreira magica que absorve dano antes do HP.

    Absorve dano ate ser depletada. Qualquer Character possui uma barreira.
    """

    def __init__(self, max_value: int = 999) -> None:
        self._current = 0
        self._max_value = max_value

    @property
    def current(self) -> int:
        return self._current

    @property
    def max_value(self) -> int:
        return self._max_value

    @property
    def is_active(self) -> bool:
        return self._current > 0

    def add(self, amount: int) -> None:
        """Adiciona pontos de barreira, clampando no max."""
        self._current = min(self._current + amount, self._max_value)

    def absorb(self, damage: int) -> int:
        """Absorve dano. Retorna dano restante que passa pela barreira."""
        absorbed = min(damage, self._current)
        self._current -= absorbed
        return damage - absorbed
