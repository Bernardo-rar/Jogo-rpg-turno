"""Painel visual do menu de acoes — renderiza lista de MenuOption."""

from __future__ import annotations

import pygame

from src.ui import colors, layout
from src.ui.input.menu_state import MenuLevel, MenuOption

_PADDING_X = 12
_PADDING_Y = 8
_KEY_WIDTH = 28
_BACK_HINT = "[ESC] Back"

_LEVEL_TITLES: dict[MenuLevel, str] = {
    MenuLevel.ACTION_TYPE: "Choose Action Type",
    MenuLevel.SPECIFIC_ACTION: "Choose Action",
    MenuLevel.TARGET_SELECT: "Choose Target",
}


def draw_action_panel(
    surface: pygame.Surface,
    options: list[MenuOption],
    level: MenuLevel,
    font: pygame.font.Font,
    combatant_name: str = "",
    breadcrumb: str = "",
    can_go_back: bool = False,
) -> None:
    """Renderiza o painel de opcoes do menu de acao."""
    _draw_panel_bg(surface)
    x = layout.ACTION_PANEL_X + _PADDING_X
    y = layout.ACTION_PANEL_Y + _PADDING_Y
    y = _draw_header(surface, font, x, y, combatant_name, breadcrumb)
    _draw_title(surface, level, x, y, font)
    y += layout.ACTION_LINE_HEIGHT + 4
    for opt in options:
        _draw_option(surface, opt, x, y, font)
        y += layout.ACTION_LINE_HEIGHT
    if can_go_back:
        _draw_back_hint(surface, font)


def _draw_panel_bg(surface: pygame.Surface) -> None:
    """Desenha fundo e borda do painel."""
    panel = pygame.Rect(
        layout.ACTION_PANEL_X, layout.ACTION_PANEL_Y,
        layout.ACTION_PANEL_WIDTH, layout.ACTION_PANEL_HEIGHT,
    )
    pygame.draw.rect(surface, colors.MENU_BG, panel, border_radius=4)
    pygame.draw.rect(surface, colors.MENU_BORDER, panel, 1, 4)


def _draw_header(
    surface: pygame.Surface,
    font: pygame.font.Font,
    x: int, y: int,
    combatant_name: str,
    breadcrumb: str,
) -> int:
    """Desenha nome do combatente e breadcrumb. Retorna y atualizado."""
    if combatant_name:
        name_text = font.render(combatant_name, True, colors.PARTY_COLOR)
        surface.blit(name_text, (x, y))
        y += layout.ACTION_LINE_HEIGHT
    if breadcrumb:
        crumb = font.render(breadcrumb, True, colors.TEXT_MUTED)
        surface.blit(crumb, (x, y))
        y += layout.ACTION_LINE_HEIGHT
    return y


def _draw_back_hint(surface: pygame.Surface, font: pygame.font.Font) -> None:
    """Desenha indicador '[ESC] Back' no canto inferior do painel."""
    hint = font.render(_BACK_HINT, True, colors.TEXT_MUTED)
    x = layout.ACTION_PANEL_X + _PADDING_X
    y = (layout.ACTION_PANEL_Y + layout.ACTION_PANEL_HEIGHT
         - _PADDING_Y - hint.get_height())
    surface.blit(hint, (x, y))


def _draw_title(
    surface: pygame.Surface,
    level: MenuLevel,
    x: int, y: int,
    font: pygame.font.Font,
) -> None:
    title = _LEVEL_TITLES.get(level, "")
    rendered = font.render(title, True, colors.TEXT_YELLOW)
    surface.blit(rendered, (x, y))


def _draw_option(
    surface: pygame.Surface,
    opt: MenuOption,
    x: int, y: int,
    font: pygame.font.Font,
) -> None:
    key_color, label_color = _option_colors(opt.available)
    key_text = font.render(f"[{opt.key}]", True, key_color)
    surface.blit(key_text, (x, y))
    label = _option_label(opt)
    label_text = font.render(label, True, label_color)
    surface.blit(label_text, (x + _KEY_WIDTH, y))


def _option_colors(available: bool) -> tuple[tuple, tuple]:
    if available:
        return colors.MENU_KEY_COLOR, colors.TEXT_WHITE
    return colors.MENU_UNAVAILABLE, colors.MENU_UNAVAILABLE


def _option_label(opt: MenuOption) -> str:
    if not opt.available and opt.reason:
        return f"{opt.label} ({opt.reason})"
    return opt.label


def get_level_title(level: MenuLevel) -> str:
    """Retorna o titulo do nivel atual do menu."""
    return _LEVEL_TITLES.get(level, "")
