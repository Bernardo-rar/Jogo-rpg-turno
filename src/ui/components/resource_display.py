"""Componentes de display para recursos de classe (BAR, COUNTER, TOGGLE)."""

from __future__ import annotations

import pygame

from src.core.characters.class_resource_snapshot import (
    ClassResourceSnapshot,
    ResourceDisplayType,
)
from src.ui import colors

_RES_BAR_WIDTH = 100
_RES_BAR_HEIGHT = 8
_PIP_SIZE = 8
_PIP_SPACING = 3
_MAX_PIPS = 10
_TEXT_PADDING_Y = -2


def draw_class_resource(
    surface: pygame.Surface,
    x: int, y: int,
    snap: ClassResourceSnapshot,
    font: pygame.font.Font,
) -> None:
    """Dispatch: desenha recurso baseado no display_type."""
    dispatch = _DRAW_DISPATCH.get(snap.display_type)
    if dispatch is not None:
        dispatch(surface, x, y, snap, font)


def _draw_resource_bar(
    surface: pygame.Surface,
    x: int, y: int,
    snap: ClassResourceSnapshot,
    font: pygame.font.Font,
) -> None:
    """Mini barra horizontal para recursos BAR (Fury, Insanity, etc)."""
    bg = pygame.Rect(x, y, _RES_BAR_WIDTH, _RES_BAR_HEIGHT)
    pygame.draw.rect(surface, colors.HP_BG, bg)
    if snap.maximum > 0:
        fill_w = int(_RES_BAR_WIDTH * snap.current / snap.maximum)
        fill = pygame.Rect(x, y, fill_w, _RES_BAR_HEIGHT)
        pygame.draw.rect(surface, snap.color, fill)
    label = f"{snap.name} {snap.current}"
    rendered = font.render(label, True, colors.TEXT_WHITE)
    surface.blit(rendered, (x + _RES_BAR_WIDTH + 4, y + _TEXT_PADDING_Y))


def _draw_resource_pips(
    surface: pygame.Surface,
    x: int, y: int,
    snap: ClassResourceSnapshot,
    font: pygame.font.Font,
) -> None:
    """Bolinhas para recursos COUNTER (AP, Holy Power, etc)."""
    max_display = min(snap.maximum, _MAX_PIPS)
    for i in range(max_display):
        px = x + i * (_PIP_SIZE + _PIP_SPACING)
        rect = pygame.Rect(px, y, _PIP_SIZE, _PIP_SIZE)
        pip_color = snap.color if i < snap.current else colors.HP_BG
        pygame.draw.rect(surface, pip_color, rect)
    label = f"{snap.name}"
    lx = x + max_display * (_PIP_SIZE + _PIP_SPACING) + 4
    rendered = font.render(label, True, colors.TEXT_WHITE)
    surface.blit(rendered, (lx, y + _TEXT_PADDING_Y))


def _draw_resource_toggle(
    surface: pygame.Surface,
    x: int, y: int,
    snap: ClassResourceSnapshot,
    font: pygame.font.Font,
) -> None:
    """Texto colorido para recursos TOGGLE (Stealth, Stance, etc)."""
    is_active = snap.current > 0
    text_color = snap.color if is_active else colors.TEXT_MUTED
    label = snap.label if snap.label else snap.name
    prefix = snap.name + ": " if snap.label else ""
    rendered = font.render(f"{prefix}{label}", True, text_color)
    surface.blit(rendered, (x, y + _TEXT_PADDING_Y))


_DRAW_DISPATCH = {
    ResourceDisplayType.BAR: _draw_resource_bar,
    ResourceDisplayType.COUNTER: _draw_resource_pips,
    ResourceDisplayType.TOGGLE: _draw_resource_toggle,
}
