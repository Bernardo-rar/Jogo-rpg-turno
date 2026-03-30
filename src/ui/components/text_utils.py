"""Shared text drawing utilities for UI scenes."""

from __future__ import annotations

import pygame


def draw_centered(
    surface: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    x: int,
    y: int,
    color: tuple[int, int, int],
) -> None:
    """Renders *text* centered on (x, y)."""
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=(x, y))
    surface.blit(rendered, rect)
