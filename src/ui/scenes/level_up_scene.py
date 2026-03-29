"""LevelUpScene — distribuicao de pontos de atributo apos level up."""

from __future__ import annotations

from enum import Enum, auto
from typing import Callable, TYPE_CHECKING

import pygame

from src.core.attributes.attribute_types import AttributeType
from src.core.progression.level_up_system import (
    MENTAL_ATTRIBUTES,
    PHYSICAL_ATTRIBUTES,
    LevelUpSystem,
)
from src.core.progression.recommended_distribution import (
    auto_distribute,
    load_recommended,
)
from src.ui import colors, layout
from src.ui.font_manager import FontManager

if TYPE_CHECKING:
    from src.core.characters.character import Character

_PHYSICAL_LIST = [
    AttributeType.STRENGTH,
    AttributeType.DEXTERITY,
    AttributeType.CONSTITUTION,
]
_MENTAL_LIST = [
    AttributeType.INTELLIGENCE,
    AttributeType.WISDOM,
    AttributeType.CHARISMA,
    AttributeType.MIND,
]

_LINE_H = 32
_LEFT_X = 80
_RIGHT_X = 650
_LIST_Y = 160
_LABEL_COLOR = colors.TEXT_WHITE
_VALUE_COLOR = colors.TEXT_YELLOW
_PLUS_COLOR = (80, 255, 80)
_HEADER_COLOR = colors.PARTY_COLOR


class _Focus(Enum):
    PHYSICAL = auto()
    MENTAL = auto()


class LevelUpScene:
    """Tela de distribuicao de pontos pos-level up."""

    def __init__(
        self,
        fonts: FontManager,
        party: list[Character],
        physical_points: int,
        mental_points: int,
        level_system: LevelUpSystem,
        on_complete: Callable[[dict], None],
    ) -> None:
        self._fonts = fonts
        self._party = party
        self._phys_total = physical_points
        self._mental_total = mental_points
        self._level_system = level_system
        self._on_complete = on_complete
        self._char_index = 0
        self._focus = _Focus.PHYSICAL
        self._attr_index = 0
        self._phys_dist = _zero_dist(_PHYSICAL_LIST)
        self._mental_dist = _zero_dist(_MENTAL_LIST)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        key = event.key
        if key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
            return
        if key == pygame.K_RETURN:
            self._confirm()
            return
        if key == pygame.K_TAB:
            self._toggle_focus()
            return
        if key in (pygame.K_UP, pygame.K_w):
            self._move_attr(-1)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self._move_attr(1)
        elif key in (pygame.K_RIGHT, pygame.K_d):
            self._add_point()
        elif key in (pygame.K_LEFT, pygame.K_a):
            self._remove_point()
        elif key == pygame.K_r:
            self._auto_distribute()

    def _current_char(self) -> Character:
        return self._party[self._char_index]

    def _auto_distribute(self) -> None:
        """Distribui pontos automaticamente por prioridade da classe."""
        configs = load_recommended()
        class_id = _get_class_id(self._current_char())
        config = configs.get(class_id)
        if config is None:
            return
        self._phys_dist = auto_distribute(self._phys_total, config.physical)
        self._mental_dist = auto_distribute(self._mental_total, config.mental)

    def _toggle_focus(self) -> None:
        if self._focus == _Focus.PHYSICAL:
            self._focus = _Focus.MENTAL
            self._attr_index = 0
        else:
            self._focus = _Focus.PHYSICAL
            self._attr_index = 0

    def _move_attr(self, delta: int) -> None:
        attrs = self._current_attrs()
        limit = len(attrs) - 1
        self._attr_index = max(0, min(limit, self._attr_index + delta))

    def _add_point(self) -> None:
        remaining = self._remaining()
        if remaining <= 0:
            return
        attr = self._selected_attr()
        dist = self._current_dist()
        dist[attr] = dist.get(attr, 0) + 1

    def _remove_point(self) -> None:
        attr = self._selected_attr()
        dist = self._current_dist()
        if dist.get(attr, 0) > 0:
            dist[attr] -= 1

    def _confirm(self) -> None:
        phys_remaining = self._phys_total - _sum_dist(self._phys_dist)
        mental_remaining = self._mental_total - _sum_dist(self._mental_dist)
        if phys_remaining > 0 or mental_remaining > 0:
            return
        self._apply_current_char()
        if self._char_index < len(self._party) - 1:
            self._char_index += 1
            self._reset_distribution()
            return
        self._on_complete({})

    def _apply_current_char(self) -> None:
        char = self._current_char()
        if self._phys_total > 0:
            self._level_system.distribute_physical_points(
                char, dict(self._phys_dist),
            )
        if self._mental_total > 0:
            self._level_system.distribute_mental_points(
                char, dict(self._mental_dist),
            )

    def _reset_distribution(self) -> None:
        """Reseta distribuição pra próximo char."""
        self._focus = _Focus.PHYSICAL
        self._attr_index = 0
        self._phys_dist = _zero_dist(_PHYSICAL_LIST)
        self._mental_dist = _zero_dist(_MENTAL_LIST)

    def _current_attrs(self) -> list[AttributeType]:
        if self._focus == _Focus.PHYSICAL:
            return _PHYSICAL_LIST
        return _MENTAL_LIST

    def _selected_attr(self) -> AttributeType:
        return self._current_attrs()[self._attr_index]

    def _current_dist(self) -> dict[AttributeType, int]:
        if self._focus == _Focus.PHYSICAL:
            return self._phys_dist
        return self._mental_dist

    def _remaining(self) -> int:
        if self._focus == _Focus.PHYSICAL:
            return self._phys_total - _sum_dist(self._phys_dist)
        return self._mental_total - _sum_dist(self._mental_dist)

    def update(self, dt_ms: int) -> bool:
        return True

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(colors.BG_DARK)
        char = self._current_char()
        char_label = f"{char.name} ({self._char_index + 1}/{len(self._party)})"
        _draw_title(surface, self._fonts, char.level, char_label)
        _draw_section(
            surface, self._fonts, _LEFT_X, "Physical",
            _PHYSICAL_LIST, self._phys_dist, char,
            self._phys_total,
            self._focus == _Focus.PHYSICAL,
            self._attr_index if self._focus == _Focus.PHYSICAL else -1,
        )
        _draw_section(
            surface, self._fonts, _RIGHT_X, "Mental",
            _MENTAL_LIST, self._mental_dist, char,
            self._mental_total,
            self._focus == _Focus.MENTAL,
            self._attr_index if self._focus == _Focus.MENTAL else -1,
        )
        _draw_controls(surface, self._fonts)
        _draw_remaining(surface, self._fonts, self)


