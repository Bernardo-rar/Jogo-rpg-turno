"""CombatRenderer — rendering logic for PlayableCombatScene."""

from __future__ import annotations

from dataclasses import dataclass

import pygame

from src.ui import colors, layout
from src.ui.animations.animation_manager import AnimationManager
from src.ui.components.action_economy_bar import draw_economy_bar
from src.ui.components.action_panel import ActionPanelState, draw_action_panel
from src.ui.components.battlefield import Battlefield
from src.ui.components.boss_indicators import (
    draw_charge_indicator,
    draw_empower_bar,
    draw_field_overlay,
)
from src.ui.components.combat_log_panel import CombatLogPanel
from src.ui.components.damage_tooltip import (
    draw_attack_preview,
    draw_heal_preview,
    draw_skill_damage_preview,
)
from src.ui.components.help_hint import draw_help_hint
from src.ui.components.help_overlay import draw_help_overlay
from src.ui.components.pause_menu import draw_pause_menu
from src.ui.components.skill_tooltip import draw_skill_tooltip
from src.ui.components.speed_indicator import draw_speed_indicator
from src.ui.components.synergy_indicator import draw_synergy_links
from src.ui.components.target_indicator import draw_target_indicator
from src.ui.components.turn_indicator import draw_turn_indicator
from src.ui.components.turn_timeline import TurnTimeline
from src.ui.font_manager import FontManager
from src.ui.input.action_menu import ActionMenu
from src.ui.input.menu_state import MenuLevel
from src.ui.scenes.combat_input_handler import InputState
from src.ui.scenes.interactive_combat import InteractiveCombatScene, TurnPhase


@dataclass(frozen=True)
class PreviewContext:
    """Groups parameters needed to render damage preview."""

    surface: pygame.Surface
    combatant: object
    target: object
    pending_type: object | None
    pending_skill: object | None
    card_rect: tuple[int, int, int, int]
    font: pygame.font.Font


class CombatRenderer:
    """Renders all combat visuals."""

    def __init__(
        self,
        scene: InteractiveCombatScene,
        input_state: InputState,
    ) -> None:
        self._scene = scene
        self._input = input_state
        self._battlefield: Battlefield | None = None
        self._log: CombatLogPanel | None = None
        self._fonts: FontManager | None = None
        self._anim_manager: AnimationManager | None = None
        self._timeline: TurnTimeline | None = None
        self._all_names: list[str] = []
        self._enemies: list = []
        self._synergy_names: list[str] = []
        self._elapsed_ms: int = 0
        self._intro: object | None = None

    def set_dependencies(
        self,
        battlefield: Battlefield,
        log: CombatLogPanel,
        fonts: FontManager,
    ) -> None:
        """Inject shared dependencies."""
        self._battlefield = battlefield
        self._log = log
        self._fonts = fonts

    def set_animation_deps(
        self,
        anim_manager: AnimationManager,
        timeline: TurnTimeline,
        intro: object,
    ) -> None:
        """Inject animation-related dependencies."""
        self._anim_manager = anim_manager
        self._timeline = timeline
        self._intro = intro

    def set_entity_data(
        self,
        all_names: list[str],
        enemies: list,
    ) -> None:
        """Inject entity references."""
        self._all_names = all_names
        self._enemies = enemies

    def draw(self, surface: pygame.Surface) -> None:
        """Main draw entry point."""
        surface.fill(colors.BG_DARK)
        self._draw_base_layer(surface)
        self._draw_indicators(surface)
        self._draw_interactive_layer(surface)
        self._draw_overlays(surface)

    def _draw_base_layer(self, surface: pygame.Surface) -> None:
        """Draws timeline, speed, battlefield, and animations."""
        assert self._timeline is not None
        assert self._fonts is not None
        assert self._anim_manager is not None
        assert self._battlefield is not None
        self._timeline.draw(
            surface, self._fonts, self._scene.round_number,
        )
        draw_speed_indicator(
            surface, self._input.speed_mult, self._fonts,
        )
        offsets = _build_shake_offsets(
            self._anim_manager, self._all_names,
        )
        offsets = _apply_intro_offsets(self._intro, offsets)
        self._battlefield.draw(
            surface, self._fonts, offsets=offsets,
        )
        self._anim_manager.draw(surface)

    def _draw_indicators(self, surface: pygame.Surface) -> None:
        """Draws turn highlight, target, boss, and synergy."""
        assert self._battlefield is not None
        _draw_turn_highlight(
            surface, self._scene, self._battlefield,
            self._elapsed_ms,
        )
        _draw_target_highlight(
            surface, self._input.menu, self._battlefield,
            self._elapsed_ms,
        )
        _draw_boss_indicators(
            surface, self._scene, self._enemies,
            self._battlefield, self._fonts,
        )
        _draw_synergy_indicators(
            surface, self._synergy_names, self._battlefield,
        )
        assert self._log is not None
        self._log.draw(surface, self._fonts.small)

    def _draw_interactive_layer(self, surface: pygame.Surface) -> None:
        """Draws menu and economy bar during input phase."""
        if self._scene.phase == TurnPhase.WAITING_INPUT:
            _draw_interactive_ui(
                surface, self._scene, self._input.menu,
                self._fonts, self._battlefield, self._enemies,
            )
        if self._scene.phase == TurnPhase.COMBAT_OVER:
            _draw_result(surface, self._scene, self._fonts)

    def _draw_overlays(self, surface: pygame.Surface) -> None:
        """Draws QTE, help, and pause overlays."""
        assert self._fonts is not None
        qte = self._input.qte_overlay
        if qte is not None:
            qte.draw(surface, self._fonts.large)
        draw_help_hint(surface, self._fonts)
        if self._input.show_help:
            draw_help_overlay(surface, self._fonts)
        elif self._input.show_pause:
            draw_pause_menu(surface, self._fonts)


