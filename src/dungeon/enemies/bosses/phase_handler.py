"""PhaseHandler — TurnHandler que muda comportamento por HP threshold."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.core.effects.buff_factory import create_percent_buff
from src.core.effects.modifiable_stat import ModifiableStat
from src.dungeon.enemies.bosses.boss_phase import BossPhase

if TYPE_CHECKING:
    from src.core.characters.character import Character
    from src.core.combat.combat_engine import CombatEvent, TurnContext, TurnHandler
    from src.dungeon.enemies.bosses.phase_transition import TransitionEffect


class PhaseHandler:
    """Delega execucao de turno para o handler da fase atual do boss.

    Fases sao ordenadas por threshold decrescente.
    A fase ativa e a primeira cujo threshold >= HP ratio atual.
    Transicoes de fase disparam uma unica vez por phase_number.
    """

    def __init__(
        self,
        phases: tuple[BossPhase, ...],
        phase_handlers: dict[str, TurnHandler],
        default_handler: TurnHandler,
    ) -> None:
        self._phases = _sort_by_threshold(phases)
        self._phase_handlers = phase_handlers
        self._default = default_handler
        self._current_phase: int = self._phases[0].phase_number
        self._transitions_fired: set[int] = set()

    @property
    def current_phase(self) -> int:
        return self._current_phase

    def execute_turn(self, context: TurnContext) -> list[CombatEvent]:
        """Resolve fase, dispara transicao se necessario, delega turno."""
        old_phase = self._current_phase
        phase = self._resolve_phase(context)
        self._current_phase = phase.phase_number
        transition_events = self._maybe_fire_transition(
            old_phase, phase, context,
        )
        handler = self._phase_handlers.get(
            phase.handler_key, self._default,
        )
        turn_events = handler.execute_turn(context)
        return transition_events + turn_events

    def _resolve_phase(self, context: TurnContext) -> BossPhase:
        ratio = _hp_ratio(context)
        for phase in self._phases:
            if ratio > phase.hp_threshold:
                return phase
        return self._phases[-1]

    def _maybe_fire_transition(
        self,
        old_phase: int,
        new_phase: BossPhase,
        context: TurnContext,
    ) -> list[CombatEvent]:
        """Dispara transicao se fase mudou e ainda nao foi disparada."""
        if old_phase == new_phase.phase_number:
            return []
        if new_phase.phase_number in self._transitions_fired:
            return []
        if new_phase.transition is None:
            return []
        self._transitions_fired.add(new_phase.phase_number)
        return _fire_transition(
            new_phase.transition, context,
        )


def _fire_transition(
    transition, context: TurnContext,
) -> list[CombatEvent]:
    """Aplica self-buffs e retorna eventos de battle cry."""
    from src.core.combat.combat_engine import CombatEvent, EventType

    events: list[CombatEvent] = []
    boss = context.combatant
    for effect in transition.self_buffs:
        _apply_self_buff(boss, effect)
    if transition.battle_cry:
        events.append(CombatEvent(
            round_number=context.round_number,
            actor_name=boss.name,
            target_name=boss.name,
            event_type=EventType.BUFF,
            description=transition.battle_cry,
        ))
    return events


def _apply_self_buff(
    boss: Character, effect: TransitionEffect,
) -> None:
    """Aplica um TransitionEffect como StatBuff no boss."""
    stat = ModifiableStat[effect.stat]
    buff = create_percent_buff(
        stat=stat, percent=effect.percent, duration=effect.duration,
    )
    boss.effect_manager.add_effect(buff)


def _hp_ratio(context: TurnContext) -> float:
    boss = context.combatant
    if boss.max_hp == 0:
        return 0.0
    return boss.current_hp / boss.max_hp


def _sort_by_threshold(phases: tuple[BossPhase, ...]) -> tuple[BossPhase, ...]:
    return tuple(sorted(phases, key=lambda p: p.hp_threshold, reverse=True))
