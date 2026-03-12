"""Borda pulsante ao redor do card (buff/debuff)."""

from __future__ import annotations

import math

import pygame

DEFAULT_DURATION_MS = 600
BORDER_WIDTH = 3
PULSE_FREQ = 0.01
MAX_ALPHA = 180


class BuffAura:
    """Rect pulsante ao redor do card do personagem."""

    def __init__(
        self,
        *,
        x: int,
        y: int,
        width: int,
        height: int,
        color: tuple,
        duration_ms: int = DEFAULT_DURATION_MS,
    ) -> None:
        self.blocking = False
        self.color = color
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
        """Desenha borda pulsante com alpha oscilante."""
        if self.is_done:
            return
        pulse = (math.sin(self._elapsed * PULSE_FREQ * math.pi * 2) + 1) / 2
        alpha = int(MAX_ALPHA * pulse)
        alpha_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        color = (*self.color, alpha)
        rect = pygame.Rect(self._x - 2, self._y - 2, self._width + 4, self._height + 4)
        pygame.draw.rect(alpha_surface, color, rect, BORDER_WIDTH, border_radius=8)
        surface.blit(alpha_surface, (0, 0))

    @property
    def is_done(self) -> bool:
        """True quando a animacao terminou."""
        return self._elapsed >= self._duration_ms
