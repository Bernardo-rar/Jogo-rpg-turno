"""Cena de combate: replay visual da batalha."""

from __future__ import annotations

import pygame

from src.core.combat.combat_engine import CombatEvent, EventType
from src.core.combat.combat_log import CombatLog
from src.core.combat.log_formatter import LogFormatter
from src.ui import colors, layout
from src.ui.components.battlefield import Battlefield
from src.ui.components.combat_log_panel import CombatLogPanel
from src.ui.font_manager import FontManager
from src.ui.replay.battle_snapshot import BattleReplay

_EVENT_COLORS: dict[EventType, tuple] = {
    EventType.DAMAGE: colors.TEXT_DAMAGE,
    EventType.HEAL: colors.TEXT_HEAL,
    EventType.BUFF: colors.EFFECT_BUFF,
    EventType.DEBUFF: colors.EFFECT_DEBUFF,
    EventType.AILMENT: colors.TEXT_EFFECT,
    EventType.CLEANSE: colors.TEXT_HEAL,
    EventType.MANA_RESTORE: colors.MANA_BLUE,
}


class CombatScene:
    """Replay visual de uma batalha gravada."""

    def __init__(self, replay: BattleReplay, fonts: FontManager) -> None:
        self._replay = replay
        self._fonts = fonts
        self._battlefield = Battlefield(replay.snapshots[0])
        self._log_panel = CombatLogPanel()
        self._event_index = 0
        self._current_round = 0
        self._timer_ms = 0
        self._finished = False
        self._running = True
        self._log_cache = _build_log_cache(replay)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._running = False

    def update(self, dt_ms: int) -> bool:
        if self._finished or not self._running:
            return self._running
        self._timer_ms += dt_ms
        if self._timer_ms >= layout.EVENT_DELAY_MS:
            self._timer_ms = 0
            self._advance_event()
        return self._running

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(colors.BG_DARK)
        self._draw_round_indicator(surface)
        self._battlefield.draw(surface, self._fonts)
        self._log_panel.draw(surface, self._fonts.medium)
        if self._finished:
            self._draw_result(surface)

    def _advance_event(self) -> None:
        if self._event_index >= len(self._replay.events):
            self._finished = True
            return
        event = self._replay.events[self._event_index]
        self._update_round(event.round_number)
        self._add_event_to_log(event)
        self._event_index += 1
        if self._event_index >= len(self._replay.events):
            self._finished = True

    def _update_round(self, round_number: int) -> None:
        if round_number <= self._current_round:
            return
        self._current_round = round_number
        snap = _find_snapshot(self._replay, round_number)
        if snap is not None:
            self._battlefield.update(snap)

    def _add_event_to_log(self, event: CombatEvent) -> None:
        text = self._log_cache.get(self._event_index, "")
        color = _EVENT_COLORS.get(event.event_type, colors.TEXT_WHITE)
        self._log_panel.add_line(text, color)

    def _draw_round_indicator(self, surface: pygame.Surface) -> None:
        text = f"Round {self._current_round}"
        rendered = self._fonts.large.render(text, True, colors.TEXT_YELLOW)
        surface.blit(rendered, (layout.ROUND_INDICATOR_X, layout.ROUND_INDICATOR_Y))

    def _draw_result(self, surface: pygame.Surface) -> None:
        text = self._replay.result.name.replace("_", " ")
        rendered = self._fonts.large.render(text, True, colors.TEXT_YELLOW)
        rect = rendered.get_rect(center=(layout.WINDOW_WIDTH // 2, layout.BATTLEFIELD_HEIGHT // 2))
        surface.blit(rendered, rect)


def _build_log_cache(replay: BattleReplay) -> dict[int, str]:
    """Pre-formata texto de cada evento via CombatLog + LogFormatter."""
    cache: dict[int, str] = {}
    log = CombatLog()
    for i, event in enumerate(replay.events):
        log_before = len(log.entries)
        log.add_from_combat_event(event)
        if len(log.entries) > log_before:
            entry = log.entries[-1]
            cache[i] = LogFormatter.format_entry(entry)
    return cache


def _find_snapshot(replay: BattleReplay, round_number: int):
    """Retorna snapshot do round, ou None se nao encontrar."""
    for snap in replay.snapshots:
        if snap.round_number == round_number:
            return snap
    return None
