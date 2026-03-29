"""SubclassChoiceScene — tela de escolha de subclass no level 3."""

from __future__ import annotations

from typing import Callable, TYPE_CHECKING

import pygame

from src.core.progression.subclass_config import ClassSubclasses, SubclassOption
from src.ui import colors, layout
from src.ui.font_manager import FontManager

if TYPE_CHECKING:
    from src.core.characters.character import Character

_CARD_W = 480
_CARD_H = 350
_CARD_GAP = 40
_CARD_Y = 150
_LINE_H = 24


class SubclassChoiceScene:
    """Tela de escolha de subclass para um personagem."""

    def __init__(
        self,
        fonts: FontManager,
        char: Character,
        subclasses: ClassSubclasses,
        on_complete: Callable[[dict], None],
    ) -> None:
        self._fonts = fonts
        self._char = char
        self._options = (subclasses.option_a, subclasses.option_b)
        self._on_complete = on_complete
        self._selected = 0

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_LEFT, pygame.K_a, pygame.K_1):
            self._selected = 0
        elif event.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_2):
            self._selected = 1
        elif event.key == pygame.K_RETURN:
            self._confirm()

    def _confirm(self) -> None:
        chosen = self._options[self._selected]
        self._on_complete({"subclass": chosen})

    def update(self, dt_ms: int) -> bool:
        return True

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(colors.BG_DARK)
        _draw_title(surface, self._fonts, self._char.name)
        for i, option in enumerate(self._options):
            selected = i == self._selected
            _draw_option_card(surface, self._fonts, option, i, selected)
        _draw_controls(surface, self._fonts)


def _draw_title(
    surface: pygame.Surface, fonts: FontManager, name: str,
) -> None:
    title = fonts.large.render(
        f"Choose Subclass: {name}", True, colors.TEXT_YELLOW,
    )
    cx = layout.WINDOW_WIDTH // 2
    surface.blit(title, (cx - title.get_width() // 2, 30))
    sub = fonts.small.render(
        "This choice is permanent for this run",
        True, colors.TEXT_MUTED,
    )
    surface.blit(sub, (cx - sub.get_width() // 2, 70))


def _draw_option_card(
    surface: pygame.Surface, fonts: FontManager,
    option: SubclassOption, index: int, selected: bool,
) -> None:
    cx = layout.WINDOW_WIDTH // 2
    total_w = _CARD_W * 2 + _CARD_GAP
    start_x = cx - total_w // 2
    x = start_x + index * (_CARD_W + _CARD_GAP)
    rect = pygame.Rect(x, _CARD_Y, _CARD_W, _CARD_H)
    border_color = colors.TEXT_YELLOW if selected else colors.MENU_BORDER
    pygame.draw.rect(surface, colors.MENU_BG, rect, border_radius=8)
    pygame.draw.rect(surface, border_color, rect, 3, 8)
    _draw_card_content(surface, fonts, option, x, index, selected)


def _draw_card_content(
    surface: pygame.Surface, fonts: FontManager,
    option: SubclassOption, x: int,
    index: int, selected: bool,
) -> None:
    pad = 16
    y = _CARD_Y + pad
    key_color = colors.TEXT_YELLOW if selected else colors.TEXT_WHITE
    header = fonts.medium.render(
        f"[{index + 1}] {option.name}", True, key_color,
    )
    surface.blit(header, (x + pad, y))
    y += 30
    desc = fonts.small.render(option.description, True, colors.TEXT_MUTED)
    surface.blit(desc, (x + pad, y))
    y += 35
    _draw_skills_section(surface, fonts, option, x + pad, y)
    y += len(option.skill_ids) * _LINE_H + 20
    _draw_bonuses_section(surface, fonts, option, x + pad, y)


def _draw_skills_section(
    surface: pygame.Surface, fonts: FontManager,
    option: SubclassOption, x: int, y: int,
) -> None:
    header = fonts.small.render("Skills:", True, colors.PARTY_COLOR)
    surface.blit(header, (x, y))
    y += _LINE_H
    for skill_id in option.skill_ids:
        name = skill_id.replace("_", " ").title()
        text = fonts.small.render(f"  + {name}", True, colors.TEXT_HEAL)
        surface.blit(text, (x, y))
        y += _LINE_H


def _draw_bonuses_section(
    surface: pygame.Surface, fonts: FontManager,
    option: SubclassOption, x: int, y: int,
) -> None:
    header = fonts.small.render("Passive Bonuses:", True, colors.PARTY_COLOR)
    surface.blit(header, (x, y))
    y += _LINE_H
    for bonus in option.passive_bonuses:
        sign = "+" if bonus.percent > 0 else ""
        label = f"  {sign}{bonus.percent:.0f}% {bonus.stat}"
        text = fonts.small.render(label, True, colors.TEXT_YELLOW)
        surface.blit(text, (x, y))
        y += _LINE_H


def _draw_controls(
    surface: pygame.Surface, fonts: FontManager,
) -> None:
    y = layout.WINDOW_HEIGHT - 30
    cx = layout.WINDOW_WIDTH // 2
    hint = "[1/A] Option A  [2/D] Option B  [ENTER] Confirm"
    text = fonts.small.render(hint, True, colors.TEXT_MUTED)
    surface.blit(text, (cx - text.get_width() // 2, y))
