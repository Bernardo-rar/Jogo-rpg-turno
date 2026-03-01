from __future__ import annotations

HOLY_POWER_LIMIT = 5
HOLY_POWER_PER_HEAL = 1


class HolyPower:
    """Recurso de Poder Sagrado do Clerigo.

    Ganho ao curar aliados, gasto em Channel Divinity.
    Limite fixo de 5 pontos.
    """

    def __init__(self) -> None:
        self._current = 0

    @property
    def current(self) -> int:
        return self._current

    @property
    def limit(self) -> int:
        return HOLY_POWER_LIMIT

    def gain(self, amount: int = 1) -> int:
        """Ganha holy power ate o limite. Retorna ganho real."""
        actual = min(amount, HOLY_POWER_LIMIT - self._current)
        self._current += actual
        return actual

    def spend(self, amount: int) -> bool:
        """Gasta holy power. Retorna False se insuficiente."""
        if amount > self._current:
            return False
        self._current -= amount
        return True
