"""FadeTransition — fade out da cena atual, fade in da proxima."""

from __future__ import annotations

from enum import Enum, auto
from typing import TYPE_CHECKING

import pygame

from src.ui import colors, layout

if TYPE_CHECKING:
    from src.ui.scenes.scene import Scene

_DEFAULT_FADE_MS = 400


class _Phase(Enum):
    FADE_OUT = auto()
    FADE_IN = auto()
    DONE = auto()


class FadeTransition:
    """Transicao com fade out/in entre duas cenas.

    Satisfaz o Scene Protocol: handle_event, update, draw.
    """

    def __init__(
        self,
        old_scene: Scene,
        new_scene: Scene,
        on_done: object,
        fade_ms: int = _DEFAULT_FADE_MS,
    ) -> None:
        self._old = old_scene
        self._new = new_scene
        self._on_done = on_done
        self._fade_ms = fade_ms
        self._phase = _Phase.FADE_OUT
        self._elapsed = 0
        self._overlay = pygame.Surface(
            (layout.WINDOW_WIDTH, layout.WINDOW_HEIGHT),
            pygame.SRCALPHA,
        )

    def handle_event(self, event: pygame.event.Event) -> None:
        """Ignora input durante a transicao."""
        pass

    def update(self, dt_ms: int) -> bool:
        self._elapsed += dt_ms
        if self._phase == _Phase.FADE_OUT:
            if self._elapsed >= self._fade_ms:
                self._phase = _Phase.FADE_IN
                self._elapsed = 0
        elif self._phase == _Phase.FADE_IN:
            if self._elapsed >= self._fade_ms:
                self._phase = _Phase.DONE
                self._finish()
        return True

    def draw(self, surface: pygame.Surface) -> None:
        if self._phase == _Phase.FADE_OUT:
            self._old.draw(surface)
            alpha = _progress(self._elapsed, self._fade_ms)
            self._draw_overlay(surface, alpha)
        elif self._phase == _Phase.FADE_IN:
            self._new.draw(surface)
            alpha = 1.0 - _progress(self._elapsed, self._fade_ms)
            self._draw_overlay(surface, alpha)
        else:
            self._new.draw(surface)

    def _draw_overlay(self, surface: pygame.Surface, alpha: float) -> None:
        a = int(max(0, min(255, alpha * 255)))
        self._overlay.fill((0, 0, 0, a))
        surface.blit(self._overlay, (0, 0))

    def _finish(self) -> None:
        if callable(self._on_done):
            self._on_done()


def _progress(elapsed: int, total: int) -> float:
    """Progresso 0.0 -> 1.0 com clamp."""
    if total <= 0:
        return 1.0
    return min(1.0, elapsed / total)
