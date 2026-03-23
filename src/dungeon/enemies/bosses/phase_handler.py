"""PhaseHandler — TurnHandler que muda comportamento por HP threshold."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.dungeon.enemies.bosses.boss_phase import BossPhase

if TYPE_CHECKING:
    from src.core.combat.combat_engine import CombatEvent, TurnContext, TurnHandler


class PhaseHandler:
    """Delega execução de turno para o handler da fase atual do boss.

    Fases são ordenadas por threshold decrescente.
    A fase ativa é a primeira cujo threshold >= HP ratio atual.
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

    @property
    def current_phase(self) -> int:
        return self._current_phase

    def execute_turn(self, context: TurnContext) -> list[CombatEvent]:
        phase = self._resolve_phase(context)
        self._current_phase = phase.phase_number
        handler = self._phase_handlers.get(
            phase.handler_key, self._default,
        )
        return handler.execute_turn(context)

    def _resolve_phase(self, context: TurnContext) -> BossPhase:
        ratio = _hp_ratio(context)
        for phase in self._phases:
            if ratio > phase.hp_threshold:
                return phase
        return self._phases[-1]


def _hp_ratio(context: TurnContext) -> float:
    boss = context.combatant
    if boss.max_hp == 0:
        return 0.0
    return boss.current_hp / boss.max_hp


def _sort_by_threshold(phases: tuple[BossPhase, ...]) -> tuple[BossPhase, ...]:
    return tuple(sorted(phases, key=lambda p: p.hp_threshold, reverse=True))
