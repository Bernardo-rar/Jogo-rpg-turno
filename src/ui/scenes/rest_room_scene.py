"""RestRoomScene — escolha de ação de descanso."""

from __future__ import annotations

from typing import Callable

import pygame

from src.core.characters.character import Character
from src.dungeon.run.rest_actions import apply_rest_heal, apply_rest_meditate
from src.ui import colors, layout
from src.ui.font_manager import FontManager


class RestRoomScene:
    """Tela de rest room: heal ou meditate."""

    def __init__(
        self,
        fonts: FontManager,
        party: list[Character],
        on_complete: Callable[[dict], None],
        healing_mult: float = 1.0,
    ) -> None:
        self._fonts = fonts
        self._party = party
        self._on_complete = on_complete
        self._healing_mult = healing_mult
        self._result: dict[str, int] | None = None
        self._result_label: str = ""
        self._wait_ms: int = 0

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if self._result is not None:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._on_complete({})
            return
        if event.key == pygame.K_1:
            self._result = apply_rest_heal(self._party, self._healing_mult)
            self._result_label = "HP Recuperado"
        elif event.key == pygame.K_2:
            self._result = apply_rest_meditate(self._party)
            self._result_label = "Mana Restaurada"

    def update(self, dt_ms: int) -> bool:
        return True

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(colors.BG_DARK)
        _draw_header(surface, self._fonts)
        _draw_party_status(surface, self._fonts, self._party)
        if self._result is None:
            _draw_options(surface, self._fonts)
        else:
            _draw_results(
                surface, self._fonts,
                self._result_label, self._result,
            )


def _draw_header(surface: pygame.Surface, fonts: FontManager) -> None:
    title = fonts.large.render("Rest Room", True, colors.TEXT_WHITE)
    surface.blit(title, (layout.WINDOW_WIDTH // 2 - title.get_width() // 2, 30))
    sub = fonts.small.render(
        "Recupere suas forcas", True, colors.TEXT_MUTED,
    )
    surface.blit(sub, (layout.WINDOW_WIDTH // 2 - sub.get_width() // 2, 70))


def _draw_party_status(
    surface: pygame.Surface,
    fonts: FontManager,
    party: list[Character],
) -> None:
    y = 120
    for c in party:
        status = "MORTO" if not c.is_alive else f"HP: {c.current_hp}/{c.max_hp}  Mana: {c.current_mana}/{c.max_mana}"
        color = colors.DEAD_COLOR if not c.is_alive else colors.TEXT_WHITE
        text = fonts.small.render(f"  {c.name}: {status}", True, color)
        surface.blit(text, (100, y))
        y += 28


def _draw_options(surface: pygame.Surface, fonts: FontManager) -> None:
    y = 400
    opt1 = fonts.medium.render("[1] Curar (30% HP)", True, colors.TEXT_HEAL)
    opt2 = fonts.medium.render("[2] Meditar (40% Mana)", True, colors.MANA_BLUE)
    surface.blit(opt1, (layout.WINDOW_WIDTH // 2 - opt1.get_width() // 2, y))
    surface.blit(opt2, (layout.WINDOW_WIDTH // 2 - opt2.get_width() // 2, y + 40))


def _draw_results(
    surface: pygame.Surface,
    fonts: FontManager,
    label: str,
    results: dict[str, int],
) -> None:
    y = 380
    header = fonts.medium.render(label, True, colors.TEXT_YELLOW)
    surface.blit(header, (layout.WINDOW_WIDTH // 2 - header.get_width() // 2, y))
    y += 40
    for name, amount in results.items():
        text = fonts.small.render(f"  {name}: +{amount}", True, colors.TEXT_HEAL)
        surface.blit(text, (layout.WINDOW_WIDTH // 2 - text.get_width() // 2, y))
        y += 24
    y += 20
    cont = fonts.small.render(
        "[ENTER] Continuar", True, colors.TEXT_MUTED,
    )
    surface.blit(cont, (layout.WINDOW_WIDTH // 2 - cont.get_width() // 2, y))
