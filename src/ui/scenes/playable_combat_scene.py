"""PlayableCombatScene — adapta InteractiveCombatScene ao Scene protocol."""

from __future__ import annotations

import pygame

from src.core.combat.combat_engine import CombatEvent, EventType
from src.core.combat.player_action import PlayerAction, PlayerActionType
from src.ui import colors, layout
from src.ui.components.action_economy_bar import draw_economy_bar
from src.ui.components.action_panel import draw_action_panel
from src.ui.components.battlefield import Battlefield
from src.ui.components.combat_log_panel import CombatLogPanel
from src.ui.components.turn_indicator import draw_turn_indicator
from src.ui.font_manager import FontManager
from src.ui.input.action_menu import ActionMenu
from src.ui.replay.live_display import create_live_snapshot
from src.ui.scenes.interactive_combat import InteractiveCombatScene, TurnPhase

_KEY_MAP = {
    pygame.K_1: 1, pygame.K_2: 2, pygame.K_3: 3,
    pygame.K_4: 4, pygame.K_5: 5, pygame.K_6: 6,
    pygame.K_7: 7, pygame.K_8: 8, pygame.K_9: 9,
}

_LOG_COMPACT_VISIBLE = 4

_EVENT_COLORS: dict[EventType, tuple] = {
    EventType.DAMAGE: colors.TEXT_DAMAGE,
    EventType.HEAL: colors.TEXT_HEAL,
    EventType.BUFF: colors.EFFECT_BUFF,
    EventType.DEBUFF: colors.EFFECT_DEBUFF,
    EventType.AILMENT: colors.TEXT_EFFECT,
    EventType.CLEANSE: colors.TEXT_HEAL,
    EventType.MANA_RESTORE: colors.MANA_BLUE,
}


class PlayableCombatScene:
    """Cena visual jogavel: renderiza battlefield + menu + input."""

    def __init__(
        self,
        scene: InteractiveCombatScene,
        party: list,
        enemies: list,
        fonts: FontManager,
    ) -> None:
        self._scene = scene
        self._party = party
        self._enemies = enemies
        self._fonts = fonts
        self._log = CombatLogPanel(max_visible=_LOG_COMPACT_VISIBLE)
        self._menu: ActionMenu | None = None
        self._menu_combatant: str | None = None
        self._running = True
        self._event_index = 0
        snap = create_live_snapshot(party, enemies, 0)
        self._battlefield = Battlefield(snap)
        self._elapsed_ms = 0

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            self._handle_key(event.key)

    def update(self, dt_ms: int) -> bool:
        if not self._running:
            return False
        self._elapsed_ms += dt_ms
        self._scene.update(dt_ms)
        self._refresh_battlefield()
        self._refresh_menu()
        self._flush_new_events()
        return self._running

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(colors.BG_DARK)
        self._draw_round(surface)
        self._battlefield.draw(surface, self._fonts)
        self._draw_turn_highlight(surface)
        self._log.draw(surface, self._fonts.small)
        if self._scene.phase == TurnPhase.WAITING_INPUT:
            self._draw_interactive_ui(surface)
        if self._scene.phase == TurnPhase.COMBAT_OVER:
            self._draw_result(surface)

    def _handle_key(self, key: int) -> None:
        if key == pygame.K_ESCAPE:
            if self._scene.phase == TurnPhase.COMBAT_OVER:
                self._running = False
                return
            if self._menu is not None:
                self._menu.cancel()
            return
        if key in (pygame.K_TAB, pygame.K_SPACE):
            self._scene.shortcut_end_turn()
            return
        num = _KEY_MAP.get(key)
        if num is not None and self._menu is not None:
            result = self._menu.select(num)
            if result is not None:
                self._scene.submit_player_action(result)
                self._force_menu_rebuild()

    def _refresh_battlefield(self) -> None:
        rnd = max(1, self._scene._engine.round_number)
        snap = create_live_snapshot(self._party, self._enemies, rnd)
        self._battlefield.update(snap)

    def _force_menu_rebuild(self) -> None:
        ctx = self._scene.current_context
        if self._scene.phase == TurnPhase.WAITING_INPUT and ctx:
            self._menu = ActionMenu(ctx)

    def _refresh_menu(self) -> None:
        phase = self._scene.phase
        ctx = self._scene.current_context
        active = self._scene.active_combatant
        if phase == TurnPhase.WAITING_INPUT and ctx:
            if active != self._menu_combatant:
                self._menu = ActionMenu(ctx)
                self._menu_combatant = active
        else:
            self._menu = None
            self._menu_combatant = None

    def _flush_new_events(self) -> None:
        """Loga eventos novos do engine no combat log."""
        all_events = self._scene._engine.events
        while self._event_index < len(all_events):
            event = all_events[self._event_index]
            self._log_event(event)
            self._event_index += 1

    def _log_event(self, event: CombatEvent) -> None:
        text = _format_event(event)
        color = _EVENT_COLORS.get(event.event_type, colors.TEXT_WHITE)
        self._log.add_line(text, color)

    def _draw_interactive_ui(self, surface: pygame.Surface) -> None:
        if self._menu is not None:
            draw_action_panel(
                surface, self._menu.options,
                self._menu.current_level, self._fonts.medium,
            )
        ctx = self._scene.current_context
        if ctx is not None:
            draw_economy_bar(surface, ctx.action_economy, self._fonts.small)

    def _draw_turn_highlight(self, surface: pygame.Surface) -> None:
        name = self._scene.active_combatant
        if name is None:
            return
        rect = self._battlefield.get_card_rect(name)
        if rect is not None:
            draw_turn_indicator(surface, rect, self._elapsed_ms)

    def _draw_round(self, surface: pygame.Surface) -> None:
        rnd = self._scene._engine.round_number
        text = f"Round {rnd}"
        rendered = self._fonts.large.render(text, True, colors.TEXT_YELLOW)
        surface.blit(
            rendered,
            (layout.ROUND_INDICATOR_X, layout.ROUND_INDICATOR_Y),
        )

    def _draw_result(self, surface: pygame.Surface) -> None:
        result = self._scene._engine.result
        if result is None:
            return
        text = result.name.replace("_", " ")
        rendered = self._fonts.large.render(text, True, colors.TEXT_YELLOW)
        rect = rendered.get_rect(
            center=(layout.WINDOW_WIDTH // 2, layout.BATTLEFIELD_HEIGHT // 2),
        )
        surface.blit(rendered, rect)


def _format_event(event: CombatEvent) -> str:
    """Formata CombatEvent como texto legivel para o log."""
    if event.event_type == EventType.DAMAGE and event.damage:
        dmg = event.damage.final_damage
        crit = " CRIT!" if event.damage.is_critical else ""
        return f"{event.actor_name} hits {event.target_name} for {dmg}{crit}"
    if event.event_type == EventType.HEAL:
        return f"{event.actor_name} heals {event.target_name} for {event.value}"
    if event.event_type == EventType.BUFF:
        return f"{event.actor_name} buffs {event.target_name}: {event.description}"
    if event.event_type == EventType.DEBUFF:
        return f"{event.actor_name} debuffs {event.target_name}: {event.description}"
    if event.event_type == EventType.AILMENT:
        return f"{event.target_name} afflicted: {event.description}"
    if event.event_type == EventType.MANA_RESTORE:
        return f"{event.target_name} restores {event.value} mana"
    return f"{event.actor_name} -> {event.target_name}: {event.description}"
