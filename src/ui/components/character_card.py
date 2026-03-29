"""Componente visual de personagem: retangulo + nome + barras + efeitos."""

from __future__ import annotations

import pygame

from src.ui import colors, layout
from src.ui.components.class_icon import draw_class_icon
from src.ui.components.effect_icons import draw_effect_icons
from src.ui.components.health_bar import draw_hp_bar, draw_mana_bar
from src.ui.components.resource_display import draw_class_resource
from src.ui.font_manager import FontManager
from src.ui.replay.battle_snapshot import CharacterSnapshot

_NAME_OFFSET_Y = 4
_HP_OFFSET_Y = 30
_MANA_OFFSET_Y = 48
_RESOURCE_OFFSET_Y = 64
_RESOURCE_LINE_HEIGHT = 14
_EFFECTS_OFFSET_Y = 66
_BAR_OFFSET_X = 15
_EFFECT_SPACING = 12


def draw_character_card(
    surface: pygame.Surface,
    snap: CharacterSnapshot,
    x: int, y: int,
    fonts: FontManager,
) -> None:
    """Desenha card completo de um personagem."""
    card_color = _pick_card_color(snap)
    rect = pygame.Rect(x, y, layout.CARD_WIDTH, layout.CARD_HEIGHT)
    pygame.draw.rect(surface, card_color, rect, border_radius=6)
    pygame.draw.rect(surface, colors.BG_PANEL_BORDER, rect, 2, 6)
    if not snap.is_alive:
        _draw_dead_card(surface, snap.name, x, y, rect, fonts)
        return
    _draw_name(surface, snap.name, x, y, fonts.medium)
    if snap.class_id:
        draw_class_icon(
            surface, snap.class_id,
            x + layout.CARD_WIDTH - 24, y + 4,
        )
    bx = x + _BAR_OFFSET_X
    draw_hp_bar(surface, bx, y + _HP_OFFSET_Y, snap.current_hp, snap.max_hp, fonts.small)
    draw_mana_bar(surface, bx, y + _MANA_OFFSET_Y, snap.current_mana, snap.max_mana, fonts.small)
    res_y = _draw_resources(surface, snap, bx, y + _RESOURCE_OFFSET_Y, fonts.small)
    effects_y = max(res_y, y + _EFFECTS_OFFSET_Y)
    _draw_effects(surface, snap.active_effects, bx, effects_y, fonts.small)


_DEATH_X_COLOR = (120, 40, 40)
_DEATH_X_WIDTH = 3


def _draw_dead_card(
    surface: pygame.Surface,
    name: str,
    x: int, y: int,
    rect: pygame.Rect,
    fonts: FontManager,
) -> None:
    """Draws simplified dead card: name in muted + red X."""
    rendered = fonts.medium.render(name, True, colors.TEXT_MUTED)
    surface.blit(rendered, (x + _BAR_OFFSET_X, y + _NAME_OFFSET_Y))
    pygame.draw.line(
        surface, _DEATH_X_COLOR,
        (rect.left + 4, rect.top + 4),
        (rect.right - 4, rect.bottom - 4),
        _DEATH_X_WIDTH,
    )
    pygame.draw.line(
        surface, _DEATH_X_COLOR,
        (rect.right - 4, rect.top + 4),
        (rect.left + 4, rect.bottom - 4),
        _DEATH_X_WIDTH,
    )


def _pick_card_color(snap: CharacterSnapshot) -> tuple:
    if not snap.is_alive:
        return colors.DEAD_COLOR
    return colors.PARTY_COLOR if snap.is_party else colors.ENEMY_COLOR


def _draw_name(
    surface: pygame.Surface,
    name: str, x: int, y: int,
    font: pygame.font.Font,
) -> None:
    rendered = font.render(name, True, colors.TEXT_WHITE)
    surface.blit(rendered, (x + _BAR_OFFSET_X, y + _NAME_OFFSET_Y))


def _draw_resources(
    surface: pygame.Surface,
    snap: CharacterSnapshot,
    x: int, y: int,
    font: pygame.font.Font,
) -> int:
    """Desenha recursos de classe. Retorna y apos o ultimo recurso."""
    for i, res in enumerate(snap.class_resources[:2]):
        draw_class_resource(surface, x, y + i * _RESOURCE_LINE_HEIGHT, res, font)
    count = min(len(snap.class_resources), 2)
    return y + count * _RESOURCE_LINE_HEIGHT


def _draw_effects(
    surface: pygame.Surface,
    effects: tuple[str, ...],
    x: int, y: int,
    font: pygame.font.Font,
) -> None:
    if effects:
        draw_effect_icons(surface, effects, x, y, font)
