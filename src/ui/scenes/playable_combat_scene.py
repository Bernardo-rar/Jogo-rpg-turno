"""PlayableCombatScene — adapta InteractiveCombatScene ao Scene protocol."""

from __future__ import annotations

from dataclasses import dataclass

import pygame

from src.core.combat.combat_engine import CombatEvent, EventType
from src.ui import colors
from src.ui.animations.animation_factory import AnimationFactory
from src.ui.animations.animation_manager import AnimationManager
from src.ui.animations.combat_intro import CombatIntroAnimation
from src.ui.animations.defeat_overlay import DefeatOverlay
from src.ui.animations.victory_overlay import VictoryOverlay
from src.ui.components.battlefield import Battlefield
from src.ui.components.combat_log_panel import CombatLogPanel, LogEntry
from src.ui.components.turn_timeline import TurnTimeline
from src.ui.font_manager import FontManager
from src.ui.input.action_menu import ActionMenu
from src.ui.replay.live_display import create_live_snapshot
from src.ui.scenes.combat_input_handler import CombatInputHandler, InputState
from src.ui.scenes.combat_renderer import CombatRenderer
from src.ui.scenes.interactive_combat import InteractiveCombatScene, TurnPhase

_LOG_COMPACT_VISIBLE = 4

_EVENT_COLORS: dict[EventType, tuple] = {
    EventType.DAMAGE: colors.TEXT_DAMAGE,
    EventType.HEAL: colors.TEXT_HEAL,
    EventType.BUFF: colors.EFFECT_BUFF,
    EventType.DEBUFF: colors.EFFECT_DEBUFF,
    EventType.AILMENT: colors.TEXT_EFFECT,
    EventType.CLEANSE: colors.TEXT_HEAL,
    EventType.MANA_RESTORE: colors.MANA_BLUE,
    EventType.SUMMON: colors.TEXT_YELLOW,
    EventType.FIELD_EFFECT: colors.TEXT_EFFECT,
    EventType.CHARGE: colors.TEXT_YELLOW,
    EventType.TRANSFORM: colors.TEXT_YELLOW,
    EventType.EMPOWER: colors.TEXT_DAMAGE,
}


@dataclass
class _SceneState:
    """Mutable state for update-cycle bookkeeping."""

    event_index: int = 0
    result_overlay_spawned: bool = False
    prev_alive: dict[str, bool] | None = None


class PlayableCombatScene:
    """Cena visual jogavel: renderiza battlefield + menu + input."""

    def __init__(
        self,
        scene: InteractiveCombatScene,
        party: list,
        enemies: list,
        fonts: FontManager,
        on_complete: object | None = None,
    ) -> None:
        self._scene = scene
        self._party = party
        self._enemies = enemies
        self._on_complete = on_complete
        self._running = True
        self._input_state = InputState()
        self._state = _SceneState()
        vis = _build_visuals(party, enemies, scene)
        self._log = vis.log
        self._anim_mgr = vis.anim_manager
        self._anim_fac = vis.anim_factory
        self._bf = vis.battlefield
        self._timeline = vis.timeline
        self._intro = vis.intro
        self._all_names = vis.all_names
        self._state.prev_alive = vis.prev_alive
        _wire_subsystems(self, scene, fonts)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            self._input_handler.handle_key(
                event.key, self._anim_mgr.has_blocking,
            )

    def update(self, dt_ms: int) -> bool:
        if not self._running:
            return False
        scaled = int(dt_ms * self._input_state.speed_mult)
        self._renderer._elapsed_ms += scaled
        self._input_handler.update_qte(scaled)
        self._anim_mgr.update(scaled)
        if self._anim_mgr.has_blocking:
            return self._running
        self._scene.update(scaled)
        _refresh_battlefield(self)
        _refresh_menu(self._scene, self._input_state)
        _flush_new_events(self)
        _maybe_spawn_result_overlay(self)
        return self._running

    def draw(self, surface: pygame.Surface) -> None:
        self._renderer.draw(surface)

    def set_synergy_names(self, names: list[str]) -> None:
        """Set which enemy names are in a synergy group."""
        self._renderer._synergy_names = names

    def _signal_complete(self) -> None:
        """Sinaliza fim do combate via callback."""
        if self._on_complete is not None:
            self._on_complete(_build_result(self))
        else:
            self._running = False

    def _signal_forfeit(self) -> None:
        """Sinaliza derrota por desistencia."""
        if self._on_complete is not None:
            self._on_complete({"victory": False})
        else:
            self._running = False


