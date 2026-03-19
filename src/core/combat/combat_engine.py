from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Protocol

from src.core.characters.character import Character
from src.core.combat.action_economy import ActionEconomy
from src.core.combat.damage import DamageResult
from src.core.combat.effect_phase import (
    EffectLogEntry,
    apply_tick_results,
    create_skip_entry,
    process_effect_ticks,
    should_skip_turn,
)
from src.core.effects.tick_result import TickResult
from src.core.combat.turn_order import Combatant, TurnOrder

MAX_ROUNDS = 100
DEFAULT_SKIP_MESSAGE = "Cannot act"


class CombatResult(Enum):
    """Resultado final do combate."""

    PARTY_VICTORY = auto()
    PARTY_DEFEAT = auto()
    DRAW = auto()


class EventType(Enum):
    """Tipo de evento de combate."""

    DAMAGE = auto()
    HEAL = auto()
    BUFF = auto()
    DEBUFF = auto()
    AILMENT = auto()
    CLEANSE = auto()
    MANA_RESTORE = auto()
    FLEE = auto()
    SKILL_USE = auto()
    ITEM_USE = auto()


@dataclass(frozen=True)
class CombatEvent:
    """Registro imutavel de algo que aconteceu no combate."""

    round_number: int
    actor_name: str
    target_name: str
    damage: DamageResult | None = None
    event_type: EventType = EventType.DAMAGE
    value: int = 0
    description: str = ""


@dataclass(frozen=True)
class TurnContext:
    """Contexto imutavel passado ao TurnHandler para decidir e executar acao."""

    combatant: Character
    allies: list[Character]
    enemies: list[Character]
    action_economy: ActionEconomy
    round_number: int


@dataclass(frozen=True)
class TurnStepResult:
    """Resultado imutavel de prepare_turn: contexto pronto ou motivo do skip."""

    can_act: bool
    context: TurnContext | None
    effect_entries: tuple[EffectLogEntry, ...]
    skip_reason: str = ""


class TurnHandler(Protocol):
    """Strategy: decide e executa a acao de um combatente no turno."""

    def execute_turn(self, context: TurnContext) -> list[CombatEvent]: ...


class CombatEngine:
    """Motor de combate por turnos. Orquestra rounds, turnos e win/lose."""

    def __init__(
        self,
        party: list[Character],
        enemies: list[Character],
        turn_handler: TurnHandler,
    ) -> None:
        self._party = party
        self._enemies = enemies
        self._handler = turn_handler
        all_combatants = party + enemies
        names = [c.name for c in all_combatants]
        if len(names) != len(set(names)):
            raise ValueError("Combatant names must be unique")
        self._turn_order = TurnOrder(all_combatants)
        self._economies = {c.name: ActionEconomy() for c in all_combatants}
        self._participants = {c.name: c for c in all_combatants}
        self._round = 0
        self._events: list[CombatEvent] = []
        self._effect_log: list[EffectLogEntry] = []
        self._result: CombatResult | None = None

    def start_round(self) -> None:
        """Incrementa round e reseta turn order."""
        self._round += 1
        self._turn_order.reset()

    def get_next_combatant(self) -> str | None:
        """Retorna nome do proximo combatente ou None se round acabou."""
        proto = self._turn_order.next()
        return proto.name if proto is not None else None

    def prepare_turn(self, combatant_name: str) -> TurnStepResult:
        """Fase 1: reset economy, tick cooldowns, process effects, check skip."""
        combatant = self._participants[combatant_name]
        economy = self._economies[combatant_name]
        economy.reset()
        _tick_cooldowns(combatant)
        tick_results = process_effect_ticks(combatant.effect_manager)
        entries = tuple(
            apply_tick_results(combatant, tick_results, self._round),
        )
        self._effect_log.extend(entries)
        skip = should_skip_turn(tick_results)
        if not combatant.is_alive or skip:
            reason = self._get_skip_reason(combatant, tick_results)
            if combatant.is_alive and skip:
                self._log_skip(combatant, tick_results)
            return TurnStepResult(
                can_act=False, context=None,
                effect_entries=entries, skip_reason=reason,
            )
        context = self._build_context(combatant, economy)
        return TurnStepResult(
            can_act=True, context=context, effect_entries=entries,
        )

    def resolve_turn(self, events: list[CombatEvent]) -> CombatResult | None:
        """Fase 2: registra eventos e checa vitoria/derrota."""
        self._events.extend(events)
        self._result = self._check_result()
        return self._result

    def run_round(self) -> CombatResult | None:
        """Executa uma rodada. Retorna resultado se acabou, None se continua."""
        self.start_round()
        name = self.get_next_combatant()
        while name is not None:
            result = self._execute_combatant_turn_internal(name)
            if result is not None:
                return result
            name = self.get_next_combatant()
        return self._result

    def _execute_combatant_turn_internal(
        self, combatant_name: str,
    ) -> CombatResult | None:
        step = self.prepare_turn(combatant_name)
        if step.can_act:
            self._execute_handler_from_context(step.context)
        self._result = self._check_result()
        return self._result

    def _build_context(
        self, combatant: Character, economy: ActionEconomy,
    ) -> TurnContext:
        allies, enemies = self._get_teams(combatant)
        return TurnContext(
            combatant=combatant, allies=allies, enemies=enemies,
            action_economy=economy, round_number=self._round,
        )

    def _execute_handler_from_context(self, context: TurnContext) -> None:
        self._events.extend(self._handler.execute_turn(context))

    def _get_skip_reason(
        self, combatant: Character, tick_results: list[TickResult],
    ) -> str:
        if not combatant.is_alive:
            return "Dead"
        skip_msgs = [r.message for r in tick_results if r.skip_turn]
        return skip_msgs[0] if skip_msgs else DEFAULT_SKIP_MESSAGE

    def _log_skip(
        self, combatant: Character, tick_results: list[TickResult],
    ) -> None:
        skip_msgs = [r.message for r in tick_results if r.skip_turn]
        msg = skip_msgs[0] if skip_msgs else DEFAULT_SKIP_MESSAGE
        self._effect_log.append(
            create_skip_entry(combatant.name, self._round, msg),
        )

    def run_combat(self) -> CombatResult:
        """Executa combate completo ate vitoria, derrota ou empate."""
        while self._round < MAX_ROUNDS:
            result = self.run_round()
            if result is not None:
                return result
        self._result = CombatResult.DRAW
        return self._result

    @property
    def round_number(self) -> int:
        return self._round

    @property
    def events(self) -> list[CombatEvent]:
        return list(self._events)

    @property
    def result(self) -> CombatResult | None:
        return self._result

    @property
    def effect_log(self) -> list[EffectLogEntry]:
        return list(self._effect_log)

    def _get_teams(
        self, combatant: Character
    ) -> tuple[list[Character], list[Character]]:
        if combatant in self._party:
            return self._party, self._enemies
        return self._enemies, self._party

    def _check_result(self) -> CombatResult | None:
        party_alive = any(c.is_alive for c in self._party)
        enemies_alive = any(c.is_alive for c in self._enemies)
        if not enemies_alive:
            return CombatResult.PARTY_VICTORY
        if not party_alive:
            return CombatResult.PARTY_DEFEAT
        return None


def _tick_cooldowns(combatant: Character) -> None:
    """Decrementa cooldowns do combatente se tiver skill_bar."""
    bar = combatant.skill_bar
    if bar is not None:
        bar.cooldown_tracker.tick()
