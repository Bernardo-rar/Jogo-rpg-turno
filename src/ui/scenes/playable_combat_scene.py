"""PlayableCombatScene — adapta InteractiveCombatScene ao Scene protocol."""

from __future__ import annotations

import pygame

from src.core.combat.combat_engine import CombatEvent, EventType
from src.core.combat.player_action import PlayerAction, PlayerActionType
from src.ui import colors, layout
from src.ui.animations.animation_factory import AnimationFactory
from src.ui.animations.animation_manager import AnimationManager
from src.ui.components.action_economy_bar import draw_economy_bar
from src.ui.components.action_panel import draw_action_panel
from src.ui.components.help_hint import draw_help_hint
from src.ui.components.help_overlay import draw_help_overlay
from src.ui.components.pause_menu import (
    PauseMenuResult,
    draw_pause_menu,
    handle_pause_input,
)
from src.ui.components.battlefield import Battlefield
from src.ui.components.combat_log_panel import CombatLogPanel
from src.ui.components.damage_tooltip import (
    draw_attack_preview,
    draw_heal_preview,
    draw_skill_damage_preview,
)
from src.ui.components.skill_tooltip import draw_skill_tooltip
from src.ui.components.speed_indicator import (
    SPEED_OPTIONS,
    draw_speed_indicator,
    next_speed_index,
)
from src.ui.components.turn_indicator import draw_turn_indicator
from src.ui.components.turn_timeline import TurnTimeline
from src.ui.font_manager import FontManager
from src.ui.input.action_menu import ActionMenu
from src.ui.input.menu_state import MenuLevel
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
        on_complete: object | None = None,
    ) -> None:
        self._scene = scene
        self._party = party
        self._enemies = enemies
        self._fonts = fonts
        self._on_complete = on_complete
        self._log = CombatLogPanel(max_visible=_LOG_COMPACT_VISIBLE)
        self._anim_manager = AnimationManager()
        self._anim_factory = AnimationFactory()
        self._menu: ActionMenu | None = None
        self._menu_combatant: str | None = None
        self._running = True
        self._event_index = 0
        snap = create_live_snapshot(party, enemies, 0)
        self._battlefield = Battlefield(snap)
        self._all_names = [c.name for c in party] + [c.name for c in enemies]
        self._prev_alive = {c.name: c.is_alive for c in party + enemies}
        self._speed_index: int = 0
        self._speed_mult: float = SPEED_OPTIONS[0]
        self._elapsed_ms = 0
        self._show_help: bool = False
        self._show_pause: bool = False
        self._timeline = TurnTimeline(
            turn_order=[c.name for c in party + enemies],
            party_names=scene.party_names,
        )

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            self._handle_key(event.key)

    def update(self, dt_ms: int) -> bool:
        if not self._running:
            return False
        scaled_dt = int(dt_ms * self._speed_mult)
        self._elapsed_ms += scaled_dt
        self._anim_manager.update(scaled_dt)
        if self._anim_manager.has_blocking:
            return self._running
        self._scene.update(scaled_dt)
        self._refresh_battlefield()
        self._refresh_menu()
        self._flush_new_events()
        return self._running

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(colors.BG_DARK)
        self._timeline.draw(surface, self._fonts, self._scene.round_number)
        draw_speed_indicator(surface, self._speed_mult, self._fonts)
        offsets = _build_shake_offsets(self._anim_manager, self._all_names)
        self._battlefield.draw(surface, self._fonts, offsets=offsets)
        self._anim_manager.draw(surface)
        self._draw_turn_highlight(surface)
        self._log.draw(surface, self._fonts.small)
        if self._scene.phase == TurnPhase.WAITING_INPUT:
            self._draw_interactive_ui(surface)
        if self._scene.phase == TurnPhase.COMBAT_OVER:
            self._draw_result(surface)
        draw_help_hint(surface, self._fonts)
        if self._show_help:
            draw_help_overlay(surface, self._fonts)
        elif self._show_pause:
            draw_pause_menu(surface, self._fonts)

    def _handle_key(self, key: int) -> None:
        if self._show_help:
            if key in (pygame.K_h, pygame.K_ESCAPE):
                self._show_help = False
            return
        if self._show_pause:
            self._handle_pause_key(key)
            return
        if key == pygame.K_s:
            self._cycle_speed()
            return
        if key == pygame.K_h:
            self._show_help = True
            return
        if self._anim_manager.has_blocking:
            return
        if self._scene.phase == TurnPhase.COMBAT_OVER:
            if key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                self._signal_complete()
            return
        if key == pygame.K_ESCAPE:
            if self._menu is not None:
                if not self._menu.cancel():
                    self._show_pause = True
            return
        if key == pygame.K_BACKSPACE:
            if self._menu is not None:
                self._menu.cancel()
            return
        if key in (pygame.K_TAB, pygame.K_SPACE):
            self._scene.shortcut_end_turn()
            return
        if key in (pygame.K_UP, pygame.K_DOWN) and self._menu is not None:
            delta = -1 if key == pygame.K_UP else 1
            self._menu.move_highlight(delta)
            return
        num = _KEY_MAP.get(key)
        if num is not None and self._menu is not None:
            result = self._menu.select(num)
            if result is not None:
                self._scene.submit_player_action(result)
                self._force_menu_rebuild()

    def _cycle_speed(self) -> None:
        """Cicla velocidade de animacao: 1x -> 2x -> 3x -> 1x."""
        self._speed_index = next_speed_index(self._speed_index)
        self._speed_mult = SPEED_OPTIONS[self._speed_index]

    def _signal_complete(self) -> None:
        """Sinaliza fim do combate via callback ou fecha a cena."""
        if self._on_complete is not None:
            from src.core.combat.combat_engine import CombatResult
            result = self._scene.result
            self._on_complete({
                "victory": result == CombatResult.PARTY_VICTORY,
            })
        else:
            self._running = False

    def _handle_pause_key(self, key: int) -> None:
        """Processa input do menu de pausa."""
        result = handle_pause_input(key)
        if result == PauseMenuResult.RESUME:
            self._show_pause = False
        elif result == PauseMenuResult.HELP:
            self._show_pause = False
            self._show_help = True
        elif result == PauseMenuResult.FORFEIT:
            self._signal_forfeit()

    def _signal_forfeit(self) -> None:
        """Sinaliza derrota por desistencia."""
        if self._on_complete is not None:
            self._on_complete({"victory": False})
        else:
            self._running = False

    def _refresh_battlefield(self) -> None:
        rnd = max(1, self._scene.round_number)
        snap = create_live_snapshot(self._party, self._enemies, rnd)
        self._battlefield.update(snap)
        dead = {n for n, alive in self._prev_alive.items() if not alive}
        self._timeline.update(
            turn_order=self._scene.turn_order_names,
            active=self._scene.active_combatant,
            dead=dead,
        )

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
        """Loga eventos novos e spawna animacoes."""
        all_events = self._scene.events
        while self._event_index < len(all_events):
            event = all_events[self._event_index]
            self._log_event(event)
            _spawn_event_animations(
                event, self._battlefield, self._anim_manager, self._anim_factory,
            )
            self._event_index += 1
        self._detect_deaths()

    def _detect_deaths(self) -> None:
        """Detecta mortes e spawna DeathFade."""
        current = {c.name: c.is_alive for c in self._party + self._enemies}
        died = [n for n, alive in self._prev_alive.items() if alive and not current.get(n, True)]
        if died:
            _spawn_death_fades(died, self._battlefield, self._anim_manager)
        self._prev_alive = current

    def _log_event(self, event: CombatEvent) -> None:
        text = _format_event(event)
        color = _EVENT_COLORS.get(event.event_type, colors.TEXT_WHITE)
        self._log.add_line(text, color)

    def _draw_interactive_ui(self, surface: pygame.Surface) -> None:
        if self._menu is not None:
            name = self._scene.active_combatant or ""
            level = self._menu.current_level
            can_back = level != MenuLevel.ACTION_TYPE
            draw_action_panel(
                surface, self._menu.options,
                level, self._fonts.medium,
                combatant_name=name,
                breadcrumb=self._menu.breadcrumb,
                can_go_back=can_back,
            )
            self._draw_skill_tooltip(surface)
            self._draw_damage_preview(surface)
        ctx = self._scene.current_context
        if ctx is not None:
            draw_economy_bar(surface, ctx.action_economy, self._fonts.small)

    def _draw_skill_tooltip(self, surface: pygame.Surface) -> None:
        """Desenha tooltip de skill quando no nivel SPECIFIC_ACTION."""
        if self._menu is None:
            return
        skill = self._menu.highlighted_skill
        if skill is None:
            return
        ctx = self._scene.current_context
        if ctx is None:
            return
        draw_skill_tooltip(
            surface, skill, ctx.combatant, self._fonts.small,
        )

    def _draw_turn_highlight(self, surface: pygame.Surface) -> None:
        name = self._scene.active_combatant
        if name is None:
            return
        rect = self._battlefield.get_card_rect(name)
        if rect is not None:
            draw_turn_indicator(surface, rect, self._elapsed_ms)

    def _draw_damage_preview(self, surface: pygame.Surface) -> None:
        """Desenha tooltip de preview quando no nivel de selecao de alvo."""
        if self._menu is None:
            return
        from src.ui.input.menu_state import MenuLevel
        if self._menu.current_level != MenuLevel.TARGET_SELECT:
            return
        target = self._find_first_target()
        if target is None:
            return
        card_rect = self._battlefield.get_card_rect(target.name)
        if card_rect is None:
            return
        combatant = self._scene.current_context.combatant
        pending_type = self._menu.pending_action_type
        pending_skill = self._menu.pending_skill
        _render_preview(
            surface, combatant, target,
            pending_type, pending_skill,
            card_rect, self._fonts.small,
        )

    def _find_first_target(self) -> object | None:
        """Encontra o primeiro alvo vivo listado no menu."""
        if self._menu is None:
            return None
        from src.core.combat.player_action import PlayerActionType
        pending = self._menu.pending_action_type
        ctx = self._scene.current_context
        if ctx is None:
            return None
        if pending == PlayerActionType.BASIC_ATTACK:
            pool = ctx.enemies
        elif self._menu.pending_skill is not None:
            from src.core.skills.target_type import TargetType
            if self._menu.pending_skill.target_type == TargetType.SINGLE_ALLY:
                pool = ctx.allies
            else:
                pool = ctx.enemies
        else:
            pool = ctx.enemies
        alive = [c for c in pool if c.is_alive]
        return alive[0] if alive else None

    def _draw_result(self, surface: pygame.Surface) -> None:
        result = self._scene.result
        if result is None:
            return
        text = result.name.replace("_", " ")
        rendered = self._fonts.large.render(text, True, colors.TEXT_YELLOW)
        cx = layout.WINDOW_WIDTH // 2
        cy = layout.BATTLEFIELD_HEIGHT // 2
        rect = rendered.get_rect(center=(cx, cy))
        surface.blit(rendered, rect)
        hint = self._fonts.small.render(
            "[ENTER] Continuar", True, colors.TEXT_MUTED,
        )
        surface.blit(hint, hint.get_rect(center=(cx, cy + 40)))


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


def _render_preview(
    surface: pygame.Surface,
    combatant: object,
    target: object,
    pending_type: object | None,
    pending_skill: object | None,
    card_rect: tuple[int, int, int, int],
    font: pygame.font.Font,
) -> None:
    """Renderiza tooltip de preview baseado no tipo de ação pendente."""
    from src.core.combat.damage_preview import (
        preview_basic_attack,
        preview_heal,
        preview_skill_damage,
    )
    from src.core.combat.player_action import PlayerActionType

    if pending_type == PlayerActionType.BASIC_ATTACK:
        preview = preview_basic_attack(combatant, target)
        draw_attack_preview(surface, preview, card_rect, font)
        return

    if pending_skill is not None:
        heal_prev = preview_heal(pending_skill, combatant, target)
        if heal_prev is not None:
            draw_heal_preview(surface, heal_prev, card_rect, font)
            return
        dmg_prev = preview_skill_damage(pending_skill, combatant, target)
        if dmg_prev is not None:
            draw_skill_damage_preview(surface, dmg_prev, card_rect, font)


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