# --- Factory helpers (called once at init) ---


@dataclass
class _Visuals:
    """Bundle of visual components created at init."""

    log: CombatLogPanel
    anim_manager: AnimationManager
    anim_factory: AnimationFactory
    battlefield: Battlefield
    timeline: TurnTimeline
    intro: CombatIntroAnimation
    all_names: list[str]
    prev_alive: dict[str, bool]


def _build_visuals(
    party: list, enemies: list, scene: InteractiveCombatScene,
) -> _Visuals:
    """Creates all visual components for the scene."""
    all_chars = party + enemies
    all_names = [c.name for c in all_chars]
    snap = create_live_snapshot(party, enemies, 0)
    anim_mgr = AnimationManager()
    intro = CombatIntroAnimation(
        party_names=[c.name for c in party],
        enemy_names=[c.name for c in enemies],
    )
    anim_mgr.spawn(intro)
    return _Visuals(
        log=CombatLogPanel(max_visible=_LOG_COMPACT_VISIBLE),
        anim_manager=anim_mgr,
        anim_factory=AnimationFactory(),
        battlefield=Battlefield(snap),
        timeline=TurnTimeline(
            turn_order=all_names,
            party_names=scene.party_names,
        ),
        intro=intro,
        all_names=all_names,
        prev_alive={c.name: c.is_alive for c in all_chars},
    )


def _wire_subsystems(
    self: PlayableCombatScene,
    scene: InteractiveCombatScene,
    fonts: FontManager,
) -> None:
    """Wires input handler and renderer onto the scene."""
    handler = CombatInputHandler(scene, self._input_state)
    handler.set_callbacks(
        log=self._log,
        on_complete=self._signal_complete,
        on_forfeit=self._signal_forfeit,
    )
    self._input_handler = handler
    renderer = CombatRenderer(scene, self._input_state)
    renderer.set_dependencies(self._bf, self._log, fonts)
    renderer.set_animation_deps(
        self._anim_mgr, self._timeline, self._intro,
    )
    renderer.set_entity_data(self._all_names, self._enemies)
    self._renderer = renderer


# --- Update-cycle helpers ---


def _build_result(self: PlayableCombatScene) -> dict:
    """Builds the combat result dict for the callback."""
    from src.core.combat.combat_engine import CombatResult
    result = self._scene.result
    deaths = sum(1 for c in self._party if not c.is_alive)
    return {
        "victory": result == CombatResult.PARTY_VICTORY,
        "rounds": self._scene.round_number,
        "deaths": deaths,
    }


def _refresh_battlefield(self: PlayableCombatScene) -> None:
    rnd = max(1, self._scene.round_number)
    snap = create_live_snapshot(
        self._party, self._enemies, rnd,
    )
    self._bf.update(snap)
    dead = {
        n for n, alive in self._state.prev_alive.items()
        if not alive
    }
    self._timeline.update(
        turn_order=self._scene.turn_order_names,
        active=self._scene.active_combatant,
        dead=dead,
    )


def _refresh_menu(
    scene: InteractiveCombatScene, state: InputState,
) -> None:
    phase = scene.phase
    ctx = scene.current_context
    active = scene.active_combatant
    if phase == TurnPhase.WAITING_INPUT and ctx:
        if active != state.menu_combatant:
            state.menu = ActionMenu(ctx)
            state.menu_combatant = active
    else:
        state.menu = None
        state.menu_combatant = None


def _flush_new_events(self: PlayableCombatScene) -> None:
    """Loga eventos novos e spawna animacoes."""
    all_events = self._scene.events
    while self._state.event_index < len(all_events):
        event = all_events[self._state.event_index]
        _log_event(self._log, event)
        _spawn_event_animations(
            event, self._bf, self._anim_mgr, self._anim_fac,
        )
        self._state.event_index += 1
    _detect_deaths(self)


def _detect_deaths(self: PlayableCombatScene) -> None:
    """Detecta mortes e spawna DeathFade."""
    current = {
        c.name: c.is_alive
        for c in self._party + self._enemies
    }
    died = [
        n for n, alive in self._state.prev_alive.items()
        if alive and not current.get(n, True)
    ]
    if died:
        _spawn_death_fades(died, self._bf, self._anim_mgr)
    self._state.prev_alive = current


def _log_event(log: CombatLogPanel, event: CombatEvent) -> None:
    tag, msg = _format_event_tagged(event)
    color = _EVENT_COLORS.get(event.event_type, colors.TEXT_WHITE)
    log.add_entry(LogEntry(tag=tag, tag_color=color, message=msg))


