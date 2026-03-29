"""MultiSlash — three staggered diagonal slashes + spark debris."""

from __future__ import annotations

import math
import random

import pygame

DURATION_MS = 350
LINE_WIDTH = 3
SLASH_COLORS = [(255, 255, 200), (220, 220, 180), (200, 200, 160)]
SPARK_COUNT = 8
SPARK_LIFETIME = 200


class MultiSlash:
    """Three diagonal slashes with staggered timing + spark particles."""

    def __init__(
        self, *, x: int, y: int, width: int, height: int,
    ) -> None:
        self.blocking = True
        self._x = x
        self._y = y
        self._w = width
        self._h = height
        self._elapsed = 0
        cx = x + width // 2
        cy = y + height // 2
        self._slashes = [
            _Slash(x, y, x + width, y + height, 0, 120),
            _Slash(x + width, y, x, y + height, 60, 180),
            _Slash(x, cy, x + width, cy, 100, 250),
        ]
        self._sparks = [
            _Spark(cx, cy) for _ in range(SPARK_COUNT)
        ]

    def update(self, dt_ms: int) -> None:
        self._elapsed += dt_ms
        for spark in self._sparks:
            spark.update(dt_ms, self._elapsed)

    def draw(self, surface: pygame.Surface) -> None:
        if self.is_done:
            return
        alpha_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        for i, slash in enumerate(self._slashes):
            color = SLASH_COLORS[i % len(SLASH_COLORS)]
            slash.draw(alpha_surf, self._elapsed, color)
        for spark in self._sparks:
            spark.draw(alpha_surf, self._elapsed)
        surface.blit(alpha_surf, (0, 0))

    @property
    def is_done(self) -> bool:
        return self._elapsed >= DURATION_MS


class _Slash:
    """A single animated slash line."""

    def __init__(
        self, x0: int, y0: int, x1: int, y1: int,
        start_ms: int, end_ms: int,
    ) -> None:
        self._x0, self._y0 = x0, y0
        self._x1, self._y1 = x1, y1
        self._start = start_ms
        self._end = end_ms

    def draw(
        self, surface: pygame.Surface, elapsed: int,
        color: tuple,
    ) -> None:
        if elapsed < self._start or elapsed > self._end + 50:
            return
        t = min(1.0, (elapsed - self._start) / max(1, self._end - self._start))
        ex = int(self._x0 + (self._x1 - self._x0) * t)
        ey = int(self._y0 + (self._y1 - self._y0) * t)
        fade = max(0, int(255 * (1.0 - max(0, elapsed - self._end) / 50)))
        pygame.draw.line(
            surface, (*color, fade),
            (self._x0, self._y0), (ex, ey), LINE_WIDTH,
        )


class _Spark:
    """A small spark particle from the slash intersection."""

    def __init__(self, cx: int, cy: int) -> None:
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(0.05, 0.15)
        self._x = float(cx)
        self._y = float(cy)
        self._vx = math.cos(angle) * speed
        self._vy = math.sin(angle) * speed
        self._age = 0
        self._spawn_at = 150

    def update(self, dt_ms: int, elapsed: int) -> None:
        if elapsed < self._spawn_at:
            return
        self._age += dt_ms
        self._x += self._vx * dt_ms
        self._y += self._vy * dt_ms

    def draw(self, surface: pygame.Surface, elapsed: int) -> None:
        if elapsed < self._spawn_at or self._age > SPARK_LIFETIME:
            return
        alpha = max(0, int(255 * (1 - self._age / SPARK_LIFETIME)))
        color = (255, 255, 200, alpha)
        x, y = int(self._x), int(self._y)
        pygame.draw.line(surface, color, (x - 2, y), (x + 2, y), 1)
        pygame.draw.line(surface, color, (x, y - 2), (x, y + 2), 1)
