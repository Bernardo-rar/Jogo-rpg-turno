"""Painel scrollavel de combat log com tags coloridas e fade."""

from __future__ import annotations

from dataclasses import dataclass

import pygame

from src.ui import colors, layout

_PADDING_X = 12
_PADDING_Y = 8
_MIN_ALPHA_RATIO = 0.4


@dataclass(frozen=True)
class LogEntry:
    """Single log line with optional tag coloring."""

    tag: str
    tag_color: tuple[int, int, int]
    message: str
    message_color: tuple[int, int, int] = colors.TEXT_WHITE


class CombatLogPanel:
    """Exibe combat log com scroll, tags e fade alpha."""

    def __init__(self, max_visible: int = layout.LOG_MAX_VISIBLE) -> None:
        self._entries: list[LogEntry] = []
        self._max_visible = max_visible
        self._scroll_offset: int = 0

    @property
    def max_visible(self) -> int:
        return self._max_visible

    @property
    def line_count(self) -> int:
        return len(self._entries)

    def add_line(self, text: str, color: tuple = colors.TEXT_WHITE) -> None:
        """Adds a plain text line (backward compat)."""
        self._entries.append(LogEntry(
            tag="", tag_color=color, message=text, message_color=color,
        ))
        self._scroll_offset = 0

    def add_entry(self, entry: LogEntry) -> None:
        """Adds a structured log entry."""
        self._entries.append(entry)
        self._scroll_offset = 0

    def scroll_up(self) -> None:
        """Scrolls up by max_visible lines."""
        max_offset = max(0, len(self._entries) - self._max_visible)
        self._scroll_offset = min(
            self._scroll_offset + self._max_visible, max_offset,
        )

    def scroll_down(self) -> None:
        """Scrolls down (toward newest)."""
        self._scroll_offset = max(0, self._scroll_offset - self._max_visible)

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Renderiza o painel com scroll e fade alpha."""
        panel = pygame.Rect(
            layout.LOG_PANEL_X, layout.LOG_PANEL_Y,
            layout.LOG_PANEL_WIDTH, layout.LOG_PANEL_HEIGHT,
        )
        pygame.draw.rect(surface, colors.BG_PANEL, panel, border_radius=4)
        pygame.draw.rect(surface, colors.BG_PANEL_BORDER, panel, 1, 4)
        visible = self._get_visible_entries()
        x = layout.LOG_PANEL_X + _PADDING_X
        y = layout.LOG_PANEL_Y + _PADDING_Y
        n = len(visible)
        for i, entry in enumerate(visible):
            alpha = _line_alpha(i, n)
            _draw_log_line(surface, x, y, entry, font, alpha)
            y += layout.LOG_LINE_HEIGHT
        self._draw_scroll_hints(surface, font)

    def _get_visible_entries(self) -> list[LogEntry]:
        end = len(self._entries) - self._scroll_offset
        start = max(0, end - self._max_visible)
        return self._entries[start:end]

    def _draw_scroll_hints(
        self, surface: pygame.Surface, font: pygame.font.Font,
    ) -> None:
        """Draws scroll indicators if content extends beyond view."""
        total = len(self._entries)
        if total <= self._max_visible:
            return
        rx = layout.LOG_PANEL_X + layout.LOG_PANEL_WIDTH - 16
        if self._scroll_offset > 0:
            hint = font.render("v", True, colors.TEXT_MUTED)
            surface.blit(hint, (rx, layout.LOG_PANEL_Y + layout.LOG_PANEL_HEIGHT - 16))
        max_offset = total - self._max_visible
        if self._scroll_offset < max_offset:
            hint = font.render("^", True, colors.TEXT_MUTED)
            surface.blit(hint, (rx, layout.LOG_PANEL_Y + 4))


def _line_alpha(index: int, total: int) -> int:
    """Computes alpha for a line. Oldest=40%, newest=100%."""
    if total <= 1:
        return 255
    ratio = _MIN_ALPHA_RATIO + (1.0 - _MIN_ALPHA_RATIO) * (index / (total - 1))
    return int(255 * ratio)


def _draw_log_line(
    surface: pygame.Surface,
    x: int, y: int,
    entry: LogEntry,
    font: pygame.font.Font,
    alpha: int,
) -> None:
    """Renders a log line with tag in accent color + message."""
    line_surf = pygame.Surface(
        (layout.LOG_PANEL_WIDTH - _PADDING_X * 2, layout.LOG_LINE_HEIGHT),
        pygame.SRCALPHA,
    )
    cx = 0
    if entry.tag:
        tag_color = (*entry.tag_color, alpha)
        tag_render = font.render(entry.tag + " ", True, tag_color)
        line_surf.blit(tag_render, (cx, 0))
        cx += tag_render.get_width()
    msg_color = (*entry.message_color, alpha)
    msg_render = font.render(entry.message, True, msg_color)
    line_surf.blit(msg_render, (cx, 0))
    surface.blit(line_surf, (x, y))