def _maybe_spawn_result_overlay(
    self: PlayableCombatScene,
) -> None:
    """Spawns victory/defeat overlay when combat ends."""
    if self._state.result_overlay_spawned:
        return
    if self._scene.phase != TurnPhase.COMBAT_OVER:
        return
    self._state.result_overlay_spawned = True
    _spawn_result_overlay(self._scene, self._anim_mgr)


def _spawn_result_overlay(
    scene: InteractiveCombatScene,
    anim_manager: AnimationManager,
) -> None:
    """Spawns the appropriate result overlay animation."""
    from src.core.combat.combat_engine import CombatResult
    from src.ui import layout
    w, h = layout.WINDOW_WIDTH, layout.WINDOW_HEIGHT
    if scene.result == CombatResult.PARTY_VICTORY:
        anim_manager.spawn(VictoryOverlay(w, h))
    elif scene.result == CombatResult.PARTY_DEFEAT:
        anim_manager.spawn(DefeatOverlay(w, h))


def _spawn_event_animations(
    event: CombatEvent,
    battlefield: Battlefield,
    anim_manager: AnimationManager,
    anim_factory: AnimationFactory,
) -> None:
    """Spawna animacoes para um evento de combate."""
    rect = battlefield.get_card_rect(event.target_name)
    if rect is None:
        return
    for anim in anim_factory.create(event, rect):
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


# --- Event formatting (dispatch table) ---


def _format_event_tagged(event: CombatEvent) -> tuple[str, str]:
    """Returns (tag, message) for a CombatEvent."""
    if event.event_type == EventType.DAMAGE and event.damage:
        return _format_damage_event(event)
    formatter = _EVENT_FORMATTERS.get(event.event_type)
    if formatter is not None:
        return formatter(event)
    return _format_generic_event(event)


def _format_damage_event(event: CombatEvent) -> tuple[str, str]:
    dmg = event.damage.final_damage
    is_crit = event.damage.is_critical
    tag = "[CRIT]" if is_crit else "[ATK]"
    crit = " CRIT!" if is_crit else ""
    msg = f"{event.actor_name} hits {event.target_name} for {dmg}{crit}"
    return tag, msg


def _fmt_heal(e: CombatEvent) -> tuple[str, str]:
    return "[HEAL]", f"{e.actor_name} heals {e.target_name} for {e.value}"


def _fmt_buff(e: CombatEvent) -> tuple[str, str]:
    return "[BUFF]", f"{e.actor_name} buffs {e.target_name}: {e.description}"


def _fmt_debuff(e: CombatEvent) -> tuple[str, str]:
    return "[DBF]", f"{e.actor_name} debuffs {e.target_name}: {e.description}"


def _fmt_ailment(e: CombatEvent) -> tuple[str, str]:
    return "[DOT]", f"{e.target_name} afflicted: {e.description}"


def _fmt_mana(e: CombatEvent) -> tuple[str, str]:
    return "[MP]", f"{e.target_name} restores {e.value} mana"


def _fmt_charge(e: CombatEvent) -> tuple[str, str]:
    return "[CHG]", f"{e.actor_name}: {e.description}"


def _fmt_summon(e: CombatEvent) -> tuple[str, str]:
    return "[SUM]", f"{e.description}"


def _fmt_transform(e: CombatEvent) -> tuple[str, str]:
    return "[TFM]", f"{e.description}"


def _fmt_empower(e: CombatEvent) -> tuple[str, str]:
    return "[EMP]", f"{e.description}"


def _fmt_field(e: CombatEvent) -> tuple[str, str]:
    return "[FLD]", f"{e.description}: {e.value} dmg to {e.target_name}"


def _format_generic_event(event: CombatEvent) -> tuple[str, str]:
    return "", f"{event.actor_name} -> {event.target_name}: {event.description}"


_EVENT_FORMATTERS = {
    EventType.HEAL: _fmt_heal,
    EventType.BUFF: _fmt_buff,
    EventType.DEBUFF: _fmt_debuff,
    EventType.AILMENT: _fmt_ailment,
    EventType.MANA_RESTORE: _fmt_mana,
    EventType.CHARGE: _fmt_charge,
    EventType.SUMMON: _fmt_summon,
    EventType.TRANSFORM: _fmt_transform,
    EventType.EMPOWER: _fmt_empower,
    EventType.FIELD_EFFECT: _fmt_field,
}
