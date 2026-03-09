"""Sistema de log estruturado para eventos de combate."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from src.core.combat.combat_engine import CombatEvent, EventType as EngineEventType


class EventType(Enum):
    """Tipos de evento rastreados pelo combat log."""

    ATTACK = auto()
    HEAL = auto()
    BARRIER_CREATE = auto()
    BARRIER_ABSORB = auto()
    OVERCHARGE_ON = auto()
    OVERCHARGE_OFF = auto()
    CHANNEL_DIVINITY = auto()
    MANA_RESTORE = auto()
    DEATH = auto()
    EFFECT_APPLY = auto()
    EFFECT_TICK = auto()
    EFFECT_EXPIRE = auto()
    ELEMENTAL_DAMAGE = auto()
    SKIP_TURN = auto()


@dataclass(frozen=True)
class CombatLogEntry:
    """Registro imutavel de um evento no combat log."""

    round_number: int
    event_type: EventType
    actor_name: str
    target_name: str = ""
    value: int = 0
    detail: str = ""


class CombatLog:
    """Coleta e filtra entradas de combat log."""

    def __init__(self) -> None:
        self._entries: list[CombatLogEntry] = []

    @property
    def entries(self) -> list[CombatLogEntry]:
        return list(self._entries)

    def add(self, entry: CombatLogEntry) -> None:
        self._entries.append(entry)

    def add_from_combat_event(self, event: CombatEvent) -> None:
        """Converte CombatEvent em CombatLogEntry."""
        if event.damage is not None:
            self._add_damage_event(event)
        else:
            self._add_non_damage_event(event)

    def _add_damage_event(self, event: CombatEvent) -> None:
        detail = "critical" if event.damage.is_critical else ""
        self.add(CombatLogEntry(
            round_number=event.round_number,
            event_type=EventType.ATTACK,
            actor_name=event.actor_name,
            target_name=event.target_name,
            value=event.damage.final_damage,
            detail=detail,
        ))

    def _add_non_damage_event(self, event: CombatEvent) -> None:
        log_type = _ENGINE_TO_LOG.get(event.event_type, EventType.EFFECT_APPLY)
        self.add(CombatLogEntry(
            round_number=event.round_number,
            event_type=log_type,
            actor_name=event.actor_name,
            target_name=event.target_name,
            value=event.value,
            detail=event.description,
        ))

    def get_by_round(self, round_number: int) -> list[CombatLogEntry]:
        return [e for e in self._entries if e.round_number == round_number]

    def get_by_actor(self, name: str) -> list[CombatLogEntry]:
        return [e for e in self._entries if e.actor_name == name]

    def get_by_type(self, event_type: EventType) -> list[CombatLogEntry]:
        return [e for e in self._entries if e.event_type == event_type]


_ENGINE_TO_LOG: dict[EngineEventType, EventType] = {
    EngineEventType.HEAL: EventType.HEAL,
    EngineEventType.MANA_RESTORE: EventType.MANA_RESTORE,
    EngineEventType.BUFF: EventType.EFFECT_APPLY,
    EngineEventType.DEBUFF: EventType.EFFECT_APPLY,
    EngineEventType.AILMENT: EventType.EFFECT_APPLY,
    EngineEventType.CLEANSE: EventType.EFFECT_EXPIRE,
}
