"""Renderiza CombatLog como texto legivel ou JSON."""

from __future__ import annotations

import json
from dataclasses import asdict

from src.core.combat.combat_log import CombatLog, CombatLogEntry, EventType

_TEXT_TEMPLATES: dict[EventType, str] = {
    EventType.ATTACK: "[Round {r}] {actor} attacks {target} for {value} damage ({detail})",
    EventType.HEAL: "[Round {r}] {actor} heals {target} for {value} HP",
    EventType.BARRIER_CREATE: "[Round {r}] {actor} creates barrier ({value} shield points)",
    EventType.BARRIER_ABSORB: "[Round {r}] {actor}'s barrier absorbs {value} damage",
    EventType.OVERCHARGE_ON: "[Round {r}] {actor} activates overcharge",
    EventType.OVERCHARGE_OFF: "[Round {r}] {actor} deactivates overcharge",
    EventType.CHANNEL_DIVINITY: "[Round {r}] {actor} channels divinity",
    EventType.MANA_RESTORE: "[Round {r}] {actor} restores {value} mana",
    EventType.DEATH: "[Round {r}] {actor} has fallen",
}


def _format_entry(entry: CombatLogEntry) -> str:
    template = _TEXT_TEMPLATES[entry.event_type]
    return template.format(
        r=entry.round_number,
        actor=entry.actor_name,
        target=entry.target_name,
        value=entry.value,
        detail=entry.detail,
    )


def _entry_to_dict(entry: CombatLogEntry) -> dict:
    data = asdict(entry)
    data["event_type"] = entry.event_type.name
    return data


class LogFormatter:
    """Renderiza CombatLog em texto ou JSON."""

    @staticmethod
    def to_text(log: CombatLog) -> str:
        if not log.entries:
            return ""
        sorted_entries = sorted(log.entries, key=lambda e: e.round_number)
        return "\n".join(_format_entry(e) for e in sorted_entries)

    @staticmethod
    def to_json(log: CombatLog) -> str:
        sorted_entries = sorted(log.entries, key=lambda e: e.round_number)
        return json.dumps(
            [_entry_to_dict(e) for e in sorted_entries],
            ensure_ascii=False,
        )
