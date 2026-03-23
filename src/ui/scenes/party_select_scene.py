"""PartySelectScene — seleção de 4 classes para a party."""

from __future__ import annotations

from typing import Callable

import pygame

from src.core.classes.class_id import ClassId
from src.dungeon.run.party_factory import is_frontliner
from src.dungeon.run.party_selection import PartySelection
from src.ui import colors, layout
from src.ui.font_manager import FontManager

_ALL_CLASSES = tuple(ClassId)
_KEYS = [
    pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5,
    pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0,
    pygame.K_a, pygame.K_b, pygame.K_c,
]
_GRID_X = 100
_GRID_Y = 120
_COL_WIDTH = 350
_ROW_HEIGHT = 40
_COLS = 3
_LABEL_KEYS = "1234567890ABC"


class PartySelectScene:
    """Tela de seleção de party com toggle de classes."""

    def __init__(
        self,
        fonts: FontManager,
        on_complete: Callable[[dict], None],
    ) -> None:
        self._fonts = fonts
        self._on_complete = on_complete
        self._selection = PartySelection(_ALL_CLASSES)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_RETURN and self._selection.is_valid():
            self._on_complete({"class_ids": list(self._selection.selected)})
            return
        for i, key in enumerate(_KEYS):
            if event.key == key and i < len(_ALL_CLASSES):
                cid = _ALL_CLASSES[i]
                if cid in self._selection.selected:
                    self._selection.deselect(cid)
                else:
                    self._selection.select(cid)
                return

    def update(self, dt_ms: int) -> bool:
        return True

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(colors.BG_DARK)
        _draw_title(surface, self._fonts)
        _draw_class_grid(surface, self._fonts, self._selection)
        _draw_status(surface, self._fonts, self._selection)

    @property
    def selection(self) -> PartySelection:
        return self._selection


def _draw_title(surface: pygame.Surface, fonts: FontManager) -> None:
    title = fonts.large.render(
        "Escolha sua Party (4 classes)", True, colors.TEXT_WHITE,
    )
    surface.blit(title, (layout.WINDOW_WIDTH // 2 - title.get_width() // 2, 40))


def _draw_class_grid(
    surface: pygame.Surface,
    fonts: FontManager,
    selection: PartySelection,
) -> None:
    for i, cid in enumerate(_ALL_CLASSES):
        col = i // 5
        row = i % 5
        x = _GRID_X + col * _COL_WIDTH
        y = _GRID_Y + row * _ROW_HEIGHT
        selected = cid in selection.selected
        color = colors.TEXT_YELLOW if selected else colors.TEXT_WHITE
        front = " [F]" if is_frontliner(cid) else ""
        label = f"[{_LABEL_KEYS[i]}] {cid.value.capitalize()}{front}"
        if selected:
            label = f">> {label} <<"
        text = fonts.medium.render(label, True, color)
        surface.blit(text, (x, y))


def _draw_status(
    surface: pygame.Surface,
    fonts: FontManager,
    selection: PartySelection,
) -> None:
    count = len(selection.selected)
    valid = selection.is_valid()
    status = f"Selecionados: {count}/4"
    color = colors.TEXT_HEAL if valid else colors.TEXT_WHITE
    text = fonts.medium.render(status, True, color)
    surface.blit(text, (layout.WINDOW_WIDTH // 2 - text.get_width() // 2, 450))
    if valid:
        confirm = fonts.medium.render(
            "[ENTER] Confirmar", True, colors.TEXT_YELLOW,
        )
        surface.blit(
            confirm,
            (layout.WINDOW_WIDTH // 2 - confirm.get_width() // 2, 490),
        )
    elif count == 4:
        warn = fonts.small.render(
            "Precisa de pelo menos 1 front-liner [F]",
            True, colors.TEXT_DAMAGE,
        )
        surface.blit(
            warn,
            (layout.WINDOW_WIDTH // 2 - warn.get_width() // 2, 490),
        )
