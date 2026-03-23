"""MainMenuScene — tela inicial simples."""

from __future__ import annotations

from typing import Callable

import pygame

from src.ui import colors, layout
from src.ui.font_manager import FontManager

_TITLE = "RPG TURNO"
_SUBTITLE = "Dungeon Roguelite"
_OPTION_PLAY = "[1] Jogar"
_OPTION_QUIT = "[ESC] Sair"


class MainMenuScene:
    """Tela de menu principal."""

    def __init__(
        self,
        fonts: FontManager,
        on_complete: Callable[[dict], None],
    ) -> None:
        self._fonts = fonts
        self._on_complete = on_complete
        self._done = False

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_1, pygame.K_RETURN):
            self._done = True
            self._on_complete({"action": "play"})
        elif event.key == pygame.K_ESCAPE:
            self._done = True

    def update(self, dt_ms: int) -> bool:
        return not self._done

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(colors.BG_DARK)
        cx = layout.WINDOW_WIDTH // 2
        _draw_centered(
            surface, self._fonts.large, _TITLE,
            cx, 200, colors.TEXT_WHITE,
        )
        _draw_centered(
            surface, self._fonts.medium, _SUBTITLE,
            cx, 260, colors.TEXT_MUTED,
        )
        _draw_centered(
            surface, self._fonts.medium, _OPTION_PLAY,
            cx, 400, colors.TEXT_YELLOW,
        )
        _draw_centered(
            surface, self._fonts.small, _OPTION_QUIT,
            cx, 450, colors.TEXT_MUTED,
        )


def _draw_centered(
    surface: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    x: int,
    y: int,
    color: tuple[int, int, int],
) -> None:
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=(x, y))
    surface.blit(rendered, rect)
