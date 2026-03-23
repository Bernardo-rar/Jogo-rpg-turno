"""GameOverScene — tela de derrota."""

from __future__ import annotations

from typing import Callable

import pygame

from src.ui import colors, layout
from src.ui.font_manager import FontManager


class GameOverScene:
    """Tela de game over com stats da run."""

    def __init__(
        self,
        fonts: FontManager,
        rooms_cleared: int,
        on_complete: Callable[[dict], None],
    ) -> None:
        self._fonts = fonts
        self._rooms = rooms_cleared
        self._on_complete = on_complete

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self._on_complete({})

    def update(self, dt_ms: int) -> bool:
        return True

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(colors.BG_DARK)
        cx = layout.WINDOW_WIDTH // 2
        _centered(surface, self._fonts.large, "GAME OVER", cx, 250, colors.TEXT_DAMAGE)
        _centered(
            surface, self._fonts.medium,
            f"Salas conquistadas: {self._rooms}",
            cx, 340, colors.TEXT_WHITE,
        )
        _centered(
            surface, self._fonts.small,
            "[ENTER] Menu Principal", cx, 450, colors.TEXT_MUTED,
        )


def _centered(surface, font, text, x, y, color):
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=(x, y))
    surface.blit(rendered, rect)
