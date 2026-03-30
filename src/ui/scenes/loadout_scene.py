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
            _populate_from_current(mgr, char)
            self._managers[char.name] = mgr
            self._pools[char.name] = pool

    def _current_manager(self) -> LoadoutManager:
        return self._managers[self._party[self._char_index].name]

    def _current_pool(self) -> list[Skill]:
        return self._pools[self._party[self._char_index].name]

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return
        _handle_key(self, event.key)

    def update(self, dt_ms: int) -> bool:
        return True

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(colors.BG_DARK)
        _draw_title(surface, self._fonts)
        _draw_char_tabs(surface, self._fonts, self._party, self._char_index, self._focus)
        _draw_slots_panel(surface, self._fonts, self._current_manager(), self._focus, self._slot_index)
        _draw_pool_panel(surface, self._fonts, self._current_pool(), self._current_manager(), self._focus, self._pool_index, self._pool_scroll)
        _draw_controls(surface, self._fonts)


def _handle_key(s: LoadoutScene, key: int) -> None:
    if key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
        _confirm_all(s)
        return
    if key == pygame.K_RETURN:
        _handle_confirm(s)
        return
    if key == pygame.K_TAB:
        _cycle_focus(s)
        return
    if key == pygame.K_r:
        _auto_fill_current(s)
        return
    _handle_nav(s, key)


def _handle_nav(s: LoadoutScene, key: int) -> None:
    if key in (pygame.K_UP, pygame.K_w):
        _nav(s, -1)
    elif key in (pygame.K_DOWN, pygame.K_s):
        _nav(s, 1)
    elif key in (pygame.K_LEFT, pygame.K_a) and s._focus == _Focus.CHAR:
        _nav(s, -1)
    elif key in (pygame.K_RIGHT, pygame.K_d) and s._focus == _Focus.CHAR:
        _nav(s, 1)
    elif key == pygame.K_DELETE:
        _remove_from_slot(s)


def _nav(s: LoadoutScene, delta: int) -> None:
    if s._focus == _Focus.CHAR:
        limit = len(s._party) - 1
        s._char_index = _clamp(s._char_index + delta, 0, limit)
        s._slot_index = 0
        s._pool_index = 0
    elif s._focus == _Focus.SLOT:
        limit = len(s._current_manager().slots) - 1
        s._slot_index = _clamp(s._slot_index + delta, 0, limit)
    elif s._focus == _Focus.POOL:
        limit = max(0, len(s._current_pool()) - 1)
        s._pool_index = _clamp(s._pool_index + delta, 0, limit)
        _adjust_scroll(s)


def _cycle_focus(s: LoadoutScene) -> None:
    order = [_Focus.CHAR, _Focus.SLOT, _Focus.POOL]
    idx = order.index(s._focus)
    s._focus = order[(idx + 1) % len(order)]


def _handle_confirm(s: LoadoutScene) -> None:
    if s._focus == _Focus.POOL:
        _add_from_pool(s)
    elif s._focus == _Focus.SLOT:
        _remove_from_slot(s)
    elif s._focus == _Focus.CHAR:
        _cycle_focus(s)


def _add_from_pool(s: LoadoutScene) -> None:
    pool = s._current_pool()
    if not pool or s._pool_index >= len(pool):
        return
    s._current_manager().add_skill(s._slot_index, pool[s._pool_index])


def _remove_from_slot(s: LoadoutScene) -> None:
    mgr = s._current_manager()
    slots = mgr.slots
    if s._slot_index >= len(slots):
        return
    slot = slots[s._slot_index]
    if slot.skills:
        mgr.remove_skill(s._slot_index, slot.skills[-1].skill_id)


def _auto_fill_current(s: LoadoutScene) -> None:
    auto_fill_loadout(s._current_pool(), s._current_manager())


def _populate_from_current(mgr: LoadoutManager, char) -> None:
    """Populates manager with the char's existing skill bar skills."""
    bar = char.skill_bar
    if bar is None:
        return
    for slot_idx, slot in enumerate(bar.slots):
        if slot_idx >= len(mgr.slots):
            break
        for skill in slot.skills:
            mgr.add_skill(slot_idx, skill)


def _confirm_all(s: LoadoutScene) -> None:
    for char in s._party:
        mgr = s._managers.get(char.name)
        if mgr is not None:
            char._skill_bar = mgr.build_skill_bar()
    s._on_complete({})


def _draw_char_tabs(
    surface: pygame.Surface, fonts: FontManager,
    party: list, char_index: int, focus: _Focus,
) -> None:
    x = _SLOT_PANEL_X
    for i, char in enumerate(party):
        sel = focus == _Focus.CHAR and i == char_index
        active = i == char_index
        color = colors.TEXT_YELLOW if sel else (
            colors.PARTY_COLOR if active else colors.TEXT_MUTED
        )
        cid = type(char).__name__
        label = f"  {char.name} ({cid})" if active else f"  {char.name}"
        text = fonts.small.render(label, True, color)
        surface.blit(text, (x + i * 120, 60))


def _draw_slots_panel(
    surface: pygame.Surface, fonts: FontManager,
    mgr: LoadoutManager, focus: _Focus, slot_index: int,
) -> None:
    header = fonts.medium.render("Slots", True, colors.PARTY_COLOR)
    surface.blit(header, (_SLOT_PANEL_X, _LIST_Y - 30))
    for i, slot in enumerate(mgr.slots):
        sel = focus == _Focus.SLOT and i == slot_index
        _draw_slot(surface, fonts, _SLOT_PANEL_X, _LIST_Y + i * 80, slot, i, sel)


def _draw_pool_panel(
    surface: pygame.Surface, fonts: FontManager,
    pool: list[Skill], mgr: LoadoutManager,
    focus: _Focus, pool_index: int, pool_scroll: int,
) -> None:
    header = fonts.medium.render("Available Skills", True, colors.PARTY_COLOR)
    surface.blit(header, (_POOL_PANEL_X, _LIST_Y - 30))
    used = mgr._assigned_ids
    end = pool_scroll + _MAX_POOL_VISIBLE
    for i, skill in enumerate(pool[pool_scroll:end]):
        real_i = pool_scroll + i
        sel = focus == _Focus.POOL and real_i == pool_index
        available = skill.skill_id not in used
        _draw_pool_skill(surface, fonts, _POOL_PANEL_X, _LIST_Y + i * _LINE_H, skill, sel, available)


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
