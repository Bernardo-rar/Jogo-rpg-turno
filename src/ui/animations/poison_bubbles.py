"""Bolhas roxas oscilando (DoT tick)."""

from __future__ import annotations

import math
import random

import pygame

DEFAULT_DURATION_MS = 500
NUM_BUBBLES = 6
BUBBLE_COLOR = (180, 140, 255)
MAX_ALPHA = 200
RISE_SPEED = 0.04
OSCILLATION_AMP = 8
OSCILLATION_FREQ = 0.008


class PoisonBubbles:
    """Bolhas roxas que sobem oscilando ao redor do card."""

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
        self._duration_ms = duration_ms
        self._elapsed = 0
        self._bubbles = _create_bubbles(x, y, width, height)

    def update(self, dt_ms: int) -> None:
        """Avanca tempo e move bolhas."""
        self._elapsed = min(self._elapsed + dt_ms, self._duration_ms)
        for b in self._bubbles:
            b["y"] -= b["speed"] * dt_ms * RISE_SPEED
            b["x_offset"] = math.sin(self._elapsed * OSCILLATION_FREQ + b["phase"]) * OSCILLATION_AMP

    def draw(self, surface: pygame.Surface) -> None:
        """Desenha bolhas com fade."""
        if self.is_done:
            return
        progress = self._elapsed / self._duration_ms
        alpha = int(MAX_ALPHA * (1.0 - progress))
        alpha_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        color = (*BUBBLE_COLOR, alpha)
        for b in self._bubbles:
            pos = (int(b["base_x"] + b["x_offset"]), int(b["y"]))
            pygame.draw.circle(alpha_surface, color, pos, b["radius"])
        surface.blit(alpha_surface, (0, 0))

    @property
    def is_done(self) -> bool:
        """True quando a animacao terminou."""
        return self._elapsed >= self._duration_ms

    @property
    def bubble_count(self) -> int:
        """Numero de bolhas."""
        return len(self._bubbles)


def _create_bubbles(x: int, y: int, width: int, height: int) -> list[dict]:
    bubbles = []
    for _ in range(NUM_BUBBLES):
        bx = x + random.randint(0, width)
        bubbles.append({
            "base_x": bx,
            "x_offset": 0.0,
            "y": y + height - random.randint(0, height // 4),
            "speed": 0.5 + random.random() * 0.5,
            "radius": random.randint(3, 6),
            "phase": random.random() * math.pi * 2,
        })
    return bubbles
