"""Texto flutuante com fade (numeros de dano/heal)."""

from __future__ import annotations

import pygame

FLOAT_DISTANCE = 30
MAX_ALPHA = 255
DEFAULT_DURATION_MS = 800


class FloatingText:
    """Texto que sobe e desaparece gradualmente."""

    def __init__(
        self,
        text: str,
        *,
        x: int,
        y: int,
        color: tuple,
        duration_ms: int = DEFAULT_DURATION_MS,
    ) -> None:
        self.text = text
        self.color = color
        self.blocking = False
        self._x = x
        self._start_y = y
        self._duration_ms = duration_ms
        self._elapsed = 0

    def update(self, dt_ms: int) -> None:
        """Avanca tempo da animacao."""
        self._elapsed = min(self._elapsed + dt_ms, self._duration_ms)

    def draw(self, surface: pygame.Surface) -> None:
        """Desenha texto com alpha na posicao atual."""
        if self.is_done:
            return
        alpha_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        color_with_alpha = (*self.color, self.alpha)
        font = pygame.font.SysFont(None, 24)
        rendered = font.render(self.text, True, color_with_alpha)
        alpha_surface.blit(rendered, (self._x, self.current_y))
        surface.blit(alpha_surface, (0, 0))

    @property
    def is_done(self) -> bool:
        """True quando a animacao terminou."""
        return self._elapsed >= self._duration_ms

    @property
    def current_y(self) -> float:
        """Posicao Y atual (sobe com o tempo)."""
        progress = self._elapsed / self._duration_ms
        return self._start_y - FLOAT_DISTANCE * progress

    @property
    def alpha(self) -> int:
        """Opacidade atual (255 -> 0)."""
        progress = self._elapsed / self._duration_ms
        return int(MAX_ALPHA * (1.0 - progress))
