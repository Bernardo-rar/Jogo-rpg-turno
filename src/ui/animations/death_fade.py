"""Overlay escurecendo gradualmente (morte)."""

from __future__ import annotations

import pygame

DEFAULT_DURATION_MS = 800
MAX_ALPHA = 180


class DeathFade:
    """Overlay preto semi-transparente que cobre o card gradualmente."""

    def __init__(
        self,
        *,
        x: int,
        y: int,
        width: int,
        height: int,
        duration_ms: int = DEFAULT_DURATION_MS,
    ) -> None:
        self.blocking = False
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
        """Desenha overlay preto com alpha crescente."""
        if self.is_done:
            return
        overlay = pygame.Surface((self._width, self._height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, self.alpha))
        surface.blit(overlay, (self._x, self._y))

    @property
    def is_done(self) -> bool:
        """True quando a animacao terminou."""
        return self._elapsed >= self._duration_ms

    @property
    def alpha(self) -> int:
        """Opacidade atual (0 -> MAX_ALPHA)."""
        if self._duration_ms == 0:
            return MAX_ALPHA
        progress = self._elapsed / self._duration_ms
        return int(MAX_ALPHA * progress)
