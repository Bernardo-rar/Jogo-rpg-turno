"""Cena de combate: replay visual da batalha."""

from __future__ import annotations

import pygame

from src.core.combat.combat_engine import CombatEvent, EventType
from src.core.combat.combat_log import CombatLog
from src.core.combat.log_formatter import LogFormatter
from src.ui import colors, layout
from src.ui.animations.animation_factory import AnimationFactory
from src.ui.animations.animation_manager import AnimationManager
from src.ui.components.battlefield import Battlefield
from src.ui.components.combat_log_panel import CombatLogPanel
from src.ui.font_manager import FontManager
from src.ui.replay.battle_snapshot import BattleReplay
from src.ui.replay.display_state import DisplayState

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
        self._display = DisplayState(replay.snapshots[0])
        self._battlefield = Battlefield(replay.snapshots[0])
        self._log_panel = CombatLogPanel()
        self._anim_manager = AnimationManager()
        self._anim_factory = AnimationFactory()
        self._effects_by_round = _group_effects_by_round(replay)
        self._all_names = [c.name for c in replay.snapshots[0].characters]
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
        self._anim_manager.update(dt_ms)
        if self._anim_manager.has_blocking:
            return self._running
        self._timer_ms += dt_ms
        if self._timer_ms >= layout.EVENT_DELAY_MS:
            self._timer_ms = 0
            self._advance_event()
        return self._running

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(colors.BG_DARK)
        self._draw_round_indicator(surface)
        offsets = _build_shake_offsets(self._anim_manager, self._all_names)
        self._battlefield.draw(surface, self._fonts, offsets=offsets)
        self._anim_manager.draw(surface)
        self._log_panel.draw(surface, self._fonts.medium)
        if self._finished:
            self._draw_result(surface)

    def _advance_event(self) -> None:
        if self._event_index >= len(self._replay.events):
            self._finished = True
            return
        event = self._replay.events[self._event_index]
        self._update_round(event.round_number)
        before = self._display.get_alive_map()
        self._apply_event_delta(event)
        after = self._display.get_alive_map()
        died = [n for n, alive in before.items() if alive and not after.get(n, True)]
        self._add_event_to_log(event)
        self._spawn_animations(event)
        _spawn_death_fades(died, self._battlefield, self._anim_manager)
        self._event_index += 1
        if self._event_index >= len(self._replay.events):
            self._finished = True
            self._load_final_snapshot()

    def _update_round(self, round_number: int) -> None:
        if round_number <= self._current_round:
            return
        self._current_round = round_number
        prev = _find_snapshot(self._replay, round_number - 1)
        if prev is not None:
            self._display.sync_from_snapshot(prev)
        ticks = self._effects_by_round.get(round_number, [])
        self._display.apply_effect_ticks(ticks)
        _spawn_tick_animations(ticks, self._battlefield, self._anim_manager)
        self._push_display()

    def _apply_event_delta(self, event: CombatEvent) -> None:
        applier = _EVENT_APPLIERS.get(event.event_type)
        if applier is not None:
            applier(self._display, event)
            self._push_display()

    def _push_display(self) -> None:
        snap = self._display.to_round_snapshot(self._current_round)
        self._battlefield.update(snap)

    def _load_final_snapshot(self) -> None:
        self._display.sync_from_snapshot(self._replay.snapshots[-1])
        self._push_display()

    def _spawn_animations(self, event: CombatEvent) -> None:
        rect = self._battlefield.get_card_rect(event.target_name)
        if rect is None:
            return
        animations = self._anim_factory.create(event, rect)
        for anim in animations:
            self._anim_manager.spawn(anim)

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
        rect = rendered.get_rect(
            center=(layout.WINDOW_WIDTH // 2, layout.BATTLEFIELD_HEIGHT // 2),
        )
        surface.blit(rendered, rect)


def _spawn_tick_animations(
    ticks: list,
    battlefield: Battlefield,
    anim_manager: AnimationManager,
) -> None:
    """Spawna animacoes para ticks de efeitos (DoTs, regens)."""
    from src.ui.animations.tick_animation_factory import create_tick_animations
    for entry in ticks:
        rect = battlefield.get_card_rect(entry.character_name)
        if rect is None:
            continue
        for anim in create_tick_animations(entry, rect):
            anim_manager.spawn(anim)


def _spawn_death_fades(
    died_names: list[str],
    battlefield: Battlefield,
    anim_manager: AnimationManager,
) -> None:
    """Spawna DeathFade para cada personagem que morreu."""
    from src.ui.animations.death_fade import DeathFade
    for name in died_names:
        rect = battlefield.get_card_rect(name)
        if rect is None:
            continue
        x, y, w, h = rect
        anim_manager.spawn(DeathFade(x=x, y=y, width=w, height=h))


def _build_shake_offsets(
    manager: AnimationManager, names: list[str],
) -> dict[str, tuple[int, int]]:
    """Coleta offsets de CardShake ativos para aplicar nos cards."""
    offsets: dict[str, tuple[int, int]] = {}
    for name in names:
        offset = manager.get_shake_offset(name)
        if offset != (0, 0):
            offsets[name] = offset
    return offsets


def _apply_damage(display: DisplayState, event: CombatEvent) -> None:
    amount = event.damage.final_damage if event.damage else event.value
    display.apply_damage(event.target_name, amount)


def _apply_heal(display: DisplayState, event: CombatEvent) -> None:
    display.apply_heal(event.target_name, event.value)


def _apply_mana(display: DisplayState, event: CombatEvent) -> None:
    display.apply_mana_restore(event.target_name, event.value)


def _apply_effect(display: DisplayState, event: CombatEvent) -> None:
    if event.description:
        display.apply_add_effect(event.target_name, event.description)


def _apply_cleanse(display: DisplayState, event: CombatEvent) -> None:
    display.apply_remove_effects(event.target_name)


_EVENT_APPLIERS: dict = {
    EventType.DAMAGE: _apply_damage,
    EventType.HEAL: _apply_heal,
    EventType.MANA_RESTORE: _apply_mana,
    EventType.AILMENT: _apply_effect,
    EventType.BUFF: _apply_effect,
    EventType.DEBUFF: _apply_effect,
    EventType.CLEANSE: _apply_cleanse,
}


def _group_effects_by_round(replay: BattleReplay) -> dict:
    """Agrupa EffectLogEntry por round_number."""
    groups: dict = {}
    for entry in replay.effect_log:
        groups.setdefault(entry.round_number, []).append(entry)
    return groups


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
