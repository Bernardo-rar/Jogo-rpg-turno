"""Painel scrollavel de combat log."""

from __future__ import annotations

import pygame

from src.ui import colors, layout

_PADDING_X = 12
_PADDING_Y = 8


class CombatLogPanel:
    """Exibe as ultimas N linhas do combat log com cores."""

    def __init__(self, max_visible: int = layout.LOG_MAX_VISIBLE) -> None:
        self._lines: list[tuple[str, tuple]] = []
        self._max_visible = max_visible

    @property
    def max_visible(self) -> int:
        return self._max_visible

    @property
    def line_count(self) -> int:
        return len(self._lines)

    def add_line(self, text: str, color: tuple = colors.TEXT_WHITE) -> None:
        """Adiciona uma linha ao log."""
        self._lines.append((text, color))

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Renderiza o painel com as linhas mais recentes."""
        panel = pygame.Rect(
            layout.LOG_PANEL_X, layout.LOG_PANEL_Y,
            layout.LOG_PANEL_WIDTH, layout.LOG_PANEL_HEIGHT,
        )
        pygame.draw.rect(surface, colors.BG_PANEL, panel, border_radius=4)
        pygame.draw.rect(surface, colors.BG_PANEL_BORDER, panel, 1, 4)
        visible = self._lines[-self._max_visible:]
        x = layout.LOG_PANEL_X + _PADDING_X
        y = layout.LOG_PANEL_Y + _PADDING_Y
        for text, color in visible:
            rendered = font.render(text, True, color)
            surface.blit(rendered, (x, y))
            y += layout.LOG_LINE_HEIGHT
