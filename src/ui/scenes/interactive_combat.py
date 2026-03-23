"""InteractiveCombatScene — state machine de combate interativo."""

from __future__ import annotations

from enum import Enum, auto

from src.core.combat.action_resolver import resolve_player_action
from src.core.combat.combat_engine import (
    CombatEngine,
    CombatResult,
    TurnContext,
    TurnHandler,
    TurnStepResult,
)
from src.core.combat.player_action import PlayerAction, PlayerActionType


class TurnPhase(Enum):
    """Fase da state machine de combate interativo."""

    STARTING_ROUND = auto()
    EFFECT_TICK = auto()
    WAITING_INPUT = auto()
    AI_TURN = auto()
    COMBAT_OVER = auto()


_BLOCKING_PHASES = frozenset({TurnPhase.WAITING_INPUT, TurnPhase.COMBAT_OVER})


class InteractiveCombatScene:
    """Orquestra combate turno-a-turno: input do jogador + IA."""

    def __init__(
        self,
        engine: CombatEngine,
        party_names: frozenset[str],
        ai_handler: TurnHandler,
    ) -> None:
        self._engine = engine
        self._party_names = party_names
        self._ai_handler = ai_handler
        self._phase = TurnPhase.STARTING_ROUND
        self._active_name: str | None = None
        self._current_step: TurnStepResult | None = None
        self._current_context: TurnContext | None = None

    @property
    def phase(self) -> TurnPhase:
        return self._phase

    @property
    def active_combatant(self) -> str | None:
        return self._active_name

    @property
    def current_context(self) -> TurnContext | None:
        return self._current_context

    def update(self, dt_ms: int) -> bool:
        """Avanca state machine ate fase bloqueante."""
        while self._phase not in _BLOCKING_PHASES:
            self._step()
        return True

    def _step(self) -> None:
        if self._phase == TurnPhase.STARTING_ROUND:
            self._do_start_round()
        elif self._phase == TurnPhase.EFFECT_TICK:
            self._do_effect_tick()
        elif self._phase == TurnPhase.AI_TURN:
            self._do_ai_turn()

    def submit_player_action(self, action: PlayerAction) -> None:
        """Recebe acao do jogador. So processa em WAITING_INPUT."""
        if self._phase != TurnPhase.WAITING_INPUT:
            return
        if self._current_context is None:
            return
        self._execute_action(action)

    def shortcut_end_turn(self) -> None:
        """Atalho Tab/Space para End Turn."""
        self.submit_player_action(
            PlayerAction(action_type=PlayerActionType.END_TURN),
        )

    def _do_start_round(self) -> None:
        self._engine.start_round()
        self._advance_to_next()

    def _do_effect_tick(self) -> None:
        if self._active_name is None:
            self._advance_to_next()
            return
        step = self._engine.prepare_turn(self._active_name)
        self._current_step = step
        if self._check_combat_end():
            return
        if not step.can_act:
            self._advance_to_next()
            return
        self._current_context = step.context
        if self._is_party_member(self._active_name):
            self._phase = TurnPhase.WAITING_INPUT
        else:
            self._phase = TurnPhase.AI_TURN

    def _do_ai_turn(self) -> None:
        if self._current_context is None:
            self._advance_to_next()
            return
        events = self._ai_handler.execute_turn(self._current_context)
        self._engine.resolve_turn(events)
        if self._check_combat_end():
            return
        self._advance_to_next()

    def _execute_action(self, action: PlayerAction) -> None:
        if self._current_context is None:
            return
        events = resolve_player_action(action, self._current_context)
        self._engine.resolve_turn(events)
        if self._check_combat_end():
            return
        if self._should_continue_turn(action):
            return
        self._advance_to_next()

    def _should_continue_turn(self, action: PlayerAction) -> bool:
        if action.action_type == PlayerActionType.END_TURN:
            return False
        return True

    def _advance_to_next(self) -> None:
        name = self._engine.get_next_combatant()
        if name is None:
            if self._engine.result is not None:
                self._phase = TurnPhase.COMBAT_OVER
                return
            self._engine.start_round()
            name = self._engine.get_next_combatant()
        self._active_name = name
        self._current_context = None
        self._current_step = None
        self._phase = TurnPhase.EFFECT_TICK

    def _is_party_member(self, name: str) -> bool:
        return name in self._party_names

    def _check_combat_end(self) -> bool:
        if self._engine.result is not None:
            self._phase = TurnPhase.COMBAT_OVER
            return True
        return False
