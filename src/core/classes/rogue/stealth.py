from __future__ import annotations


class Stealth:
    """Estado de furtividade do Ladino.

    Entrar em stealth garante crit no proximo ataque.
    Stealth quebra ao atacar ou receber dano.
    """

    def __init__(self) -> None:
        self._active = False

    @property
    def is_active(self) -> bool:
        return self._active

    @property
    def guaranteed_crit(self) -> bool:
        return self._active

    def enter(self) -> bool:
        """Ativa stealth. Retorna False se ja estava ativo."""
        if self._active:
            return False
        self._active = True
        return True

    def break_stealth(self) -> bool:
        """Desativa stealth. Retorna False se ja estava inativo."""
        if not self._active:
            return False
        self._active = False
        return True
