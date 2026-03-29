"""Particle system — lightweight particles for elemental effects."""

from __future__ import annotations

import math
import random

import pygame

from dataclasses import dataclass


@dataclass
class Particle:
    """Single particle with position, velocity, lifetime."""

    x: float
    y: float
    vx: float
    vy: float
    lifetime_ms: int
    elapsed_ms: int = 0
    color: tuple[int, int, int] = (255, 255, 255)
    size: float = 3.0
    size_decay: float = 0.5
    gravity: float = 0.0
    shape: str = "circle"

    @property
    def is_alive(self) -> bool:
        return self.elapsed_ms < self.lifetime_ms

    @property
    def progress(self) -> float:
        if self.lifetime_ms <= 0:
            return 1.0
        return min(self.elapsed_ms / self.lifetime_ms, 1.0)

    @property
    def alpha(self) -> int:
        return max(0, int(255 * (1.0 - self.progress)))

    @property
    def current_size(self) -> float:
        decay = 1.0 - self.progress * (1.0 - self.size_decay)
        return max(0.5, self.size * decay)

    def update(self, dt_ms: int) -> None:
        self.x += self.vx * dt_ms
        self.y += self.vy * dt_ms
        self.vy += self.gravity * dt_ms
        self.elapsed_ms += dt_ms

    def draw(self, surface: pygame.Surface) -> None:
        if not self.is_alive:
            return
        alpha = self.alpha
        if alpha <= 0:
            return
        sz = int(self.current_size)
        if sz <= 0:
            return
        color = (*self.color, alpha)
        if self.shape == "diamond":
            _draw_diamond(surface, int(self.x), int(self.y), sz, color)
        elif self.shape == "spark":
            _draw_spark(surface, int(self.x), int(self.y), sz, color)
        else:
            _draw_circle(surface, int(self.x), int(self.y), sz, color)


@dataclass(frozen=True)
class ParticleConfig:
    """Data-driven config for a particle emitter."""

    name: str
    count: int
    duration_ms: int
    lifetime_range: tuple[int, int]
    speed_range: tuple[float, float]
    angle_range: tuple[float, float]
    size_range: tuple[float, float]
    size_decay: float
    colors: list[tuple[int, int, int]]
    gravity: float
    shape: str
    spawn_area: str
    blocking: bool = True


class ParticleEmitter:
    """Spawns and manages particles from a config."""

    def __init__(
        self, config: ParticleConfig, rect: tuple[int, int, int, int],
    ) -> None:
        self.blocking = config.blocking
        self._config = config
        self._rect = rect
        self._elapsed = 0
        self._particles = _spawn_particles(config, rect)

    def update(self, dt_ms: int) -> None:
        self._elapsed += dt_ms
        for p in self._particles:
            p.update(dt_ms)

    def draw(self, surface: pygame.Surface) -> None:
        alpha_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        for p in self._particles:
            p.draw(alpha_surf)
        surface.blit(alpha_surf, (0, 0))

    @property
    def is_done(self) -> bool:
        return self._elapsed >= self._config.duration_ms


def _spawn_particles(
    config: ParticleConfig,
    rect: tuple[int, int, int, int],
) -> list[Particle]:
    x, y, w, h = rect
    cx, cy = x + w // 2, y + h // 2
    particles = []
    for _ in range(config.count):
        sx, sy = _spawn_pos(config.spawn_area, x, y, w, h, cx, cy)
        angle = random.uniform(*config.angle_range)
        speed = random.uniform(*config.speed_range)
        rad = math.radians(angle)
        vx = math.cos(rad) * speed
        vy = math.sin(rad) * speed
        lifetime = random.randint(*config.lifetime_range)
        size = random.uniform(*config.size_range)
        color = random.choice(config.colors)
        particles.append(Particle(
            x=sx, y=sy, vx=vx, vy=vy,
            lifetime_ms=lifetime, color=color,
            size=size, size_decay=config.size_decay,
            gravity=config.gravity, shape=config.shape,
        ))
    return particles


def _spawn_pos(
    area: str, x: int, y: int, w: int, h: int,
    cx: int, cy: int,
) -> tuple[float, float]:
    if area == "center":
        return cx + random.uniform(-5, 5), cy + random.uniform(-5, 5)
    if area == "bottom":
        return (
            x + random.uniform(0, w),
            y + h - random.uniform(0, 5),
        )
    if area == "edges":
        side = random.choice(["left", "right", "top", "bottom"])
        if side == "left":
            return float(x), y + random.uniform(0, h)
        if side == "right":
            return float(x + w), y + random.uniform(0, h)
        if side == "top":
            return x + random.uniform(0, w), float(y)
        return x + random.uniform(0, w), float(y + h)
    return (
        x + random.uniform(0, w),
        y + random.uniform(0, h),
    )


def _draw_circle(
    surface: pygame.Surface,
    x: int, y: int, size: int,
    color: tuple,
) -> None:
    pygame.draw.circle(surface, color, (x, y), max(1, size))


def _draw_diamond(
    surface: pygame.Surface,
    x: int, y: int, size: int,
    color: tuple,
) -> None:
    s = max(1, size)
    points = [(x, y - s), (x + s, y), (x, y + s), (x - s, y)]
    pygame.draw.polygon(surface, color, points)


def _draw_spark(
    surface: pygame.Surface,
    x: int, y: int, size: int,
    color: tuple,
) -> None:
    s = max(1, size)
    pygame.draw.line(surface, color, (x - s, y), (x + s, y), 1)
    pygame.draw.line(surface, color, (x, y - s), (x, y + s), 1)
