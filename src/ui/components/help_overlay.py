"""HelpOverlay — painel de keybindings centralizado na tela."""

from __future__ import annotations

import pygame

from src.ui import colors, layout
from src.ui.font_manager import FontManager

KEYBINDINGS: tuple[tuple[str, str], ...] = (
    ("[1-9]", "Select option"),
    ("[UP/DOWN]", "Navigate skills"),
    ("[ESC]", "Back / Pause menu"),
    ("[Backspace]", "Back"),
    ("[TAB]", "End turn"),
    ("[SPACE]", "End turn"),
    ("[C]", "Items (quick access)"),
    ("[S]", "Speed (1x/2x/3x)"),
    ("[H]", "Help"),
)

_PANEL_W = 400
_PANEL_H = 378
_PADDING_X = 24
_LINE_HEIGHT = 28
_KEY_COL_WIDTH = 130
_OVERLAY_ALPHA = 180


def draw_help_overlay(surface: pygame.Surface, fonts: FontManager) -> None:
    """Desenha overlay de help centralizado na tela."""
    _draw_backdrop(surface)
    panel_rect = _centered_panel_rect()
    _draw_panel_box(surface, panel_rect)
    _draw_title(surface, fonts, panel_rect)
    _draw_keybindings(surface, fonts, panel_rect)
    _draw_footer(surface, fonts, panel_rect)


def _draw_backdrop(surface: pygame.Surface) -> None:
    """Overlay escuro semi-transparente cobrindo a tela toda."""
    overlay = pygame.Surface(
        (layout.WINDOW_WIDTH, layout.WINDOW_HEIGHT), pygame.SRCALPHA,
    )
    overlay.fill((0, 0, 0, _OVERLAY_ALPHA))
    surface.blit(overlay, (0, 0))


def _centered_panel_rect() -> pygame.Rect:
    """Retorna Rect do painel centralizado."""
    px = (layout.WINDOW_WIDTH - _PANEL_W) // 2
    py = (layout.WINDOW_HEIGHT - _PANEL_H) // 2
    return pygame.Rect(px, py, _PANEL_W, _PANEL_H)


def _draw_panel_box(surface: pygame.Surface, rect: pygame.Rect) -> None:
    """Desenha caixa do painel com fundo e borda."""
    pygame.draw.rect(surface, colors.MENU_BG, rect, border_radius=8)
    pygame.draw.rect(surface, colors.MENU_BORDER, rect, 2, 8)


def _draw_title(
    surface: pygame.Surface, fonts: FontManager, rect: pygame.Rect,
) -> None:
    """Desenha titulo 'HELP' centralizado no topo do painel."""
    title = fonts.large.render("HELP", True, colors.TEXT_YELLOW)
    cx = rect.centerx - title.get_width() // 2
    cy = rect.y + 16
    surface.blit(title, (cx, cy))


def _draw_keybindings(
    surface: pygame.Surface, fonts: FontManager, rect: pygame.Rect,
) -> None:
    """Desenha linhas de keybinding: tecla em amarelo, desc em branco."""
    x = rect.x + _PADDING_X
    y = rect.y + 56
    for key_label, description in KEYBINDINGS:
        _draw_binding_line(surface, fonts.medium, key_label, description, x, y)
        y += _LINE_HEIGHT


def _draw_binding_line(
    surface: pygame.Surface, font: pygame.font.Font,
    key_label: str, description: str,
    x: int, y: int,
) -> None:
    """Desenha uma linha: tecla amarela + descricao branca."""
    key_text = font.render(key_label, True, colors.TEXT_YELLOW)
    surface.blit(key_text, (x, y))
    desc_text = font.render(description, True, colors.TEXT_WHITE)
    surface.blit(desc_text, (x + _KEY_COL_WIDTH, y))


def _draw_footer(
    surface: pygame.Surface, fonts: FontManager, rect: pygame.Rect,
) -> None:
    """Desenha instrucao de fechar na parte inferior do painel."""
    footer = fonts.small.render(
        "[ESC] or [H] to close", True, colors.TEXT_MUTED,
    )
    cx = rect.centerx - footer.get_width() // 2
    cy = rect.bottom - 30
    surface.blit(footer, (cx, cy))
