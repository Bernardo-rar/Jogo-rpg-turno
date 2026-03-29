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


_PANEL_BOTTOM = layout.WINDOW_HEIGHT - 10


def draw_action_panel(
    surface: pygame.Surface,
    options: list[MenuOption],
    level: MenuLevel,
    font: pygame.font.Font,
    combatant_name: str = "",
    breadcrumb: str = "",
    can_go_back: bool = False,
    highlight_index: int = -1,
    description: str = "",
) -> None:
    """Renderiza o painel de opcoes do menu de acao."""
    h = _compute_height(
        len(options), combatant_name, breadcrumb,
        can_go_back, description,
    )
    panel_y = _PANEL_BOTTOM - h
    _draw_panel_bg(surface, panel_y, h)
    x = layout.ACTION_PANEL_X + _PADDING_X
    y = panel_y + _PADDING_Y
    y = _draw_header(surface, font, x, y, combatant_name, breadcrumb)
    _draw_title(surface, level, x, y, font)
    y += layout.ACTION_LINE_HEIGHT + 4
    for i, opt in enumerate(options):
        if i == highlight_index:
            _draw_highlight_bar(surface, x, y)
        _draw_option(surface, opt, x, y, font)
        y += layout.ACTION_LINE_HEIGHT
    if description:
        _draw_description(surface, font, x, y + 4, description)
    if can_go_back:
        back_y = panel_y + h - layout.ACTION_LINE_HEIGHT - 4
        _draw_back_hint_at(surface, font, back_y)


def _compute_height(
    n_options: int,
    name: str,
    breadcrumb: str,
    has_back: bool,
    description: str,
) -> int:
    """Calcula altura do painel baseado no conteudo."""
    h = _PADDING_Y * 2
    if name:
        h += layout.ACTION_LINE_HEIGHT
    if breadcrumb:
        h += layout.ACTION_LINE_HEIGHT
    h += layout.ACTION_LINE_HEIGHT + 4  # title
    h += n_options * layout.ACTION_LINE_HEIGHT
    if description:
        h += layout.ACTION_LINE_HEIGHT + 4
    if has_back:
        h += layout.ACTION_LINE_HEIGHT + 4
    return h


def _draw_panel_bg(
    surface: pygame.Surface, panel_y: int, panel_h: int,
) -> None:
    """Desenha fundo e borda do painel com tamanho dinamico."""
    panel = pygame.Rect(
        layout.ACTION_PANEL_X, panel_y,
        layout.ACTION_PANEL_WIDTH, panel_h,
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
    """Legacy — nao mais usada."""
    pass


def _draw_back_hint_at(
    surface: pygame.Surface, font: pygame.font.Font, y: int,
) -> None:
    """Desenha indicador '[ESC] Back' na posicao Y dada."""
    hint = font.render(_BACK_HINT, True, colors.TEXT_MUTED)
    x = layout.ACTION_PANEL_X + _PADDING_X
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


_HIGHLIGHT_BG = (50, 50, 70)
_HIGHLIGHT_BAR_HEIGHT = 22


def _draw_highlight_bar(
    surface: pygame.Surface,
    x: int, y: int,
) -> None:
    """Desenha fundo sutil atras da opcao destacada."""
    bar_w = layout.ACTION_PANEL_WIDTH - _PADDING_X * 2
    bar = pygame.Rect(x - 4, y, bar_w, _HIGHLIGHT_BAR_HEIGHT)
    pygame.draw.rect(surface, _HIGHLIGHT_BG, bar, border_radius=3)


def _draw_description(
    surface: pygame.Surface,
    font: pygame.font.Font,
    x: int, y: int,
    description: str,
) -> None:
    """Desenha descricao da opcao destacada abaixo das opcoes."""
    text = font.render(description, True, colors.TEXT_MUTED)
    surface.blit(text, (x, y))


_CD_BAR_W = 30
_CD_BAR_H = 6
_CD_BAR_BG = (50, 50, 50)
_CD_BAR_FILL = colors.TEXT_MUTED


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
    if not opt.available and opt.reason.startswith("CD:"):
        bx = x + _KEY_WIDTH + label_text.get_width() + 6
        by = y + (label_text.get_height() - _CD_BAR_H) // 2
        _draw_cooldown_bar(surface, bx, by, opt.reason)


def _draw_cooldown_bar(
    surface: pygame.Surface,
    x: int, y: int,
    reason: str,
) -> None:
    """Draws a mini cooldown bar. Format: 'CD: N'."""
    try:
        remaining = int(reason.split(":")[1].strip())
    except (IndexError, ValueError):
        return
    max_cd = max(remaining, 5)
    fill_ratio = 1.0 - (remaining / max_cd)
    pygame.draw.rect(surface, _CD_BAR_BG, (x, y, _CD_BAR_W, _CD_BAR_H))
    fill_w = int(_CD_BAR_W * fill_ratio)
    if fill_w > 0:
        pygame.draw.rect(surface, _CD_BAR_FILL, (x, y, fill_w, _CD_BAR_H))


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
