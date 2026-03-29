"""DefeatOverlay — dark red screen dim on defeat."""

from __future__ import annotations

import pygame

DURATION_MS = 1000
DIM_ALPHA = 180
PULSE_ALPHA = 60


class DefeatOverlay:
    """Dark overlay with red pulse on defeat."""

    def __init__(self, screen_w: int, screen_h: int) -> None:
        self.blocking = False
        self._elapsed = 0
        self._w = screen_w
        self._h = screen_h

    def update(self, dt_ms: int) -> None:
        self._elapsed += dt_ms

    def draw(self, surface: pygame.Surface) -> None:
        if self._elapsed > DURATION_MS:
            return
        overlay = pygame.Surface((self._w, self._h), pygame.SRCALPHA)
        t = min(1.0, self._elapsed / 200)
        alpha = int(DIM_ALPHA * t)
        overlay.fill((0, 0, 0, alpha))
        if 200 < self._elapsed < 400:
            pulse_t = (self._elapsed - 200) / 200
            pa = int(PULSE_ALPHA * (1.0 - abs(pulse_t * 2 - 1)))
            overlay.fill((80, 0, 0, pa), special_flags=pygame.BLEND_RGBA_ADD)
        surface.blit(overlay, (0, 0))

    @property
    def is_done(self) -> bool:
        return self._elapsed >= DURATION_MS
