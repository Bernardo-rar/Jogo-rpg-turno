"""Paralysis - CC com chance de perder acao a cada turno."""

from __future__ import annotations

import random as _random_module
from typing import Callable

from src.core.effects.ailments.cc_ailment import CcAilment
from src.core.effects.tick_result import TickResult

DEFAULT_SKIP_CHANCE = 0.5


class Paralysis(CcAilment):
    """Paralisia: chance de perder a acao a cada turno."""

    def __init__(
        self,
        duration: int,
        skip_chance: float = DEFAULT_SKIP_CHANCE,
        random_fn: Callable[[], float] | None = None,
    ) -> None:
        super().__init__(duration)
        self._skip_chance = skip_chance
        self._random_fn = random_fn or _random_module.random

    @property
    def skip_chance(self) -> float:
        """Chance (0.0-1.0) de perder a acao."""
        return self._skip_chance

    def _do_tick(self) -> TickResult:
        """Chance de pular turno baseada em random."""
        if self._random_fn() < self._skip_chance:
            return TickResult(
                skip_turn=True,
                message="Paralyzed! Cannot act.",
            )
        return TickResult(message="Resisted paralysis.")
