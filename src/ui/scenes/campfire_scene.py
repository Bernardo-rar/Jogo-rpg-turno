"""CampfireScene — tela de fogueira com escolha de buff."""

from __future__ import annotations

from typing import Callable

import pygame

from src.dungeon.run.campfire_actions import CampfireBuff
from src.ui import colors, layout
from src.ui.font_manager import FontManager

_CAMPFIRE_COLOR = (220, 140, 40)
_OPTION_SPACING = 60


class CampfireScene:
    """Tela de fogueira: escolha 1 buff de 3 opcoes."""

    def __init__(
        self,
        fonts: FontManager,
        buffs: list[CampfireBuff],
        on_select: Callable[[int], dict[str, object]],
        on_complete: Callable[[dict], None],
    ) -> None:
        self._fonts = fonts
        self._buffs = buffs
        self._on_select = on_select
        self._on_complete = on_complete
        self._result: dict[str, object] | None = None

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if self._result is not None:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._on_complete({})
            return
        idx = _key_to_index(event.key)
        if idx is not None and idx < len(self._buffs):
            self._result = self._on_select(idx)

    def update(self, dt_ms: int) -> bool:
        return True

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(colors.BG_DARK)
        cx = layout.WINDOW_WIDTH // 2
        _centered(surface, self._fonts.large, "Fogueira", cx, 120, _CAMPFIRE_COLOR)
        _centered(
            surface, self._fonts.small,
            "Escolha um beneficio para sua party:",
            cx, 170, colors.TEXT_MUTED,
        )
        if self._result is None:
            _draw_options(surface, self._fonts, cx, self._buffs)
        else:
            _draw_result(surface, self._fonts, cx, self._result)


def _draw_options(
    surface: pygame.Surface,
    fonts: FontManager,
    cx: int,
    buffs: list[CampfireBuff],
) -> None:
    """Desenha opcoes de buff."""
    y = 250
    for i, buff in enumerate(buffs):
        label = f"[{i + 1}] {buff.name}"
        _centered(surface, fonts.medium, label, cx, y, colors.TEXT_YELLOW)
        _centered(surface, fonts.small, buff.description, cx, y + 28, colors.TEXT_WHITE)
        y += _OPTION_SPACING


def _draw_result(
    surface: pygame.Surface,
    fonts: FontManager,
    cx: int,
    result: dict[str, object],
) -> None:
    """Desenha resultado da escolha."""
    buff_name = result.get("buff_name", "")
    _centered(surface, fonts.medium, f"{buff_name} ativado!", cx, 300, colors.TEXT_HEAL)
    _centered(surface, fonts.small, "[ENTER] Continuar", cx, 450, colors.TEXT_MUTED)


def _key_to_index(key: int) -> int | None:
    mapping = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2}
    return mapping.get(key)


def _centered(surface, font, text, x, y, color):
    rendered = font.render(text, True, color)
    rect = rendered.get_rect(center=(x, y))
    surface.blit(rendered, rect)
