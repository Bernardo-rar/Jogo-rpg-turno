"""Offset oscilante para tremer o card ao receber dano."""

from __future__ import annotations

import math

DEFAULT_DURATION_MS = 300
DEFAULT_INTENSITY = 6
SHAKE_CYCLES = 4


class CardShake:
    """Produz offset (dx, dy) oscilante para o card do alvo."""

    def __init__(
        self,
        *,
        target_name: str,
        intensity: int = DEFAULT_INTENSITY,
        duration_ms: int = DEFAULT_DURATION_MS,
    ) -> None:
        self.blocking = True
        self.target_name = target_name
        self._intensity = intensity
        self._duration_ms = duration_ms
        self._elapsed = 0

    def update(self, dt_ms: int) -> None:
        """Avanca tempo da animacao."""
        self._elapsed = min(self._elapsed + dt_ms, self._duration_ms)

    def draw(self, surface: object) -> None:
        """Noop — efeito e aplicado via offset property."""

    @property
    def is_done(self) -> bool:
        """True quando a animacao terminou."""
        return self._elapsed >= self._duration_ms

    @property
    def offset(self) -> tuple[int, int]:
        """Offset atual (dx, dy) para aplicar no card."""
        if self.is_done:
            return (0, 0)
        progress = self._elapsed / self._duration_ms
        decay = 1.0 - progress
        phase = progress * SHAKE_CYCLES * math.pi * 2
        shake = math.sin(phase)
        displacement = int(self._intensity * shake * decay)
        return (displacement, displacement // 2)
