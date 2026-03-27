"""Mini-icones de status effects nos character cards."""

from __future__ import annotations

import pygame

from src.ui import colors

# Mapeamento: nome do efeito (lowercase) -> (simbolo, cor)
# Ailments usam class name (ex: "Poison"), buffs usam "X Up", debuffs "X Down"
_ICON_MAP: dict[str, tuple[str, tuple[int, int, int]]] = {
    # DoTs
    "poison": ("Ps", (120, 220, 50)),
    "virus": ("Vi", (160, 255, 50)),
    "bleed": ("Bl", (200, 40, 40)),
    "burn": ("Br", (255, 120, 30)),
    "scorch": ("Sc", (255, 80, 0)),
    # CCs
    "freeze": ("Fz", (130, 200, 255)),
    "paralysis": ("Pa", (255, 255, 100)),
    "confusion": ("Cf", (255, 150, 200)),
    # Debuffs
    "cold": ("Cd", (100, 160, 220)),
    "weakness": ("Wk", (200, 100, 100)),
    "injury": ("Ij", (220, 80, 80)),
    "sickness": ("Sk", (180, 140, 100)),
    # Resource locks
    "amnesia": ("Am", (180, 140, 255)),
    "curse": ("Cu", (100, 50, 150)),
}

_BUFF_COLOR = colors.EFFECT_BUFF
_DEBUFF_COLOR = colors.EFFECT_DEBUFF
_BUFF_SYMBOL = "+"
_DEBUFF_SYMBOL = "-"

_ICON_WIDTH = 22
_ICON_HEIGHT = 16
_ICON_SPACING = 3
_ICON_RADIUS = 3
_MAX_ICONS = 5


def draw_effect_icons(
    surface: pygame.Surface,
    effects: tuple[str, ...],
    x: int,
    y: int,
    font: pygame.font.Font,
) -> None:
    """Desenha mini-badges de efeitos ativos no card."""
    cx = x
    for name in effects[:_MAX_ICONS]:
        symbol, color = _resolve_icon(name)
        _draw_icon_badge(surface, cx, y, symbol, color, font)
        cx += _ICON_WIDTH + _ICON_SPACING
    overflow = len(effects) - _MAX_ICONS
    if overflow > 0:
        text = font.render(f"+{overflow}", True, colors.TEXT_MUTED)
        surface.blit(text, (cx + 2, y))


def _resolve_icon(name: str) -> tuple[str, tuple[int, int, int]]:
    """Resolve nome do efeito para simbolo e cor."""
    key = name.lower()
    if key in _ICON_MAP:
        return _ICON_MAP[key]
    if key.endswith(" up"):
        return _BUFF_SYMBOL, _BUFF_COLOR
    if key.endswith(" down"):
        return _DEBUFF_SYMBOL, _DEBUFF_COLOR
    return "\u25cf", colors.TEXT_EFFECT


def _draw_icon_badge(
    surface: pygame.Surface,
    x: int,
    y: int,
    symbol: str,
    color: tuple[int, int, int],
    font: pygame.font.Font,
) -> None:
    """Desenha badge colorido com simbolo."""
    bg = _dim_color(color, 0.3)
    rect = pygame.Rect(x, y, _ICON_WIDTH, _ICON_HEIGHT)
    pygame.draw.rect(surface, bg, rect, border_radius=_ICON_RADIUS)
    pygame.draw.rect(surface, color, rect, 1, border_radius=_ICON_RADIUS)
    rendered = font.render(symbol, True, color)
    text_rect = rendered.get_rect(center=rect.center)
    surface.blit(rendered, text_rect)


def _dim_color(
    color: tuple[int, int, int], factor: float,
) -> tuple[int, int, int]:
    """Escurece uma cor por um fator."""
    return (
        int(color[0] * factor),
        int(color[1] * factor),
        int(color[2] * factor),
    )
