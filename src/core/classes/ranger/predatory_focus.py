from __future__ import annotations


class PredatoryFocus:
    """Barra de Foco Predatorio: ganha stacks ao acertar, perde ao errar."""

    def __init__(self, max_stacks: int) -> None:
        self._current = 0
        self._max_stacks = max_stacks

    @property
    def current(self) -> int:
        return self._current

    @property
    def max_stacks(self) -> int:
        return self._max_stacks

    @property
    def focus_ratio(self) -> float:
        if self._max_stacks == 0:
            return 0.0
        return self._current / self._max_stacks

    def gain(self, amount: int) -> int:
        """Ganha stacks ate o max. Retorna quantidade real ganha."""
        actual = min(amount, self._max_stacks - self._current)
        self._current += actual
        return actual

    def lose(self, amount: int) -> int:
        """Perde stacks ate 0. Retorna quantidade real perdida."""
        actual = min(amount, self._current)
        self._current -= actual
        return actual

    def decay(self, amount: int) -> int:
        """Decai stacks no fim do turno. Retorna quantidade decaida."""
        return self.lose(amount)
