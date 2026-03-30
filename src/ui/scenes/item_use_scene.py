"""ItemUseScene — tela de uso de consumiveis fora de combate."""

from __future__ import annotations

from enum import Enum, auto
from typing import Callable, TYPE_CHECKING

import pygame

from src.core.items.inventory_slot import InventorySlot
from src.dungeon.run.item_use_actions import (
    apply_consumable_on_target,
    get_usable_consumables,
)
from src.ui import colors, layout
from src.ui.font_manager import FontManager

if TYPE_CHECKING:
    from src.core.characters.character import Character

_LINE_H = 28
_ITEM_PANEL_X = 40
_TARGET_PANEL_X = 500
_LIST_START_Y = 130
_RESULT_DISPLAY_Y = 560
_MAX_VISIBLE_ITEMS = 12


class _Phase(Enum):
    CHOOSE_ITEM = auto()
    CHOOSE_TARGET = auto()
    RESULT = auto()


class ItemUseScene:
    """Tela de uso de consumiveis fora de combate."""

    def __init__(
        self,
        fonts: FontManager,
        party: list[Character],
        on_complete: Callable[[dict], None],
        gold: int = 0,
    ) -> None:
        self._fonts = fonts
        self._party = party
        self._on_complete = on_complete
        self._gold = gold
        self._inventory = self._resolve_inventory()
        self._usable: list[InventorySlot] = self._refresh_usable()
        self._phase = _Phase.CHOOSE_ITEM
        self._item_index = 0
        self._target_index = 0
        self._result_text = ""

    def _resolve_inventory(self) -> object:
        """Busca primeiro inventario nao-vazio da party."""
        for char in self._party:
            inv = char.inventory
            if inv is not None and len(inv.slots) > 0:
                return inv
        for char in self._party:
            if char.inventory is not None:
                return char.inventory
        return None

    def _refresh_usable(self) -> list[InventorySlot]:
        """Atualiza lista de consumiveis usaveis de toda a party."""
        usable: list[InventorySlot] = []
        for char in self._party:
            inv = char.inventory
            if inv is None:
                continue
            usable.extend(get_usable_consumables(inv))
        return usable

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        handler = _PHASE_HANDLERS.get(self._phase)
        if handler is not None:
            handler(self, event)

    def _handle_choose_item(self, event: pygame.event.Event) -> None:
        """Input na fase de escolher item."""
        if event.key == pygame.K_ESCAPE:
            self._on_complete({})
            return
        if event.key == pygame.K_UP:
            self._item_index = max(0, self._item_index - 1)
        elif event.key == pygame.K_DOWN:
            limit = max(0, len(self._usable) - 1)
            self._item_index = min(limit, self._item_index + 1)
        elif event.key == pygame.K_RETURN:
            self._enter_target_phase()
        else:
            idx = _key_to_index(event.key)
            if idx is not None and idx < len(self._usable):
                self._item_index = idx
                self._enter_target_phase()

    def _enter_target_phase(self) -> None:
        """Transiciona para fase de escolher alvo."""
        if not self._usable:
            return
        self._phase = _Phase.CHOOSE_TARGET
        self._target_index = 0

    def _handle_choose_target(self, event: pygame.event.Event) -> None:
        """Input na fase de escolher alvo."""
        if event.key == pygame.K_ESCAPE:
            self._phase = _Phase.CHOOSE_ITEM
            return
        if event.key == pygame.K_UP:
            self._target_index = max(0, self._target_index - 1)
        elif event.key == pygame.K_DOWN:
            limit = max(0, len(self._party) - 1)
            self._target_index = min(limit, self._target_index + 1)
        elif event.key == pygame.K_RETURN:
            self._use_item()
        else:
            idx = _key_to_index(event.key)
            if idx is not None and idx < len(self._party):
                self._target_index = idx
                self._use_item()

    def _use_item(self) -> None:
        """Aplica consumivel no alvo e remove do inventario."""
        slot = self._usable[self._item_index]
        target = self._party[self._target_index]
        self._result_text = apply_consumable_on_target(
            slot.consumable, target,
        )
        self._consume_from_inventory(slot)
        self._phase = _Phase.RESULT

    def _consume_from_inventory(self, slot: InventorySlot) -> None:
        """Remove 1 unidade do inventario e atualiza lista."""
        cid = slot.consumable.consumable_id
        for char in self._party:
            inv = char.inventory
            if inv is not None and inv.has_item(cid):
                inv.remove_item(cid)
                break
        self._usable = self._refresh_usable()
        self._clamp_item_index()

    def _clamp_item_index(self) -> None:
        """Mantem item_index dentro dos limites."""
        if not self._usable:
            self._item_index = 0
            return
        limit = len(self._usable) - 1
        self._item_index = min(self._item_index, limit)

    def _handle_result(self, event: pygame.event.Event) -> None:
        """Input na fase de resultado."""
        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
            if self._usable:
                self._phase = _Phase.CHOOSE_ITEM
            else:
                self._on_complete({})
        elif event.key == pygame.K_ESCAPE:
            self._on_complete({})

    def update(self, dt_ms: int) -> bool:
        return True

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(colors.BG_DARK)
        _draw_header(surface, self._fonts)
        if self._gold > 0:
            gold_text = self._fonts.medium.render(
                f"Gold: {self._gold}", True, colors.TEXT_YELLOW,
            )
            surface.blit(gold_text, (layout.WINDOW_WIDTH - gold_text.get_width() - 40, 30))
        _draw_item_list(
            surface, self._fonts, self._usable,
            self._item_index, self._phase == _Phase.CHOOSE_ITEM,
        )
        _draw_target_list(
            surface, self._fonts, self._party,
            self._target_index, self._phase == _Phase.CHOOSE_TARGET,
        )
        if self._phase == _Phase.RESULT:
            _draw_result(surface, self._fonts, self._result_text)
        _draw_controls(surface, self._fonts, self._phase)


