"""TurnTimeline — barra horizontal no topo mostrando ordem de turnos."""

from __future__ import annotations

import pygame

from src.ui import colors, layout
from src.ui.font_manager import FontManager


class TurnTimeline:
    """Barra de ordem de turnos estilo Octopath Traveler / FFX."""

    def __init__(
        self,
        turn_order: list[str],
        party_names: frozenset[str],
    ) -> None:
        self._order = turn_order
        self._party_names = party_names
        self._active: str | None = None
        self._dead: set[str] = set()

    def update(
        self,
        turn_order: list[str],
        active: str | None,
        dead: set[str],
    ) -> None:
        """Atualiza estado da timeline a cada frame."""
        self._order = turn_order
        self._active = active
        self._dead = dead

    def draw(
        self,
        surface: pygame.Surface,
        fonts: FontManager,
        round_number: int,
    ) -> None:
        """Desenha a timeline completa no topo da tela."""
        self._draw_round_label(surface, fonts, round_number)
        self._draw_slots(surface, fonts)

    def _draw_round_label(
        self,
        surface: pygame.Surface,
        fonts: FontManager,
        round_number: int,
    ) -> None:
        text = f"R{round_number}"
        rendered = fonts.medium.render(text, True, colors.TEXT_YELLOW)
        surface.blit(rendered, (layout.TIMELINE_ROUND_X, layout.TIMELINE_Y + 5))

    def _draw_slots(
        self,
        surface: pygame.Surface,
        fonts: FontManager,
    ) -> None:
        total_width = _calculate_total_width(len(self._order))
        start_x = (layout.WINDOW_WIDTH - total_width) // 2
        y = layout.TIMELINE_Y + (layout.TIMELINE_HEIGHT - layout.TIMELINE_SLOT_HEIGHT) // 2

        for i, name in enumerate(self._order):
            x = start_x + i * (layout.TIMELINE_SLOT_WIDTH + layout.TIMELINE_SLOT_SPACING)
            is_active = name == self._active
            is_dead = name in self._dead
            is_party = name in self._party_names
            _draw_slot(surface, fonts, x, y, name, is_active, is_dead, is_party)


def _calculate_total_width(count: int) -> int:
    """Largura total dos slots + espaçamento."""
    if count == 0:
        return 0
    return count * layout.TIMELINE_SLOT_WIDTH + (count - 1) * layout.TIMELINE_SLOT_SPACING


def _draw_slot(
    surface: pygame.Surface,
    fonts: FontManager,
    x: int,
    y: int,
    name: str,
    is_active: bool,
    is_dead: bool,
    is_party: bool,
) -> None:
    """Desenha um slot individual na timeline."""
    w = layout.TIMELINE_SLOT_WIDTH
    h = layout.TIMELINE_SLOT_HEIGHT
    radius = layout.TIMELINE_SLOT_RADIUS

    bg_color = _pick_bg_color(is_dead, is_party)
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(surface, bg_color, rect, border_radius=radius)

    if is_active:
        border_rect = rect.inflate(4, 4)
        pygame.draw.rect(
            surface, colors.TIMELINE_ACTIVE_BORDER,
            border_rect, width=2, border_radius=radius + 2,
        )

    text_color = colors.TEXT_MUTED if is_dead else colors.TEXT_WHITE
    label = _abbreviate_name(name)
    rendered = fonts.small.render(label, True, text_color)
    text_rect = rendered.get_rect(center=rect.center)
    surface.blit(rendered, text_rect)

    if is_dead:
        _draw_strikethrough(surface, rect)


def _pick_bg_color(
    is_dead: bool, is_party: bool,
) -> tuple[int, int, int]:
    if is_dead:
        return colors.TIMELINE_DEAD
    return colors.TIMELINE_PARTY if is_party else colors.TIMELINE_ENEMY


def _abbreviate_name(name: str) -> str:
    """Abrevia nomes longos para caber no slot."""
    max_chars = 10
    if len(name) <= max_chars:
        return name
    return name[:max_chars - 1] + "."


def _draw_strikethrough(
    surface: pygame.Surface,
    rect: pygame.Rect,
) -> None:
    """Risca o slot de personagens mortos."""
    y_mid = rect.centery
    pygame.draw.line(
        surface, colors.TEXT_MUTED,
        (rect.left + 4, y_mid), (rect.right - 4, y_mid), 1,
    )
