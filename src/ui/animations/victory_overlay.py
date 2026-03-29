"""VictoryOverlay — gold sparkle particles on victory."""

from __future__ import annotations

import pygame

from src.ui.animations.particle import ParticleConfig, ParticleEmitter

DURATION_MS = 1200

_SPARKLE_CONFIG = ParticleConfig(
    name="victory",
    count=30,
    duration_ms=DURATION_MS,
    lifetime_range=(600, 1000),
    speed_range=(0.02, 0.05),
    angle_range=(0, 360),
    size_range=(2, 4),
    size_decay=0.5,
    colors=[(255, 220, 80), (255, 240, 150), (255, 200, 50)],
    gravity=-0.00002,
    shape="diamond",
    spawn_area="center",
    blocking=False,
)


class VictoryOverlay:
    """Gold sparkle particles from screen center on victory."""

    def __init__(self, screen_w: int, screen_h: int) -> None:
        self.blocking = False
        self._elapsed = 0
        cx, cy = screen_w // 2, screen_h // 3
        rect = (cx - 50, cy - 50, 100, 100)
        self._emitter = ParticleEmitter(_SPARKLE_CONFIG, rect)

    def update(self, dt_ms: int) -> None:
        self._elapsed += dt_ms
        self._emitter.update(dt_ms)

    def draw(self, surface: pygame.Surface) -> None:
        self._emitter.draw(surface)

    @property
    def is_done(self) -> bool:
        return self._elapsed >= DURATION_MS
