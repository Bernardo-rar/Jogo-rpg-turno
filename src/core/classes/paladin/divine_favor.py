from __future__ import annotations


class DivineFavor:
    """Favor Divino do Paladino.

    Recurso de stacks ganho ao proteger, buffar ou curar aliados.
    Gasto em Glimpse of Glory.
    """

    def __init__(self, max_stacks: int) -> None:
        self._current = 0
        self._max_stacks = max_stacks

    @property
    def current(self) -> int:
        return self._current

    @property
    def max_stacks(self) -> int:
        return self._max_stacks

    def gain(self, amount: int = 1) -> int:
        """Ganha stacks ate o maximo. Retorna quantidade real ganha."""
        actual = min(amount, self._max_stacks - self._current)
        self._current += actual
        return actual

    def spend(self, amount: int) -> bool:
        """Gasta stacks. Retorna False se insuficiente."""
        if amount > self._current:
            return False
        self._current -= amount
        return True