# --- Module-level rendering functions (stateless) ---


def _build_shake_offsets(
    manager: AnimationManager, names: list[str],
) -> dict[str, tuple[int, int]]:
    """Coleta offsets de CardShake ativos."""
    offsets: dict[str, tuple[int, int]] = {}
    for name in names:
        offset = manager.get_shake_offset(name)
        if offset != (0, 0):
            offsets[name] = offset
    return offsets


def _apply_intro_offsets(
    intro: object | None,
    offsets: dict[str, tuple[int, int]],
) -> dict[str, tuple[int, int]]:
    """Merges intro animation offsets into shake offsets."""
    if intro is None or getattr(intro, "is_done", True):
        return offsets
    intro_offsets = intro.get_offsets()  # type: ignore[attr-defined]
    for name, (dx, dy) in intro_offsets.items():
        ox, oy = offsets.get(name, (0, 0))
        offsets[name] = (ox + dx, oy + dy)
    return offsets


def _draw_turn_highlight(
    surface: pygame.Surface,
    scene: InteractiveCombatScene,
    battlefield: Battlefield,
    elapsed_ms: int,
) -> None:
    """Draws pulsing indicator around active combatant."""
    name = scene.active_combatant
    if name is None:
        return
    rect = battlefield.get_card_rect(name)
    if rect is not None:
        draw_turn_indicator(surface, rect, elapsed_ms)


def _draw_target_highlight(
    surface: pygame.Surface,
    menu: ActionMenu | None,
    battlefield: Battlefield,
    elapsed_ms: int,
) -> None:
    """Draws pulsing border around highlighted target."""
    if menu is None:
        return
    target_name = menu.highlighted_target
    if target_name is None:
        return
    rect = battlefield.get_card_rect(target_name)
    if rect is not None:
        draw_target_indicator(surface, rect, elapsed_ms)


def _draw_boss_indicators(
    surface: pygame.Surface,
    scene: InteractiveCombatScene,
    enemies: list,
    battlefield: Battlefield,
    fonts: FontManager | None,
) -> None:
    """Draws boss empower bar, charge, and field overlay."""
    handler = _get_boss_handler(scene)
    if handler is None:
        return
    boss = enemies[0] if enemies else None
    if boss is None:
        return
    rect = battlefield.get_card_rect(boss.name)
    if rect is None:
        return
    assert fonts is not None
    _draw_boss_handler_visuals(surface, handler, rect, fonts)


def _draw_boss_handler_visuals(
    surface: pygame.Surface,
    handler: object,
    rect: tuple,
    fonts: FontManager,
) -> None:
    """Draws empower, charge, and field from boss handler."""
    empower = getattr(handler, "empower_bar", None)
    if empower is not None:
        draw_empower_bar(
            surface, rect, empower.current,
            empower._config.max_value, empower.is_empowered,
            fonts.small,
        )
    charge = getattr(handler, "_charge_pending", None)
    if charge is not None:
        draw_charge_indicator(
            surface, rect, "CHARGING!", fonts.small,
        )
    field = getattr(handler, "field_effect", None)
    if field is not None and not field.is_expired:
        draw_field_overlay(
            surface, field.config.name,
            fonts.small, layout.WINDOW_WIDTH,
        )


def _get_boss_handler(scene: InteractiveCombatScene):
    """Tries to find BossTurnHandler from the scene's engine."""
    engine = getattr(scene, "_engine", None)
    if engine is None:
        return None
    handler = getattr(engine, "_handler", None)
    if handler is None:
        return None
    from src.core.combat.boss.boss_turn_handler import BossTurnHandler
    if isinstance(handler, BossTurnHandler):
        return handler
    handlers = getattr(handler, "_handlers", {})
    for h in handlers.values():
        if isinstance(h, BossTurnHandler):
            return h
    return None


def _draw_synergy_indicators(
    surface: pygame.Surface,
    synergy_names: list[str],
    battlefield: Battlefield,
) -> None:
    """Draws links between synergy-bound enemies."""
    if not synergy_names:
        return
    rects = []
    for name in synergy_names:
        rect = battlefield.get_card_rect(name)
        if rect is not None:
            rects.append(rect)
    draw_synergy_links(surface, rects)


