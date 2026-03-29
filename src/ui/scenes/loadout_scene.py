"""LoadoutScene — tela de customizacao de spell loadout."""

from __future__ import annotations

from enum import Enum, auto
from typing import Callable, TYPE_CHECKING

import pygame

from src.core.combat.action_economy import ActionType
from src.core.skills.auto_fill import auto_fill_loadout
from src.core.skills.loadout_manager import LoadoutManager
from src.core.skills.skill import Skill
from src.core.skills.skill_pool_builder import build_skill_pool
from src.core.skills.slot_budget_calculator import calculate_slot_budget
from src.core.skills.slot_config import load_slot_config
from src.ui import colors, layout
from src.ui.font_manager import FontManager

if TYPE_CHECKING:
    from src.core.characters.character import Character

_LINE_H = 24
_SLOT_PANEL_X = 30
_POOL_PANEL_X = 500
_LIST_Y = 100
_MAX_POOL_VISIBLE = 16


class _Focus(Enum):
    CHAR = auto()
    SLOT = auto()
    POOL = auto()


class LoadoutScene:
    """Tela de customizacao de spell loadout por personagem."""

    def __init__(
        self,
        fonts: FontManager,
        party: list[Character],
        on_complete: Callable[[dict], None],
    ) -> None:
        self._fonts = fonts
        self._party = party
        self._on_complete = on_complete
        self._config = load_slot_config()
        self._focus = _Focus.CHAR
        self._char_index = 0
        self._slot_index = 0
        self._pool_index = 0
        self._pool_scroll = 0
        self._managers: dict[str, LoadoutManager] = {}
        self._pools: dict[str, list[Skill]] = {}
        self._init_managers()

    def _init_managers(self) -> None:
        """Cria LoadoutManager e pool pra cada personagem."""
        for char in self._party:
            cid = type(char).__name__.lower()
            budget = calculate_slot_budget(char.level, self._config)
            slot_count = self._config.base_slot_count
            mgr = LoadoutManager(slot_count, budget)
            pool = build_skill_pool(cid, char.level)
            auto_fill_loadout(pool, mgr)
            self._managers[char.name] = mgr
            self._pools[char.name] = pool

    def _current_manager(self) -> LoadoutManager:
        return self._managers[self._party[self._char_index].name]

    def _current_pool(self) -> list[Skill]:
        return self._pools[self._party[self._char_index].name]

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        key = event.key
        if key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
            self._confirm_all()
            return
        if key == pygame.K_RETURN:
            self._handle_confirm()
            return
        if key == pygame.K_TAB:
            self._cycle_focus()
            return
        if key == pygame.K_r:
            self._auto_fill_current()
            return
        self._handle_nav(key)

    def _handle_nav(self, key: int) -> None:
        if key in (pygame.K_UP, pygame.K_w):
            self._nav(-1)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self._nav(1)
        elif key in (pygame.K_LEFT, pygame.K_a):
            if self._focus == _Focus.CHAR:
                self._nav(-1)
        elif key in (pygame.K_RIGHT, pygame.K_d):
            if self._focus == _Focus.CHAR:
                self._nav(1)
        elif key == pygame.K_DELETE:
            self._remove_from_slot()

    def _nav(self, delta: int) -> None:
        if self._focus == _Focus.CHAR:
            limit = len(self._party) - 1
            self._char_index = _clamp(self._char_index + delta, 0, limit)
            self._slot_index = 0
            self._pool_index = 0
        elif self._focus == _Focus.SLOT:
            mgr = self._current_manager()
            limit = len(mgr.slots) - 1
            self._slot_index = _clamp(self._slot_index + delta, 0, limit)
        elif self._focus == _Focus.POOL:
            pool = self._current_pool()
            limit = max(0, len(pool) - 1)
            self._pool_index = _clamp(self._pool_index + delta, 0, limit)
            _adjust_scroll(self)

    def _cycle_focus(self) -> None:
        order = [_Focus.CHAR, _Focus.SLOT, _Focus.POOL]
        idx = order.index(self._focus)
        self._focus = order[(idx + 1) % len(order)]

    def _handle_confirm(self) -> None:
        if self._focus == _Focus.POOL:
            self._add_from_pool()
        elif self._focus == _Focus.SLOT:
            self._remove_from_slot()
        elif self._focus == _Focus.CHAR:
            self._cycle_focus()

    def _add_from_pool(self) -> None:
        pool = self._current_pool()
        if not pool or self._pool_index >= len(pool):
            return
        skill = pool[self._pool_index]
        self._current_manager().add_skill(self._slot_index, skill)

    def _remove_from_slot(self) -> None:
        mgr = self._current_manager()
        slots = mgr.slots
        if self._slot_index >= len(slots):
            return
        slot = slots[self._slot_index]
        if not slot.skills:
            return
        mgr.remove_skill(self._slot_index, slot.skills[-1].skill_id)

    def _auto_fill_current(self) -> None:
        pool = self._current_pool()
        mgr = self._current_manager()
        auto_fill_loadout(pool, mgr)

    def _confirm_all(self) -> None:
        """Aplica loadouts a todos os personagens e sai."""
        for char in self._party:
            mgr = self._managers.get(char.name)
            if mgr is not None:
                bar = mgr.build_skill_bar()
                char._skill_bar = bar
        self._on_complete({})

    def update(self, dt_ms: int) -> bool:
        return True

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(colors.BG_DARK)
        _draw_title(surface, self._fonts)
        self._draw_char_tabs(surface)
        self._draw_slots(surface)
        self._draw_pool(surface)
        _draw_controls(surface, self._fonts)

    def _draw_char_tabs(self, surface: pygame.Surface) -> None:
        x = _SLOT_PANEL_X
        for i, char in enumerate(self._party):
            sel = self._focus == _Focus.CHAR and i == self._char_index
            active = i == self._char_index
            color = colors.TEXT_YELLOW if sel else (
                colors.PARTY_COLOR if active else colors.TEXT_MUTED
            )
            cid = type(char).__name__
            label = f"  {char.name} ({cid})" if active else f"  {char.name}"
            text = self._fonts.small.render(label, True, color)
            surface.blit(text, (x + i * 120, 60))

    def _draw_slots(self, surface: pygame.Surface) -> None:
        mgr = self._current_manager()
        header = self._fonts.medium.render("Slots", True, colors.PARTY_COLOR)
        surface.blit(header, (_SLOT_PANEL_X, _LIST_Y - 30))
        for i, slot in enumerate(mgr.slots):
            sel = self._focus == _Focus.SLOT and i == self._slot_index
            _draw_slot(surface, self._fonts, _SLOT_PANEL_X, _LIST_Y + i * 80, slot, i, sel)

    def _draw_pool(self, surface: pygame.Surface) -> None:
        pool = self._current_pool()
        header = self._fonts.medium.render("Available Skills", True, colors.PARTY_COLOR)
        surface.blit(header, (_POOL_PANEL_X, _LIST_Y - 30))
        mgr = self._current_manager()
        used = mgr._assigned_ids
        end = self._pool_scroll + _MAX_POOL_VISIBLE
        for i, skill in enumerate(pool[self._pool_scroll:end]):
            real_i = self._pool_scroll + i
            sel = self._focus == _Focus.POOL and real_i == self._pool_index
            available = skill.skill_id not in used
            _draw_pool_skill(
                surface, self._fonts, _POOL_PANEL_X,
                _LIST_Y + i * _LINE_H, skill, sel, available,
            )


