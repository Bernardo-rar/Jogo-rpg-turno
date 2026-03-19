"""Indicador visual de turno — borda pulsante no card do personagem ativo."""

from __future__ import annotations

import math

import pygame

from src.ui import colors, layout


def draw_turn_indicator(
    surface: pygame.Surface,
    card_rect: tuple[int, int, int, int],
    elapsed_ms: int,
) -> None:
    """Desenha borda pulsante ao redor do card ativo."""
    alpha = _pulse_alpha(elapsed_ms)
    x, y, w, h = card_rect
    border = layout.TURN_INDICATOR_BORDER
    outer = pygame.Rect(
        x - border, y - border,
        w + border * 2, h + border * 2,
    )
    color = _apply_alpha(colors.HIGHLIGHT_ACTIVE, alpha)
    pygame.draw.rect(surface, color, outer, border, border_radius=8)


def _pulse_alpha(elapsed_ms: int) -> float:
    """Calcula alpha pulsante entre 0.4 e 1.0 usando seno."""
    seconds = elapsed_ms / 1000.0
    wave = math.sin(seconds * layout.TURN_INDICATOR_PULSE_SPEED)
    return 0.7 + 0.3 * wave


def _apply_alpha(
    base_color: tuple[int, ...], alpha: float,
) -> tuple[int, int, int]:
    """Aplica alpha multiplicativo a uma cor RGB."""
    return (
        int(base_color[0] * alpha),
        int(base_color[1] * alpha),
        int(base_color[2] * alpha),
    )
