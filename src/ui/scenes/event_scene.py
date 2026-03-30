"""EventScene — tela de evento aleatorio com escolhas."""

from __future__ import annotations

from enum import Enum, auto
from typing import Callable

import pygame

from src.dungeon.events.event_template import EventTemplate
from src.ui import colors, layout
from src.ui.components.text_utils import draw_centered
from src.ui.font_manager import FontManager

_EVENT_COLOR = (120, 160, 220)
_CHOICE_SPACING = 36


class _Phase(Enum):
    CHOOSING = auto()
    RESULT = auto()


class EventScene:
    """Tela de evento: fase de escolha e fase de resultado."""

    def __init__(
        self,
        fonts: FontManager,
        event: EventTemplate,
        on_choice: Callable[[int], dict[str, object]],
        on_complete: Callable[[dict], None],
    ) -> None:
        self._fonts = fonts
        self._event = event
        self._on_choice = on_choice
        self._on_complete = on_complete
        self._phase = _Phase.CHOOSING
        self._choice_idx: int = 0
        self._result_text: str = ""
        self._effect_summary: dict[str, object] = {}

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if self._phase == _Phase.CHOOSING:
            self._handle_choosing(event.key)
        elif self._phase == _Phase.RESULT:
            self._handle_result(event.key)

    def _handle_choosing(self, key: int) -> None:
        """Processa input na fase de escolha."""
        idx = _key_to_choice_index(key)
        if idx is None or idx >= len(self._event.choices):
            return
        self._choice_idx = idx
        choice = self._event.choices[idx]
        self._effect_summary = self._on_choice(idx)
        self._result_text = choice.result_text
        self._phase = _Phase.RESULT

    def _handle_result(self, key: int) -> None:
        """Processa input na fase de resultado."""
        if key in (pygame.K_RETURN, pygame.K_SPACE):
            self._on_complete({})

    def update(self, dt_ms: int) -> bool:
        return True

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(colors.BG_DARK)
        cx = layout.WINDOW_WIDTH // 2
        draw_centered(surface, self._fonts.large, self._event.title, cx, 120, _EVENT_COLOR)
        if self._phase == _Phase.CHOOSING:
            _draw_choosing(surface, self._fonts, cx, self._event)
        else:
            _draw_result(surface, self._fonts, cx, self._result_text)


def _draw_choosing(
    surface: pygame.Surface,
    fonts: FontManager,
    cx: int,
    event: EventTemplate,
) -> None:
    """Desenha descricao e opcoes de escolha."""
    draw_centered(surface, fonts.small, event.description, cx, 190, colors.TEXT_WHITE)
    y = 280
    for i, choice in enumerate(event.choices):
        label = f"[{i + 1}] {choice.label}"
        draw_centered(surface, fonts.medium, label, cx, y + i * _CHOICE_SPACING, colors.TEXT_YELLOW)


def _draw_result(
    surface: pygame.Surface,
    fonts: FontManager,
    cx: int,
    result_text: str,
) -> None:
    """Desenha texto de resultado."""
    draw_centered(surface, fonts.medium, result_text, cx, 300, colors.TEXT_WHITE)
    draw_centered(surface, fonts.small, "[ENTER] Continuar", cx, 450, colors.TEXT_MUTED)


def _key_to_choice_index(key: int) -> int | None:
    """Converte tecla numerica em indice de escolha."""
    mapping = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2, pygame.K_4: 3, pygame.K_5: 4}
    return mapping.get(key)


