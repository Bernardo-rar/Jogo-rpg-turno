"""Speed indicator — badge visual e logica de ciclo de velocidade."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from src.ui import colors, layout

if TYPE_CHECKING:
    from src.ui.font_manager import FontManager

SPEED_OPTIONS: tuple[float, ...] = (1.0, 2.0, 3.0)

_SPEED_COLORS: dict[float, tuple[int, int, int]] = {
    1.0: colors.TEXT_MUTED,
    2.0: colors.TEXT_YELLOW,
    3.0: (255, 140, 50),
}

_BG_ALPHA = 160


def next_speed_index(current: int) -> int:
    """Retorna proximo indice ciclico de velocidade."""
    return (current + 1) % len(SPEED_OPTIONS)


def _speed_label(speed: float) -> str:
    """Formata label de velocidade: '1x', '2x', '3x'."""
    return f"{int(speed)}x"


def _speed_color(speed: float) -> tuple[int, int, int]:
    """Retorna cor baseada na velocidade atual."""
    return _SPEED_COLORS.get(speed, colors.TEXT_WHITE)


def draw_speed_indicator(
    surface: pygame.Surface,
    speed_mult: float,
    fonts: FontManager,
) -> None:
    """Desenha badge de velocidade no canto superior direito."""
    _draw_background(surface)
    _draw_label(surface, speed_mult, fonts)


def _draw_background(surface: pygame.Surface) -> None:
    """Desenha retangulo semi-transparente de fundo."""
    bg = pygame.Surface(
        (layout.SPEED_INDICATOR_W, layout.SPEED_INDICATOR_H),
    )
    bg.set_alpha(_BG_ALPHA)
    bg.fill(colors.BG_PANEL)
    surface.blit(
        bg,
        (layout.SPEED_INDICATOR_X, layout.SPEED_INDICATOR_Y),
    )


def _draw_label(
    surface: pygame.Surface,
    speed: float,
    fonts: FontManager,
) -> None:
    """Desenha texto da velocidade centralizado no badge."""
    label = _speed_label(speed)
    color = _speed_color(speed)
    rendered = fonts.medium.render(label, True, color)
    cx = layout.SPEED_INDICATOR_X + layout.SPEED_INDICATOR_W // 2
    cy = layout.SPEED_INDICATOR_Y + layout.SPEED_INDICATOR_H // 2
    rect = rendered.get_rect(center=(cx, cy))
    surface.blit(rendered, rect)
