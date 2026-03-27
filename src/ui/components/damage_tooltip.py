"""Tooltip flutuante de preview de dano/cura ao lado do card alvo."""

from __future__ import annotations

import pygame

from src.core.combat.damage import DamageType
from src.core.combat.player_action import PlayerActionType
from src.core.combat.damage_preview import (
    AttackPreview,
    HealPreview,
    SkillDamagePreview,
)
from src.ui import colors, layout

_TOOLTIP_WIDTH = 220
_TOOLTIP_PADDING = 8
_LINE_HEIGHT = 18
_BORDER_RADIUS = 6
_BG_COLOR = (20, 20, 35, 230)
_BORDER_COLOR = (80, 80, 120)
_MARGIN_FROM_CARD = 8


def draw_attack_preview(
    surface: pygame.Surface,
    preview: AttackPreview,
    card_rect: tuple[int, int, int, int],
    font: pygame.font.Font,
) -> None:
    """Desenha tooltip de ataque basico ao lado do card."""
    lines = [
        (PlayerActionType.BASIC_ATTACK.label, colors.TEXT_WHITE),
        (f"Damage: {preview.min_damage} ~ {preview.max_damage}", colors.TEXT_DAMAGE),
        (f"Crit: {preview.crit_chance_pct}%", colors.TEXT_YELLOW),
        (f"Type: {preview.damage_type.name.title()}", colors.TEXT_MUTED),
    ]
    _draw_tooltip(surface, lines, card_rect, font)


def draw_skill_damage_preview(
    surface: pygame.Surface,
    preview: SkillDamagePreview,
    card_rect: tuple[int, int, int, int],
    font: pygame.font.Font,
) -> None:
    """Desenha tooltip de skill de dano ao lado do card."""
    element_str = preview.element.name.title() if preview.element else ""
    type_label = f"{preview.damage_type.name.title()}"
    if element_str:
        type_label += f" ({element_str})"
    lines = [
        (preview.skill_name, colors.TEXT_WHITE),
        (f"Cost: {preview.mana_cost} MP", colors.MANA_BLUE),
        (f"Damage: {preview.min_damage} ~ {preview.max_damage}", colors.TEXT_DAMAGE),
        (f"Crit: {preview.crit_chance_pct}%", colors.TEXT_YELLOW),
        (f"Type: {type_label}", colors.TEXT_MUTED),
    ]
    _draw_tooltip(surface, lines, card_rect, font)


def draw_heal_preview(
    surface: pygame.Surface,
    preview: HealPreview,
    card_rect: tuple[int, int, int, int],
    font: pygame.font.Font,
) -> None:
    """Desenha tooltip de skill de cura ao lado do card."""
    hp_pct = int(preview.target_hp_current / preview.target_hp_max * 100)
    lines = [
        (preview.skill_name, colors.TEXT_WHITE),
        (f"Cost: {preview.mana_cost} MP", colors.MANA_BLUE),
        (f"Heal: ~{preview.estimated_heal}", colors.TEXT_HEAL),
        (f"Target HP: {preview.target_hp_current}/{preview.target_hp_max} ({hp_pct}%)", colors.TEXT_MUTED),
    ]
    _draw_tooltip(surface, lines, card_rect, font)


def _draw_tooltip(
    surface: pygame.Surface,
    lines: list[tuple[str, tuple[int, int, int]]],
    card_rect: tuple[int, int, int, int],
    font: pygame.font.Font,
) -> None:
    """Renderiza tooltip generico ao lado do card."""
    cx, cy, cw, ch = card_rect
    height = _TOOLTIP_PADDING * 2 + len(lines) * _LINE_HEIGHT
    x, y = _pick_position(cx, cy, cw, ch, height)

    bg_rect = pygame.Rect(x, y, _TOOLTIP_WIDTH, height)
    bg_surface = pygame.Surface(
        (_TOOLTIP_WIDTH, height), pygame.SRCALPHA,
    )
    bg_surface.fill(_BG_COLOR)
    surface.blit(bg_surface, (x, y))
    pygame.draw.rect(surface, _BORDER_COLOR, bg_rect, 1, _BORDER_RADIUS)

    text_x = x + _TOOLTIP_PADDING
    text_y = y + _TOOLTIP_PADDING
    for text, color in lines:
        rendered = font.render(text, True, color)
        surface.blit(rendered, (text_x, text_y))
        text_y += _LINE_HEIGHT


def _pick_position(
    cx: int, cy: int, cw: int, ch: int, tooltip_height: int,
) -> tuple[int, int]:
    """Posiciona o tooltip: preferencialmente a esquerda do card."""
    x = cx - _TOOLTIP_WIDTH - _MARGIN_FROM_CARD
    if x < 0:
        x = cx + cw + _MARGIN_FROM_CARD
    y = cy
    if y + tooltip_height > layout.WINDOW_HEIGHT:
        y = layout.WINDOW_HEIGHT - tooltip_height - 4
    return x, y