def _clamp(value: int, low: int, high: int) -> int:
    return max(low, min(value, high))


def _adjust_scroll(scene: LoadoutScene) -> None:
    if scene._pool_index < scene._pool_scroll:
        scene._pool_scroll = scene._pool_index
    visible_end = scene._pool_scroll + _MAX_POOL_VISIBLE
    if scene._pool_index >= visible_end:
        scene._pool_scroll = scene._pool_index - _MAX_POOL_VISIBLE + 1


def _draw_title(surface: pygame.Surface, fonts: FontManager) -> None:
    title = fonts.large.render("Skill Loadout", True, colors.TEXT_WHITE)
    cx = layout.WINDOW_WIDTH // 2
    surface.blit(title, (cx - title.get_width() // 2, 20))
    sub = fonts.small.render(
        "Customize skills for each character", True, colors.TEXT_MUTED,
    )
    surface.blit(sub, (cx - sub.get_width() // 2, 55))


def _draw_slot(
    surface: pygame.Surface, fonts: FontManager,
    x: int, y: int, slot, index: int, selected: bool,
) -> None:
    from src.core.skills.spell_slot import total_slot_cost
    used = total_slot_cost(slot)
    color = colors.TEXT_YELLOW if selected else colors.TEXT_WHITE
    header = fonts.small.render(
        f"Slot {index + 1} [{used}/{slot.max_cost}]", True, color,
    )
    surface.blit(header, (x, y))
    for j, skill in enumerate(slot.skills):
        sk_text = fonts.small.render(
            f"  {skill.name} ({skill.slot_cost})", True, colors.TEXT_MUTED,
        )
        surface.blit(sk_text, (x + 20, y + 20 + j * 18))


def _draw_pool_skill(
    surface: pygame.Surface, fonts: FontManager,
    x: int, y: int, skill: Skill,
    selected: bool, available: bool,
) -> None:
    if selected:
        color = colors.TEXT_YELLOW
    elif available:
        color = colors.TEXT_WHITE
    else:
        color = colors.TEXT_MUTED
    label = f"  {skill.name} (cost:{skill.slot_cost})"
    text = fonts.small.render(label, True, color)
    surface.blit(text, (x, y))


def _draw_controls(surface: pygame.Surface, fonts: FontManager) -> None:
    y = layout.WINDOW_HEIGHT - 30
    cx = layout.WINDOW_WIDTH // 2
    hint = "[TAB] Focus  [W/S] Nav  [ENTER] Add/Remove  [R] Auto  [ESC] Confirm"
    text = fonts.small.render(hint, True, colors.TEXT_MUTED)
    surface.blit(text, (cx - text.get_width() // 2, y))
