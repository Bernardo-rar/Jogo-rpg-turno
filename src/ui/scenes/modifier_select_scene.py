"""ModifierSelectScene — selecao de modifiers antes da run."""

from __future__ import annotations

from typing import Callable

import pygame

from src.dungeon.modifiers.run_modifier import ModifierCategory, RunModifier
from src.ui import colors, layout
from src.ui.font_manager import FontManager

_CARD_WIDTH = 340
_CARD_HEIGHT = 280
_CARD_SPACING = 30
_CARD_Y = 180
_BORDER_WIDTH = 3
_ACTIVE_BORDER_WIDTH = 4

_CATEGORY_COLORS: dict[ModifierCategory, tuple[int, int, int]] = {
    ModifierCategory.DIFFICULTY: (220, 60, 60),
    ModifierCategory.ECONOMY: (255, 220, 80),
    ModifierCategory.CHAOS: (180, 80, 220),
    ModifierCategory.RESTRICTION: (140, 140, 160),
}

_TOGGLE_KEYS = (pygame.K_1, pygame.K_2, pygame.K_3)


class ModifierSelectScene:
    """Tela de selecao de modifiers para a run."""

    def __init__(
        self,
        fonts: FontManager,
        offered: list[RunModifier],
        on_complete: Callable[[dict], None],
    ) -> None:
        self._fonts = fonts
        self._offered = offered
        self._active: set[int] = set()
        self._on_complete = on_complete

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_RETURN:
            self._confirm()
            return
        self._handle_toggle(event.key)

    def _handle_toggle(self, key: int) -> None:
        """Alterna selecao do modifier correspondente a tecla."""
        for i, toggle_key in enumerate(_TOGGLE_KEYS):
            if key == toggle_key and i < len(self._offered):
                _toggle_set(self._active, i)
                return

    def _confirm(self) -> None:
        """Confirma selecao e chama callback."""
        selected = [self._offered[i] for i in sorted(self._active)]
        self._on_complete({"modifiers": selected})

    def update(self, dt_ms: int) -> bool:
        return True

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(colors.BG_DARK)
        _draw_title(surface, self._fonts)
        _draw_cards(surface, self._fonts, self._offered, self._active)
        _draw_footer(surface, self._fonts)


def _toggle_set(active: set[int], index: int) -> None:
    """Alterna presenca de index no set."""
    if index in active:
        active.discard(index)
    else:
        active.add(index)


def _draw_title(surface: pygame.Surface, fonts: FontManager) -> None:
    title = fonts.large.render(
        "Run Modifiers", True, colors.TEXT_WHITE,
    )
    cx = layout.WINDOW_WIDTH // 2 - title.get_width() // 2
    surface.blit(title, (cx, 40))
    sub = fonts.small.render(
        "Escolha modifiers para sua run (opcional)",
        True, colors.TEXT_MUTED,
    )
    surface.blit(sub, (layout.WINDOW_WIDTH // 2 - sub.get_width() // 2, 80))


def _draw_cards(
    surface: pygame.Surface,
    fonts: FontManager,
    offered: list[RunModifier],
    active: set[int],
) -> None:
    total_w = len(offered) * _CARD_WIDTH + (len(offered) - 1) * _CARD_SPACING
    start_x = (layout.WINDOW_WIDTH - total_w) // 2
    for i, mod in enumerate(offered):
        x = start_x + i * (_CARD_WIDTH + _CARD_SPACING)
        is_active = i in active
        _draw_single_card(surface, fonts, mod, x, _CARD_Y, i, is_active)


def _draw_single_card(
    surface: pygame.Surface,
    fonts: FontManager,
    mod: RunModifier,
    x: int, y: int,
    index: int,
    is_active: bool,
) -> None:
    bg = colors.BG_PANEL if is_active else (25, 25, 35)
    border_color = colors.TEXT_YELLOW if is_active else colors.BG_PANEL_BORDER
    bw = _ACTIVE_BORDER_WIDTH if is_active else _BORDER_WIDTH
    rect = pygame.Rect(x, y, _CARD_WIDTH, _CARD_HEIGHT)
    pygame.draw.rect(surface, bg, rect)
    pygame.draw.rect(surface, border_color, rect, bw)
    _draw_card_content(surface, fonts, mod, x, y, index)


def _draw_card_content(
    surface: pygame.Surface,
    fonts: FontManager,
    mod: RunModifier,
    x: int, y: int,
    index: int,
) -> None:
    cat_color = _CATEGORY_COLORS.get(mod.category, colors.TEXT_WHITE)
    key_label = fonts.medium.render(f"[{index + 1}]", True, colors.MENU_KEY_COLOR)
    surface.blit(key_label, (x + 10, y + 10))
    name_label = fonts.medium.render(mod.name, True, cat_color)
    surface.blit(name_label, (x + 50, y + 10))
    cat_text = fonts.small.render(mod.category.value, True, cat_color)
    surface.blit(cat_text, (x + 10, y + 45))
    _draw_description(surface, fonts, mod.description, x + 10, y + 80)
    _draw_effects_summary(surface, fonts, mod, x + 10, y + 160)


def _draw_description(
    surface: pygame.Surface,
    fonts: FontManager,
    text: str,
    x: int, y: int,
) -> None:
    label = fonts.small.render(text, True, colors.TEXT_WHITE)
    surface.blit(label, (x, y))


def _draw_effects_summary(
    surface: pygame.Surface,
    fonts: FontManager,
    mod: RunModifier,
    x: int, y: int,
) -> None:
    lines = _build_effect_lines(mod)
    for i, line in enumerate(lines):
        color = colors.TEXT_DAMAGE if "-" in line else colors.TEXT_HEAL
        label = fonts.small.render(line, True, color)
        surface.blit(label, (x, y + i * 20))


def _build_effect_lines(mod: RunModifier) -> list[str]:
    """Gera linhas de resumo dos efeitos do modifier."""
    lines: list[str] = []
    eff = mod.effect
    _add_mult_line(lines, "Dmg Dealt", eff.damage_dealt_mult)
    _add_mult_line(lines, "Dmg Taken", eff.damage_taken_mult)
    _add_mult_line(lines, "Healing", eff.healing_mult)
    _add_mult_line(lines, "Gold", eff.gold_mult)
    _add_mult_line(lines, "Score", eff.score_mult)
    return lines


def _add_mult_line(
    lines: list[str], label: str, value: float,
) -> None:
    """Adiciona linha formatada se o valor diferir de 1.0."""
    if value == 1.0:
        return
    pct = int((value - 1.0) * 100)
    sign = "+" if pct > 0 else ""
    lines.append(f"{label}: {sign}{pct}%")


def _draw_footer(surface: pygame.Surface, fonts: FontManager) -> None:
    text = fonts.medium.render(
        "[ENTER] Start Run", True, colors.TEXT_YELLOW,
    )
    cx = layout.WINDOW_WIDTH // 2 - text.get_width() // 2
    surface.blit(text, (cx, layout.WINDOW_HEIGHT - 60))