def _draw_header(surface: pygame.Surface, fonts: FontManager) -> None:
    title = fonts.large.render("Use Items", True, colors.TEXT_WHITE)
    cx = layout.WINDOW_WIDTH // 2
    surface.blit(title, (cx - title.get_width() // 2, 30))
    sub = fonts.small.render(
        "Selecione um item e um alvo", True, colors.TEXT_MUTED,
    )
    surface.blit(sub, (cx - sub.get_width() // 2, 65))


def _draw_item_list(
    surface: pygame.Surface,
    fonts: FontManager,
    usable: list[InventorySlot],
    selected: int,
    is_active: bool,
) -> None:
    header = fonts.medium.render("Items", True, colors.PARTY_COLOR)
    surface.blit(header, (_ITEM_PANEL_X, 100))
    if not usable:
        empty = fonts.small.render("  (no items)", True, colors.TEXT_MUTED)
        surface.blit(empty, (_ITEM_PANEL_X, _LIST_START_Y))
        return
    for i, slot in enumerate(usable[:_MAX_VISIBLE_ITEMS]):
        _draw_item_line(surface, fonts, slot, i, selected, is_active)


def _draw_item_line(
    surface: pygame.Surface,
    fonts: FontManager,
    slot: InventorySlot,
    index: int,
    selected: int,
    is_active: bool,
) -> None:
    is_sel = is_active and index == selected
    color = colors.TEXT_YELLOW if is_sel else colors.TEXT_WHITE
    label = f"[{index + 1}] {slot.consumable.name} x{slot.quantity}"
    text = fonts.small.render(label, True, color)
    y = _LIST_START_Y + index * _LINE_H
    surface.blit(text, (_ITEM_PANEL_X, y))


def _draw_target_list(
    surface: pygame.Surface,
    fonts: FontManager,
    party: list[Character],
    selected: int,
    is_active: bool,
) -> None:
    header = fonts.medium.render("Targets", True, colors.PARTY_COLOR)
    surface.blit(header, (_TARGET_PANEL_X, 100))
    for i, char in enumerate(party):
        _draw_target_line(
            surface, fonts, char, i, selected, is_active,
        )


def _draw_target_line(
    surface: pygame.Surface,
    fonts: FontManager,
    char: Character,
    index: int,
    selected: int,
    is_active: bool,
) -> None:
    is_sel = is_active and index == selected
    if not char.is_alive:
        color = colors.DEAD_COLOR
    elif is_sel:
        color = colors.TEXT_YELLOW
    else:
        color = colors.TEXT_WHITE
    status = _char_status(char)
    label = f"[{index + 1}] {char.name}: {status}"
    text = fonts.small.render(label, True, color)
    y = _LIST_START_Y + index * _LINE_H
    surface.blit(text, (_TARGET_PANEL_X, y))


def _char_status(char: Character) -> str:
    """Formata status curto do personagem."""
    if not char.is_alive:
        return "DEAD"
    return f"HP {char.current_hp}/{char.max_hp}  MP {char.current_mana}/{char.max_mana}"


def _draw_result(
    surface: pygame.Surface, fonts: FontManager, text: str,
) -> None:
    rendered = fonts.medium.render(text, True, colors.TEXT_HEAL)
    cx = layout.WINDOW_WIDTH // 2
    surface.blit(rendered, (cx - rendered.get_width() // 2, _RESULT_DISPLAY_Y))


def _draw_controls(
    surface: pygame.Surface, fonts: FontManager, phase: _Phase,
) -> None:
    y = layout.WINDOW_HEIGHT - 30
    cx = layout.WINDOW_WIDTH // 2
    hints = {
        _Phase.CHOOSE_ITEM: "[1-9/UP/DOWN] Select  [ENTER] Confirm  [ESC] Exit",
        _Phase.CHOOSE_TARGET: "[1-9/UP/DOWN] Select  [ENTER] Use  [ESC] Back",
        _Phase.RESULT: "[ENTER] Continue  [ESC] Exit",
    }
    hint = hints.get(phase, "")
    text = fonts.small.render(hint, True, colors.TEXT_MUTED)
    surface.blit(text, (cx - text.get_width() // 2, y))


def _key_to_index(key: int) -> int | None:
    """Mapeia teclas numericas para indice 0-based."""
    mapping = {
        pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2,
        pygame.K_4: 3, pygame.K_5: 4, pygame.K_6: 5,
        pygame.K_7: 6, pygame.K_8: 7, pygame.K_9: 8,
    }
    return mapping.get(key)


_PHASE_HANDLERS: dict[_Phase, object] = {
    _Phase.CHOOSE_ITEM: ItemUseScene._handle_choose_item,
    _Phase.CHOOSE_TARGET: ItemUseScene._handle_choose_target,
    _Phase.RESULT: ItemUseScene._handle_result,
}
