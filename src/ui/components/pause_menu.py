"""PauseMenu — menu de pausa com Resume, Help e Forfeit."""

from __future__ import annotations

from enum import Enum, auto

import pygame

from src.ui import colors, layout
from src.ui.font_manager import FontManager

_PAUSE_OPTIONS: tuple[tuple[str, str], ...] = (
    ("[1]", "Resume"),
    ("[2]", "Help"),
    ("[3]", "Forfeit (Lose Run)"),
)

_PANEL_W = 320
_PANEL_H = 220
_PADDING_X = 24
_LINE_HEIGHT = 32
_KEY_COL_WIDTH = 50
_OVERLAY_ALPHA = 180


class PauseMenuResult(Enum):
    """Resultado de input no menu de pausa."""

    RESUME = auto()
    HELP = auto()
    FORFEIT = auto()


_INPUT_MAP: dict[int, PauseMenuResult] = {
    pygame.K_1: PauseMenuResult.RESUME,
    pygame.K_ESCAPE: PauseMenuResult.RESUME,
    pygame.K_2: PauseMenuResult.HELP,
    pygame.K_3: PauseMenuResult.FORFEIT,
}


def handle_pause_input(key: int) -> PauseMenuResult | None:
    """Retorna resultado para teclas 1/2/3/ESC, None caso contrario."""
    return _INPUT_MAP.get(key)


def draw_pause_menu(surface: pygame.Surface, fonts: FontManager) -> None:
    """Desenha overlay do menu de pausa centralizado."""
    _draw_backdrop(surface)
    panel_rect = _centered_panel_rect()
    _draw_panel_box(surface, panel_rect)
    _draw_title(surface, fonts, panel_rect)
    _draw_options(surface, fonts, panel_rect)


def _draw_backdrop(surface: pygame.Surface) -> None:
    """Overlay escuro semi-transparente."""
    overlay = pygame.Surface(
        (layout.WINDOW_WIDTH, layout.WINDOW_HEIGHT), pygame.SRCALPHA,
    )
    overlay.fill((0, 0, 0, _OVERLAY_ALPHA))
    surface.blit(overlay, (0, 0))


def _centered_panel_rect() -> pygame.Rect:
    """Rect centralizado para o painel de pausa."""
    px = (layout.WINDOW_WIDTH - _PANEL_W) // 2
    py = (layout.WINDOW_HEIGHT - _PANEL_H) // 2
    return pygame.Rect(px, py, _PANEL_W, _PANEL_H)


def _draw_panel_box(surface: pygame.Surface, rect: pygame.Rect) -> None:
    """Caixa do painel com fundo e borda."""
    pygame.draw.rect(surface, colors.MENU_BG, rect, border_radius=8)
    pygame.draw.rect(surface, colors.MENU_BORDER, rect, 2, 8)


def _draw_title(
    surface: pygame.Surface, fonts: FontManager, rect: pygame.Rect,
) -> None:
    """Titulo 'PAUSED' centralizado no topo."""
    title = fonts.large.render("PAUSED", True, colors.TEXT_YELLOW)
    cx = rect.centerx - title.get_width() // 2
    cy = rect.y + 16
    surface.blit(title, (cx, cy))


def _draw_options(
    surface: pygame.Surface, fonts: FontManager, rect: pygame.Rect,
) -> None:
    """Desenha opcoes do menu de pausa."""
    x = rect.x + _PADDING_X
    y = rect.y + 64
    for key_label, description in _PAUSE_OPTIONS:
        _draw_option_line(surface, fonts.medium, key_label, description, x, y)
        y += _LINE_HEIGHT


def _draw_option_line(
    surface: pygame.Surface, font: pygame.font.Font,
    key_label: str, description: str,
    x: int, y: int,
) -> None:
    """Uma linha de opcao: tecla amarela + descricao branca."""
    key_text = font.render(key_label, True, colors.TEXT_YELLOW)
    surface.blit(key_text, (x, y))
    desc_text = font.render(description, True, colors.TEXT_WHITE)
    surface.blit(desc_text, (x + _KEY_COL_WIDTH, y))
