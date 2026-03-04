from __future__ import annotations


class FuryBar:
    """Barra de Furia do Barbaro.

    Recurso que acumula ao receber dano e atacar.
    Fury passiva aumenta ataque e regen proporcionalmente.
    Decai no fim do turno se nao recebeu dano.
    """

    def __init__(self, max_fury: int) -> None:
        self._current = 0
        self._max_fury = max_fury

    @property
    def current(self) -> int:
        return self._current

    @property
    def max_fury(self) -> int:
        return self._max_fury

    @property
    def fury_ratio(self) -> float:
        """Razao de furia preenchida (0.0 a 1.0)."""
        if self._max_fury == 0:
            return 0.0
        return self._current / self._max_fury

    def gain(self, amount: int) -> int:
        """Ganha fury ate o maximo. Retorna quantidade real ganha."""
        actual = min(amount, self._max_fury - self._current)
        self._current += actual
        return actual

    def spend(self, amount: int) -> bool:
        """Gasta fury. Retorna False se insuficiente."""
        if amount > self._current:
            return False
        self._current -= amount
        return True

    def decay(self, amount: int) -> int:
        """Decai fury ate zero. Retorna quantidade real decaida."""
        actual = min(amount, self._current)
        self._current -= actual
        return actual

    def update_max(self, new_max: int) -> None:
        """Atualiza max fury. Clamp current se necessario."""
        self._max_fury = new_max
        self._current = min(self._current, self._max_fury)
