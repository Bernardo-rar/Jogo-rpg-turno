"""Boss mechanic indicators — empower bar, charge text, field overlay."""

from __future__ import annotations

import pygame

from src.ui import colors

EMPOWER_BAR_W = 80
EMPOWER_BAR_H = 6
EMPOWER_COLOR = (255, 165, 0)
EMPOWER_ACTIVE_COLOR = (255, 50, 50)
EMPOWER_BG = (40, 40, 40)

CHARGE_COLOR = (255, 200, 50)
FIELD_COLOR = (200, 100, 50)
FIELD_BG_ALPHA = 40


def draw_empower_bar(
    surface: pygame.Surface,
    card_rect: tuple[int, int, int, int],
    current: int,
    max_value: int,
    is_empowered: bool,
    font: pygame.font.Font,
) -> None:
    """Draws a small empower bar below the boss card."""
    x, y, w, h = card_rect
    bar_x = x + (w - EMPOWER_BAR_W) // 2
    bar_y = y + h + 2
    pygame.draw.rect(
        surface, EMPOWER_BG,
        (bar_x, bar_y, EMPOWER_BAR_W, EMPOWER_BAR_H),
    )
    if max_value > 0:
        fill_w = int(EMPOWER_BAR_W * current / max_value)
        bar_color = EMPOWER_ACTIVE_COLOR if is_empowered else EMPOWER_COLOR
        pygame.draw.rect(
            surface, bar_color,
            (bar_x, bar_y, fill_w, EMPOWER_BAR_H),
        )
    if is_empowered:
        text = font.render("EMPOWERED", True, EMPOWER_ACTIVE_COLOR)
        tx = x + (w - text.get_width()) // 2
        surface.blit(text, (tx, bar_y + EMPOWER_BAR_H + 1))


def draw_charge_indicator(
    surface: pygame.Surface,
    card_rect: tuple[int, int, int, int],
    message: str,
    font: pygame.font.Font,
) -> None:
    """Draws a 'CHARGING!' text above the boss card."""
    x, y, w, _h = card_rect
    text = font.render(message, True, CHARGE_COLOR)
    tx = x + (w - text.get_width()) // 2
    ty = y - text.get_height() - 2
    surface.blit(text, (tx, ty))


def draw_field_overlay(
    surface: pygame.Surface,
    field_name: str,
    font: pygame.font.Font,
    window_w: int,
) -> None:
    """Draws a field effect name at the top of the screen."""
    text = font.render(f"Field: {field_name}", True, FIELD_COLOR)
    tx = (window_w - text.get_width()) // 2
    surface.blit(text, (tx, 4))
