"""Indicador visual de alvo — borda pulsante no card do alvo selecionado."""

from __future__ import annotations

import math

import pygame

from src.ui import colors, layout

PULSE_SPEED = 4.0
ALPHA_MIN = 0.5
ALPHA_MAX = 1.0
BORDER_WIDTH = 3
TARGET_COLOR = (255, 220, 50)


def draw_target_indicator(
    surface: pygame.Surface,
    card_rect: tuple[int, int, int, int],
    elapsed_ms: int,
) -> None:
    """Desenha borda amarela pulsante ao redor do card alvo."""
    alpha = _pulse_alpha(elapsed_ms)
    x, y, w, h = card_rect
    outer = pygame.Rect(
        x - BORDER_WIDTH, y - BORDER_WIDTH,
        w + BORDER_WIDTH * 2, h + BORDER_WIDTH * 2,
    )
    color = _apply_alpha(TARGET_COLOR, alpha)
    pygame.draw.rect(surface, color, outer, BORDER_WIDTH, border_radius=8)


def _pulse_alpha(elapsed_ms: int) -> float:
    """Calcula alpha pulsante entre ALPHA_MIN e ALPHA_MAX."""
    seconds = elapsed_ms / 1000.0
    wave = math.sin(seconds * PULSE_SPEED)
    return ALPHA_MIN + (ALPHA_MAX - ALPHA_MIN) * (0.5 + 0.5 * wave)


def _apply_alpha(
    base_color: tuple[int, ...], alpha: float,
) -> tuple[int, int, int]:
    """Aplica alpha multiplicativo a uma cor RGB."""
    return (
        int(base_color[0] * alpha),
        int(base_color[1] * alpha),
        int(base_color[2] * alpha),
    )
