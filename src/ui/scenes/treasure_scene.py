"""TreasureScene — tela de bau de tesouro."""

from __future__ import annotations

from typing import Callable

import pygame

from src.dungeon.loot.drop_table import LootDrop
from src.dungeon.run.treasure_actions import TreasureResult
from src.ui import colors, layout
from src.ui.font_manager import FontManager

_GOLD_COLOR = (200, 180, 50)
_DROP_LINE_HEIGHT = 28
_MAX_VISIBLE_DROPS = 6


class TreasureScene:
    """Tela de recompensa de bau de tesouro."""

    def __init__(
        self,
        fonts: FontManager,
        result: TreasureResult,
        on_complete: Callable[[dict], None],
    ) -> None:
        self._fonts = fonts
        self._result = result
        self._on_complete = on_complete

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self._on_complete({})

    def update(self, dt_ms: int) -> bool:
        return True

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(colors.BG_DARK)
        cx = layout.WINDOW_WIDTH // 2
        _centered(surface, self._fonts.large, "Bau do Tesouro!", cx, 180, _GOLD_COLOR)
        _draw_gold(surface, self._fonts, cx, self._result.gold_earned)
        _draw_drops(surface, self._fonts, cx, self._result.drops)
        _centered(
            surface, self._fonts.small,
            "[ENTER] Continuar", cx, 550, colors.TEXT_MUTED,
        )


def _draw_gold(
    surface: pygame.Surface,
    fonts: FontManager,
    cx: int,
    gold: int,
) -> None:
    """Desenha gold encontrado."""
    text = f"+{gold} Gold"
    _centered(surface, fonts.medium, text, cx, 260, colors.TEXT_YELLOW)


def _draw_drops(
    surface: pygame.Surface,
    fonts: FontManager,
    cx: int,
    drops: tuple[LootDrop, ...],
) -> None:
    """Desenha itens encontrados."""
    if not drops:
        return
    y = 320
    _centered(surface, fonts.medium, "Itens encontrados:", cx, y, colors.TEXT_WHITE)
    visible = drops[:_MAX_VISIBLE_DROPS]
    for i, drop in enumerate(visible):
        name = drop.item_id.replace("_", " ").title()
        qty = f" x{drop.quantity}" if drop.quantity > 1 else ""
        _centered(
            surface, fonts.small,
            f"{name}{qty}", cx,
            y + 35 + i * _DROP_LINE_HEIGHT,
            colors.TEXT_WHITE,
        )


def _centered(surface, font, text, x, y, color):
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=(x, y))
    surface.blit(rendered, rect)
