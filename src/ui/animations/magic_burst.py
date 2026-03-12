"""Circulos concentricos expandindo (ataque magico)."""

from __future__ import annotations

import pygame

DEFAULT_DURATION_MS = 500
MAX_RADIUS = 40
MAX_ALPHA = 255
NUM_RINGS = 3


class MagicBurst:
    """Circulos concentricos que expandem do centro do card."""

    def __init__(
        self,
        *,
        cx: int,
        cy: int,
        color: tuple,
        duration_ms: int = DEFAULT_DURATION_MS,
    ) -> None:
        self.blocking = True
        self.color = color
        self._cx = cx
        self._cy = cy
        self._duration_ms = duration_ms
        self._elapsed = 0

    def update(self, dt_ms: int) -> None:
        """Avanca tempo da animacao."""
        self._elapsed = min(self._elapsed + dt_ms, self._duration_ms)

    def draw(self, surface: pygame.Surface) -> None:
        """Desenha circulos concentricos com fade."""
        if self.is_done:
            return
        alpha_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        color_with_alpha = (*self.color, self.alpha)
        progress = self._progress
        for i in range(NUM_RINGS):
            scale = 1.0 - i * 0.3
            radius = max(1, int(progress * MAX_RADIUS * scale))
            pygame.draw.circle(
                alpha_surface, color_with_alpha, (self._cx, self._cy), radius, 2,
            )
        surface.blit(alpha_surface, (0, 0))

    @property
    def is_done(self) -> bool:
        """True quando a animacao terminou."""
        return self._elapsed >= self._duration_ms

    @property
    def current_radius(self) -> float:
        """Raio do circulo principal."""
        return self._progress * MAX_RADIUS

    @property
    def alpha(self) -> int:
        """Opacidade atual (255 -> 0)."""
        return int(MAX_ALPHA * (1.0 - self._progress))

    @property
    def _progress(self) -> float:
        if self._duration_ms == 0:
            return 1.0
        return min(self._elapsed / self._duration_ms, 1.0)
