from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Protocol

from src.core.characters.character import Character
from src.core.combat.action_economy import ActionEconomy
from src.core.combat.damage import DamageResult
from src.core.combat.turn_order import Combatant, TurnOrder

MAX_ROUNDS = 100


class CombatResult(Enum):
    """Resultado final do combate."""

    PARTY_VICTORY = auto()
    PARTY_DEFEAT = auto()
    DRAW = auto()


@dataclass(frozen=True)
class CombatEvent:
    """Registro imutavel de algo que aconteceu no combate."""

    round_number: int
    actor_name: str
    target_name: str
    damage: DamageResult


@dataclass(frozen=True)
class TurnContext:
    """Contexto imutavel passado ao TurnHandler para decidir e executar acao."""

    combatant: Character
    allies: list[Character]
    enemies: list[Character]
    action_economy: ActionEconomy
    round_number: int


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
        self._result: CombatResult | None = None

    def run_round(self) -> CombatResult | None:
        """Executa uma rodada. Retorna resultado se acabou, None se continua."""
        self._round += 1
        self._turn_order.reset()
        combatant_proto = self._turn_order.next()
        while combatant_proto is not None:
            result = self._execute_combatant_turn(combatant_proto)
            if result is not None:
                return result
            combatant_proto = self._turn_order.next()
        return self._result

    def _execute_combatant_turn(
        self, combatant_proto: Combatant,
    ) -> CombatResult | None:
        combatant = self._participants[combatant_proto.name]
        economy = self._economies[combatant.name]
        economy.reset()
        allies, enemies = self._get_teams(combatant)
        context = TurnContext(
            combatant=combatant, allies=allies, enemies=enemies,
            action_economy=economy, round_number=self._round,
        )
        self._events.extend(self._handler.execute_turn(context))
        self._result = self._check_result()
        return self._result

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
