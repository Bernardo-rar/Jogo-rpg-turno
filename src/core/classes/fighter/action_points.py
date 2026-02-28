from __future__ import annotations

AP_LIMIT_PER_LEVEL = {1: 2, 2: 4, 3: 6, 4: 8, 5: 10}
DEFAULT_AP_LIMIT = 10
AP_GAIN_PASSIVE = 1


class ActionPoints:
    """Recurso de Pontos de Acao do Guerreiro.

    Ganhos ao atacar, gastos em habilidades especiais.
    Se nenhum AP for gasto no turno, ganha +1 passivamente.
    Limite maximo cresce com o nivel.
    """

    def __init__(self, level: int = 1) -> None:
        self._current = 0
        self._limit = AP_LIMIT_PER_LEVEL.get(level, DEFAULT_AP_LIMIT)
        self._spent_this_turn = False

    @property
    def current(self) -> int:
        return self._current

    @property
    def limit(self) -> int:
        return self._limit

    def gain(self, amount: int = 1) -> int:
        """Ganha AP ate o limite. Retorna quantidade real ganha."""
        actual = min(amount, self._limit - self._current)
        self._current += actual
        return actual

    def spend(self, amount: int) -> bool:
        """Gasta AP. Retorna False se insuficiente (nao gasta nada)."""
        if amount > self._current:
            return False
        self._current -= amount
        self._spent_this_turn = True
        return True

    def on_turn_end(self) -> None:
        """Fim do turno: ganha +1 passivo se nao gastou neste turno."""
        if not self._spent_this_turn:
            self.gain(AP_GAIN_PASSIVE)
        self._spent_this_turn = False