def _get_class_id(char: Character) -> str:
    """Extrai class_id a partir do tipo da classe."""
    return type(char).__name__.lower()


def _zero_dist(attrs: list[AttributeType]) -> dict[AttributeType, int]:
    return {a: 0 for a in attrs}


def _sum_dist(dist: dict[AttributeType, int]) -> int:
    return sum(dist.values())


def _draw_title(
    surface: pygame.Surface, fonts: FontManager,
    level: int, char_label: str = "",
) -> None:
    title = fonts.large.render(
        f"Level Up! (Lv.{level})", True, _VALUE_COLOR,
    )
    cx = layout.WINDOW_WIDTH // 2
    surface.blit(title, (cx - title.get_width() // 2, 30))
    label = char_label or "Distribua pontos"
    sub = fonts.small.render(label, True, colors.TEXT_MUTED,
    )
    surface.blit(sub, (cx - sub.get_width() // 2, 70))


def _draw_section(
    surface: pygame.Surface,
    fonts: FontManager,
    x: int,
    title: str,
    attrs: list[AttributeType],
    dist: dict[AttributeType, int],
    char: Character,
    total: int,
    is_active: bool,
    selected: int,
) -> None:
    spent = _sum_dist(dist)
    remaining = total - spent
    header_color = _HEADER_COLOR if is_active else colors.TEXT_MUTED
    header = fonts.medium.render(
        f"{title} ({remaining}/{total})", True, header_color,
    )
    surface.blit(header, (x, _LIST_Y - 35))
    for i, attr in enumerate(attrs):
        _draw_attr_line(
            surface, fonts, x, _LIST_Y + i * _LINE_H,
            attr, char, dist.get(attr, 0),
            is_active and i == selected,
        )


def _draw_attr_line(
    surface: pygame.Surface,
    fonts: FontManager,
    x: int, y: int,
    attr: AttributeType,
    char: Character,
    added: int,
    is_selected: bool,
) -> None:
    current = char._attributes.get(attr)
    name_color = _VALUE_COLOR if is_selected else _LABEL_COLOR
    name = fonts.small.render(f"  {attr.name}", True, name_color)
    surface.blit(name, (x, y))
    val = fonts.small.render(f"{current}", True, _LABEL_COLOR)
    surface.blit(val, (x + 200, y))
    if added > 0:
        plus = fonts.small.render(f"+{added}", True, _PLUS_COLOR)
        surface.blit(plus, (x + 240, y))
    if is_selected:
        arrow = fonts.small.render("<  >", True, _VALUE_COLOR)
        surface.blit(arrow, (x + 290, y))


def _draw_controls(surface: pygame.Surface, fonts: FontManager) -> None:
    y = layout.WINDOW_HEIGHT - 30
    cx = layout.WINDOW_WIDTH // 2
    hint = "[W/S] Attr  [A/D] +/-  [TAB] Phys/Mental  [R] Auto  [ENTER] Confirm"
    text = fonts.small.render(hint, True, colors.TEXT_MUTED)
    surface.blit(text, (cx - text.get_width() // 2, y))


def _draw_remaining(
    surface: pygame.Surface, fonts: FontManager, scene: LevelUpScene,
) -> None:
    phys_rem = scene._phys_total - _sum_dist(scene._phys_dist)
    mental_rem = scene._mental_total - _sum_dist(scene._mental_dist)
    done = phys_rem == 0 and mental_rem == 0
    if done:
        text = fonts.medium.render(
            "[ENTER] Confirmar distribuicao", True, _VALUE_COLOR,
        )
    else:
        text = fonts.medium.render(
            "Distribua todos os pontos para confirmar", True, colors.TEXT_MUTED,
        )
    cx = layout.WINDOW_WIDTH // 2
    surface.blit(text, (cx - text.get_width() // 2, layout.WINDOW_HEIGHT - 70))
