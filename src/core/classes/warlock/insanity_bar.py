from __future__ import annotations


class InsanityBar:
    """Barra de Insanidade do Warlock.

    Recurso double-edged: acumula ao usar habilidades e receber dano.
    Mais insanidade = mais dano magico mas menos defesa magica.
    Decai no fim do turno.
    """

    MAX_INSANITY = 100

    def __init__(self) -> None:
        self._current = 0

    @property
    def current(self) -> int:
        return self._current

    @property
    def ratio(self) -> float:
        """Razao de insanidade (0.0 a 1.0)."""
        return self._current / self.MAX_INSANITY

    def gain(self, amount: int) -> int:
        """Ganha insanidade ate o maximo. Retorna quantidade real ganha."""
        actual = min(amount, self.MAX_INSANITY - self._current)
        self._current += actual
        return actual

    def decay(self, amount: int) -> int:
        """Decai insanidade ate zero. Retorna quantidade real decaida."""
        actual = min(amount, self._current)
        self._current -= actual
        return actual

    def reset(self) -> None:
        """Reseta insanidade para zero."""
        self._current = 0
