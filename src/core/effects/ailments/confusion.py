"""Confusion - CC ailment que redireciona ataques para alvos aleatorios."""

from __future__ import annotations

from src.core.effects.ailments.cc_ailment import CcAilment
from src.core.effects.tick_result import TickResult


class Confusion(CcAilment):
    """Confusao: ataques sao redirecionados para alvos aleatorios.

    Diferente de Freeze/Paralysis, Confusion NAO pula turno.
    O personagem age normalmente mas seu alvo e randomizado.
    """

    @property
    def redirects_target(self) -> bool:
        """Flag indicando que ataques devem ser redirecionados."""
        return True

    def _do_tick(self) -> TickResult:
        return TickResult(message="Confused! Attacks may target randomly.")
