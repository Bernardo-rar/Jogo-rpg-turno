"""CombatInputHandler — processa input de teclado para combate."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import pygame

from src.core.combat.player_action import PlayerAction, PlayerActionType
from src.ui.components.combat_log_panel import CombatLogPanel
from src.ui.components.pause_menu import (
    PauseMenuResult,
    handle_pause_input,
)
from src.ui.components.qte_overlay import QteOverlay
from src.ui.components.speed_indicator import (
    SPEED_OPTIONS,
    next_speed_index,
)
from src.ui.input.action_menu import ActionMenu
from src.ui.input.menu_state import MenuLevel
from src.ui.scenes.interactive_combat import InteractiveCombatScene, TurnPhase

_KEY_MAP = {
    pygame.K_1: 1, pygame.K_2: 2, pygame.K_3: 3,
    pygame.K_4: 4, pygame.K_5: 5, pygame.K_6: 6,
    pygame.K_7: 7, pygame.K_8: 8, pygame.K_9: 9,
}

_NAV_UP = frozenset({pygame.K_UP, pygame.K_w})
_NAV_DOWN = frozenset({pygame.K_DOWN, pygame.K_s})

_ITEM_KEY = 4


@dataclass
class InputState:
    """Mutable UI state shared between input handler and scene."""

    menu: ActionMenu | None = None
    menu_combatant: str | None = None
    speed_index: int = 0
    speed_mult: float = field(default_factory=lambda: SPEED_OPTIONS[0])
    show_help: bool = False
    show_pause: bool = False
    qte_overlay: QteOverlay | None = None
    qte_pending_action: PlayerAction | None = None


class CombatInputHandler:
    """Processa input de teclado para o combate jogavel."""

    def __init__(
        self,
        scene: InteractiveCombatScene,
        state: InputState,
    ) -> None:
        self._scene = scene
        self._state = state
        self._log: CombatLogPanel | None = None
        self._on_complete: Callable[[], None] | None = None
        self._on_forfeit: Callable[[], None] | None = None

    def set_callbacks(
        self,
        log: CombatLogPanel,
        on_complete: Callable[[], None],
        on_forfeit: Callable[[], None],
    ) -> None:
        """Inject dependencies that aren't available at init time."""
        self._log = log
        self._on_complete = on_complete
        self._on_forfeit = on_forfeit

    def handle_key(self, key: int, has_blocking: bool) -> None:
        """Entry point: dispatches key to the right handler."""
        if self._handle_overlay_keys(key):
            return
        if has_blocking:
            return
        if self._handle_combat_over(key):
            return
        self._handle_gameplay_key(key)

    def _handle_overlay_keys(self, key: int) -> bool:
        """Handles help, pause, and QTE overlays."""
        if self._state.show_help:
            if key in (pygame.K_h, pygame.K_ESCAPE):
                self._state.show_help = False
            return True
        if self._state.show_pause:
            self._handle_pause_key(key)
            return True
        if key == pygame.K_h:
            self._state.show_help = True
            return True
        if self._state.qte_overlay is not None:
            self._state.qte_overlay.handle_key(key)
            return True
        return False

    def _handle_combat_over(self, key: int) -> bool:
        """Handles input when combat is finished."""
        if self._scene.phase != TurnPhase.COMBAT_OVER:
            return False
        confirm = (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE)
        if key in confirm and self._on_complete is not None:
            self._on_complete()
        return True

    def _handle_gameplay_key(self, key: int) -> None:
        """Handles normal gameplay keys."""
        if self._handle_escape(key):
            return
        if self._handle_shortcut_keys(key):
            return
        if self._handle_menu_nav(key):
            return
        if key == pygame.K_s:
            self._cycle_speed()
            return
        self._handle_selection_keys(key)

    def _handle_escape(self, key: int) -> bool:
        """Handles ESC and BACKSPACE."""
        if key == pygame.K_ESCAPE:
            menu = self._state.menu
            if menu is not None:
                if not menu.cancel():
                    self._state.show_pause = True
            return True
        if key == pygame.K_BACKSPACE:
            if self._state.menu is not None:
                self._state.menu.cancel()
            return True
        return False

    def _handle_shortcut_keys(self, key: int) -> bool:
        """Handles Tab/Space, PageUp/Down, and C shortcut."""
        if key in (pygame.K_TAB, pygame.K_SPACE):
            self._scene.shortcut_end_turn()
            return True
        if key == pygame.K_PAGEUP and self._log is not None:
            self._log.scroll_up()
            return True
        if key == pygame.K_PAGEDOWN and self._log is not None:
            self._log.scroll_down()
            return True
        if key == pygame.K_c and self._state.menu is not None:
            if self._state.menu.current_level == MenuLevel.ACTION_TYPE:
                self._state.menu.select(_ITEM_KEY)
            return True
        return False

    def _handle_selection_keys(self, key: int) -> None:
        """Handles Enter and number key selection."""
        menu = self._state.menu
        if key == pygame.K_RETURN and menu is not None:
            result = menu.select_highlighted()
            if result is not None:
                self._try_submit_action(result)
            return
        num = _KEY_MAP.get(key)
        if num is not None and menu is not None:
            result = menu.select(num)
            if result is not None:
                self._try_submit_action(result)

    def _handle_menu_nav(self, key: int) -> bool:
        """Processa W/S e UP/DOWN para navegacao de menu."""
        if self._state.menu is None:
            return False
        if key in _NAV_UP:
            self._state.menu.move_highlight(-1)
            return True
        if key in _NAV_DOWN:
            self._state.menu.move_highlight(1)
            return True
        return False

    def _handle_pause_key(self, key: int) -> None:
        """Processa input do menu de pausa."""
        result = handle_pause_input(key)
        if result == PauseMenuResult.RESUME:
            self._state.show_pause = False
        elif result == PauseMenuResult.HELP:
            self._state.show_pause = False
            self._state.show_help = True
        elif result == PauseMenuResult.FORFEIT:
            if self._on_forfeit is not None:
                self._on_forfeit()

    def _cycle_speed(self) -> None:
        """Cicla velocidade de animacao: 1x -> 2x -> 3x."""
        idx = next_speed_index(self._state.speed_index)
        self._state.speed_index = idx
        self._state.speed_mult = SPEED_OPTIONS[idx]

    def _try_submit_action(self, action: PlayerAction) -> None:
        """Submits action, or starts QTE if skill has one."""
        if action.action_type == PlayerActionType.SKILL:
            skill = _find_skill_for_action(self._scene, action)
            if skill is not None and skill.qte is not None:
                self._state.qte_overlay = QteOverlay(skill.qte)
                self._state.qte_pending_action = action
                return
        self._scene.submit_player_action(action)
        self._force_menu_rebuild()

    def _force_menu_rebuild(self) -> None:
        ctx = self._scene.current_context
        if self._scene.phase == TurnPhase.WAITING_INPUT and ctx:
            self._state.menu = ActionMenu(ctx)

    def update_qte(self, dt_ms: int) -> None:
        """Updates QTE overlay and submits result when done."""
        overlay = self._state.qte_overlay
        if overlay is None:
            return
        overlay.update(dt_ms)
        if not overlay.is_done:
            return
        from src.core.combat.action_resolver import set_qte_result
        set_qte_result(overlay.get_result())
        pending = self._state.qte_pending_action
        if pending is not None:
            self._scene.submit_player_action(pending)
            self._force_menu_rebuild()
        self._state.qte_overlay = None
        self._state.qte_pending_action = None


def _find_skill_for_action(
    scene: InteractiveCombatScene,
    action: PlayerAction,
):
    """Finds the Skill object for a skill action."""
    ctx = scene.current_context
    if ctx is None or action.skill_id is None:
        return None
    bar = ctx.combatant.skill_bar
    if bar is None:
        return None
    for s in bar.all_skills:
        if s.skill_id == action.skill_id:
            return s
    return None
