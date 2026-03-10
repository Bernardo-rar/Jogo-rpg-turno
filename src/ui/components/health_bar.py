"""Componente de barra de HP/Mana."""

from __future__ import annotations

import pygame

from src.ui import colors, layout

_TEXT_PADDING_X = 4
_TEXT_PADDING_Y = -2


def draw_bar(
    surface: pygame.Surface,
    x: int, y: int,
    current: int, maximum: int,
    fill_color: tuple, font: pygame.font.Font,
) -> None:
    """Desenha barra horizontal com fundo, preenchimento e texto."""
    bg_rect = pygame.Rect(x, y, layout.BAR_WIDTH, layout.BAR_HEIGHT)
    pygame.draw.rect(surface, colors.HP_BG, bg_rect)
    if maximum > 0:
        fill_w = int(layout.BAR_WIDTH * current / maximum)
        fill_rect = pygame.Rect(x, y, fill_w, layout.BAR_HEIGHT)
        pygame.draw.rect(surface, fill_color, fill_rect)
    text = f"{current}/{maximum}"
    rendered = font.render(text, True, colors.TEXT_WHITE)
    surface.blit(rendered, (x + _TEXT_PADDING_X, y + _TEXT_PADDING_Y))


def draw_hp_bar(
    surface: pygame.Surface,
    x: int, y: int,
    current_hp: int, max_hp: int,
    font: pygame.font.Font,
) -> None:
    """Desenha barra de HP (verde se >50%, vermelho se <=50%)."""
    ratio = current_hp / max_hp if max_hp > 0 else 0
    color = colors.HP_GREEN if ratio > 0.5 else colors.HP_RED
    draw_bar(surface, x, y, current_hp, max_hp, color, font)


def draw_mana_bar(
    surface: pygame.Surface,
    x: int, y: int,
    current_mana: int, max_mana: int,
    font: pygame.font.Font,
) -> None:
    """Desenha barra de Mana (azul)."""
    draw_bar(surface, x, y, current_mana, max_mana, colors.MANA_BLUE, font)
