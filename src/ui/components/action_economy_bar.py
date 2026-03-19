"""Barra visual da action economy — mostra [A][B][R] com status."""

from __future__ import annotations

import pygame

from src.core.combat.action_economy import ActionEconomy, ActionType
from src.ui import colors, layout

_LABELS: tuple[tuple[ActionType, str], ...] = (
    (ActionType.ACTION, "A"),
    (ActionType.BONUS_ACTION, "B"),
    (ActionType.REACTION, "R"),
)


def draw_economy_bar(
    surface: pygame.Surface,
    economy: ActionEconomy,
    font: pygame.font.Font,
) -> None:
    """Renderiza indicadores [A][B][R] com cor verde/cinza."""
    x = layout.ECONOMY_BAR_X
    y = layout.ECONOMY_BAR_Y
    pos = (layout.ECONOMY_BAR_X, layout.ECONOMY_BAR_Y)
    for action_type, label in _LABELS:
        available = economy.is_available(action_type)
        _draw_slot(surface, label, available, pos, font)
        pos = (pos[0] + layout.ECONOMY_SLOT_WIDTH + layout.ECONOMY_SLOT_SPACING, pos[1])


def _draw_slot(
    surface: pygame.Surface,
    label: str,
    available: bool,
    pos: tuple[int, int],
    font: pygame.font.Font,
) -> None:
    slot_rect = pygame.Rect(
        pos[0], pos[1],
        layout.ECONOMY_SLOT_WIDTH, layout.ECONOMY_BAR_HEIGHT,
    )
    fill = colors.ECONOMY_AVAILABLE if available else colors.ECONOMY_USED
    pygame.draw.rect(surface, fill, slot_rect, border_radius=3)
    mark = "\u2713" if available else "\u2717"
    text = font.render(f"{label}{mark}", True, colors.TEXT_WHITE)
    text_x = pos[0] + (layout.ECONOMY_SLOT_WIDTH - text.get_width()) // 2
    text_y = pos[1] + (layout.ECONOMY_BAR_HEIGHT - text.get_height()) // 2
    surface.blit(text, (text_x, text_y))


def get_economy_labels() -> list[tuple[ActionType, str]]:
    """Retorna labels da economy bar para testes."""
    return list(_LABELS)
