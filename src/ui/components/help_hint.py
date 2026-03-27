"""HelpHint — indicador '[H] Help' sempre visivel no canto inferior direito."""

from __future__ import annotations

import pygame

from src.ui import layout
from src.ui.font_manager import FontManager

_HINT_COLOR = (140, 140, 160)
_MARGIN_RIGHT = 10
_MARGIN_BOTTOM = 8


def draw_help_hint(surface: pygame.Surface, fonts: FontManager) -> None:
    """Desenha '[H] Help' discreto no canto inferior direito."""
    text = fonts.small.render("[H] Help", True, _HINT_COLOR)
    x = layout.WINDOW_WIDTH - text.get_width() - _MARGIN_RIGHT
    y = layout.WINDOW_HEIGHT - text.get_height() - _MARGIN_BOTTOM
    surface.blit(text, (x, y))