def _draw_interactive_ui(
    surface: pygame.Surface,
    scene: InteractiveCombatScene,
    menu: ActionMenu | None,
    fonts: FontManager | None,
    battlefield: Battlefield | None,
    enemies: list,
) -> None:
    """Draws action panel, skill tooltip, and damage preview."""
    assert fonts is not None
    if menu is not None:
        _draw_action_panel(surface, scene, menu, fonts)
        _draw_skill_tooltip_if_needed(surface, scene, menu, fonts)
        _draw_damage_preview_if_needed(
            surface, scene, menu, fonts, battlefield, enemies,
        )
    ctx = scene.current_context
    if ctx is not None:
        draw_economy_bar(surface, ctx.action_economy, fonts.small)


def _draw_action_panel(
    surface: pygame.Surface,
    scene: InteractiveCombatScene,
    menu: ActionMenu,
    fonts: FontManager,
) -> None:
    """Draws the action panel with options and breadcrumb."""
    name = scene.active_combatant or ""
    level = menu.current_level
    can_back = level != MenuLevel.ACTION_TYPE
    state = ActionPanelState(
        options=menu.options,
        level=level,
        combatant_name=name,
        breadcrumb=menu.breadcrumb,
        can_go_back=can_back,
        highlight_index=menu.highlight_index,
        description=menu.highlighted_description,
    )
    draw_action_panel(surface, state, fonts.medium)


def _draw_skill_tooltip_if_needed(
    surface: pygame.Surface,
    scene: InteractiveCombatScene,
    menu: ActionMenu,
    fonts: FontManager,
) -> None:
    """Draws tooltip when on SPECIFIC_ACTION level."""
    skill = menu.highlighted_skill
    if skill is None:
        return
    ctx = scene.current_context
    if ctx is None:
        return
    draw_skill_tooltip(surface, skill, ctx.combatant, fonts.small)


def _draw_damage_preview_if_needed(
    surface: pygame.Surface,
    scene: InteractiveCombatScene,
    menu: ActionMenu,
    fonts: FontManager,
    battlefield: Battlefield | None,
    enemies: list,
) -> None:
    """Draws damage preview when on target selection."""
    if menu.current_level != MenuLevel.TARGET_SELECT:
        return
    target_name = menu.highlighted_target
    if target_name is None:
        return
    target = _find_target_by_name(scene, target_name)
    if target is None:
        return
    assert battlefield is not None
    card_rect = battlefield.get_card_rect(target_name)
    if card_rect is None:
        return
    ctx = PreviewContext(
        surface=surface,
        combatant=scene.current_context.combatant,
        target=target,
        pending_type=menu.pending_action_type,
        pending_skill=menu.pending_skill,
        card_rect=card_rect,
        font=fonts.small,
    )
    render_preview(ctx)


def _find_target_by_name(
    scene: InteractiveCombatScene, name: str,
) -> object | None:
    """Encontra um alvo vivo pelo nome."""
    ctx = scene.current_context
    if ctx is None:
        return None
    for char in ctx.allies + ctx.enemies:
        if char.name == name and char.is_alive:
            return char
    return None


def render_preview(ctx: PreviewContext) -> None:
    """Renderiza tooltip de preview baseado no tipo de acao."""
    from src.core.combat.damage_preview import (
        preview_basic_attack,
        preview_heal,
        preview_skill_damage,
    )
    from src.core.combat.player_action import PlayerActionType

    if ctx.pending_type == PlayerActionType.BASIC_ATTACK:
        prev = preview_basic_attack(ctx.combatant, ctx.target)
        draw_attack_preview(
            ctx.surface, prev, ctx.card_rect, ctx.font,
        )
        return
    _render_skill_preview(ctx)


def _render_skill_preview(ctx: PreviewContext) -> None:
    """Renders heal or damage preview for a skill."""
    from src.core.combat.damage_preview import (
        preview_heal,
        preview_skill_damage,
    )

    if ctx.pending_skill is None:
        return
    heal = preview_heal(ctx.pending_skill, ctx.combatant, ctx.target)
    if heal is not None:
        draw_heal_preview(
            ctx.surface, heal, ctx.card_rect, ctx.font,
        )
        return
    dmg = preview_skill_damage(
        ctx.pending_skill, ctx.combatant, ctx.target,
    )
    if dmg is not None:
        draw_skill_damage_preview(
            ctx.surface, dmg, ctx.card_rect, ctx.font,
        )


def _draw_result(
    surface: pygame.Surface,
    scene: InteractiveCombatScene,
    fonts: FontManager | None,
) -> None:
    """Draws combat result text and continue hint."""
    result = scene.result
    if result is None:
        return
    assert fonts is not None
    text = result.name.replace("_", " ")
    rendered = fonts.large.render(text, True, colors.TEXT_YELLOW)
    cx = layout.WINDOW_WIDTH // 2
    cy = layout.BATTLEFIELD_HEIGHT // 2
    rect = rendered.get_rect(center=(cx, cy))
    surface.blit(rendered, rect)
    hint = fonts.small.render(
        "[ENTER] Continuar", True, colors.TEXT_MUTED,
    )
    surface.blit(hint, hint.get_rect(center=(cx, cy + 40)))
