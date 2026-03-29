"""TalentChoiceScene — tela de escolha de talento (pick 1 of 3)."""

from __future__ import annotations

from typing import Callable, TYPE_CHECKING

import pygame

from src.core.progression.talent_config import Talent
from src.ui import colors, layout
from src.ui.font_manager import FontManager

if TYPE_CHECKING:
    from src.core.characters.character import Character

_CARD_W = 350
_CARD_H = 200
_CARD_GAP = 30
_CARD_Y = 180
_LINE_H = 22


class TalentChoiceScene:
    """Tela de escolha de talento para um personagem."""

    def __init__(
        self,
        fonts: FontManager,
        char: Character,
        options: list[Talent],
        on_complete: Callable[[dict], None],
    ) -> None:
        self._fonts = fonts
        self._char = char
        self._options = options
        self._on_complete = on_complete
        self._selected = 0

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_LEFT, pygame.K_a):
            self._selected = max(0, self._selected - 1)
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            self._selected = min(len(self._options) - 1, self._selected + 1)
        elif event.key == pygame.K_1 and len(self._options) >= 1:
            self._selected = 0
        elif event.key == pygame.K_2 and len(self._options) >= 2:
            self._selected = 1
        elif event.key == pygame.K_3 and len(self._options) >= 3:
            self._selected = 2
        elif event.key == pygame.K_RETURN:
            self._confirm()

    def _confirm(self) -> None:
        if not self._options:
            self._on_complete({})
            return
        chosen = self._options[self._selected]
        self._on_complete({"talent": chosen})

    def update(self, dt_ms: int) -> bool:
        return True

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(colors.BG_DARK)
        _draw_title(surface, self._fonts, self._char.name)
        for i, talent in enumerate(self._options):
            selected = i == self._selected
            _draw_talent_card(surface, self._fonts, talent, i, selected)
        _draw_controls(surface, self._fonts)


def _draw_title(
    surface: pygame.Surface, fonts: FontManager, name: str,
) -> None:
    title = fonts.large.render(
        f"Choose Talent: {name}", True, colors.TEXT_YELLOW,
    )
    cx = layout.WINDOW_WIDTH // 2
    surface.blit(title, (cx - title.get_width() // 2, 30))
    sub = fonts.small.render(
        "Pick 1 of 3 talents", True, colors.TEXT_MUTED,
    )
    surface.blit(sub, (cx - sub.get_width() // 2, 70))


_CAT_COLORS: dict[str, tuple[int, int, int]] = {
    "OFFENSIVE": colors.TEXT_DAMAGE,
    "DEFENSIVE": (80, 200, 255),
    "UTILITY": colors.TEXT_YELLOW,
}


def _draw_talent_card(
    surface: pygame.Surface, fonts: FontManager,
    talent: Talent, index: int, selected: bool,
) -> None:
    cx = layout.WINDOW_WIDTH // 2
    total_w = _CARD_W * 3 + _CARD_GAP * 2
    start_x = cx - total_w // 2
    x = start_x + index * (_CARD_W + _CARD_GAP)
    rect = pygame.Rect(x, _CARD_Y, _CARD_W, _CARD_H)
    border_color = colors.TEXT_YELLOW if selected else colors.MENU_BORDER
    pygame.draw.rect(surface, colors.MENU_BG, rect, border_radius=8)
    pygame.draw.rect(surface, border_color, rect, 3, 8)
    _draw_card_content(surface, fonts, talent, x, index, selected)


def _draw_card_content(
    surface: pygame.Surface, fonts: FontManager,
    talent: Talent, x: int, index: int, selected: bool,
) -> None:
    pad = 14
    y = _CARD_Y + pad
    key_color = colors.TEXT_YELLOW if selected else colors.TEXT_WHITE
    header = fonts.medium.render(
        f"[{index + 1}] {talent.name}", True, key_color,
    )
    surface.blit(header, (x + pad, y))
    y += 28
    cat_color = _CAT_COLORS.get(talent.category, colors.TEXT_MUTED)
    cat = fonts.small.render(talent.category, True, cat_color)
    surface.blit(cat, (x + pad, y))
    y += 24
    desc = fonts.small.render(talent.description, True, colors.TEXT_MUTED)
    surface.blit(desc, (x + pad, y))
    y += 30
    for effect in talent.effects:
        sign = "+" if effect.percent > 0 else ""
        label = f"  {sign}{effect.percent:.0f}% {effect.stat}"
        text = fonts.small.render(label, True, colors.TEXT_HEAL)
        surface.blit(text, (x + pad, y))
        y += _LINE_H


def _draw_controls(
    surface: pygame.Surface, fonts: FontManager,
) -> None:
    y = layout.WINDOW_HEIGHT - 30
    cx = layout.WINDOW_WIDTH // 2
    hint = "[1/2/3] Select  [A/D] Navigate  [ENTER] Confirm"
    text = fonts.small.render(hint, True, colors.TEXT_MUTED)
    surface.blit(text, (cx - text.get_width() // 2, y))
