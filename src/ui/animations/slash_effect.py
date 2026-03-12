"""Linha diagonal cruzando o card (ataque fisico)."""

from __future__ import annotations

import pygame

DEFAULT_DURATION_MS = 300
LINE_WIDTH = 3
LINE_COLOR = (255, 255, 200)


class SlashEffect:
    """Linha diagonal que cruza o card do alvo."""

    def __init__(
        self,
        *,
        x: int,
        y: int,
        width: int,
        height: int,
        duration_ms: int = DEFAULT_DURATION_MS,
    ) -> None:
        self.blocking = True
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._duration_ms = duration_ms
        self._elapsed = 0

    def update(self, dt_ms: int) -> None:
        """Avanca tempo da animacao."""
        self._elapsed = min(self._elapsed + dt_ms, self._duration_ms)

    def draw(self, surface: pygame.Surface) -> None:
        """Desenha linha diagonal parcial baseada no progress."""
        if self.is_done:
            return
        start = (self._x, self._y)
        end_x = self._x + int(self._width * self.progress)
        end_y = self._y + int(self._height * self.progress)
        pygame.draw.line(surface, LINE_COLOR, start, (end_x, end_y), LINE_WIDTH)

    @property
    def is_done(self) -> bool:
        """True quando a animacao terminou."""
        return self._elapsed >= self._duration_ms

    @property
    def progress(self) -> float:
        """Progresso da animacao (0.0 a 1.0)."""
        if self._duration_ms == 0:
            return 1.0
        return min(self._elapsed / self._duration_ms, 1.0)
