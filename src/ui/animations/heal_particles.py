"""Particulas verdes subindo (animacao de cura)."""

from __future__ import annotations

import random

import pygame

DEFAULT_DURATION_MS = 400
NUM_PARTICLES = 10
PARTICLE_RADIUS = 4
PARTICLE_COLOR = (80, 255, 80)
MAX_ALPHA = 220
RISE_SPEED = 0.06


class HealParticles:
    """Particulas verdes que sobem a partir da base do card."""

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
        self._particles = _create_particles(x, y, width, height)

    def update(self, dt_ms: int) -> None:
        """Avanca tempo e move particulas."""
        self._elapsed = min(self._elapsed + dt_ms, self._duration_ms)
        for p in self._particles:
            p["y"] -= p["speed"] * dt_ms * RISE_SPEED

    def draw(self, surface: pygame.Surface) -> None:
        """Desenha particulas com fade."""
        if self.is_done:
            return
        progress = self._elapsed / self._duration_ms
        alpha = int(MAX_ALPHA * (1.0 - progress))
        alpha_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        color = (*PARTICLE_COLOR, alpha)
        for p in self._particles:
            pos = (int(p["x"]), int(p["y"]))
            pygame.draw.circle(alpha_surface, color, pos, p["radius"])
        surface.blit(alpha_surface, (0, 0))

    @property
    def is_done(self) -> bool:
        """True quando a animacao terminou."""
        return self._elapsed >= self._duration_ms

    @property
    def particle_count(self) -> int:
        """Numero de particulas."""
        return len(self._particles)


def _create_particles(
    x: int, y: int, width: int, height: int,
) -> list[dict]:
    particles = []
    for _ in range(NUM_PARTICLES):
        particles.append({
            "x": x + random.randint(0, width),
            "y": y + height - random.randint(0, height // 3),
            "speed": 0.5 + random.random() * 0.5,
            "radius": random.randint(2, PARTICLE_RADIUS),
        })
    return particles
