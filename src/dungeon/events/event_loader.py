"""Event loader — carrega eventos aleatorios do JSON."""

from __future__ import annotations

import json

from src.core._paths import resolve_data_path
from src.dungeon.events.event_template import (
    EventChoice,
    EventEffect,
    EventTemplate,
)

_EVENTS_FILE = "data/dungeon/events/random_events.json"


def _parse_effect(raw: dict) -> EventEffect:
    """Converte dict JSON em EventEffect."""
    return EventEffect(
        effect_type=raw["type"],
        value=raw["value"],
    )


def _parse_choice(raw: dict) -> EventChoice:
    """Converte dict JSON em EventChoice."""
    effects = tuple(_parse_effect(e) for e in raw["effects"])
    return EventChoice(
        label=raw["label"],
        effects=effects,
        result_text=raw["result_text"],
    )


def _parse_event(event_id: str, raw: dict) -> EventTemplate:
    """Converte dict JSON em EventTemplate."""
    choices = tuple(_parse_choice(c) for c in raw["choices"])
    return EventTemplate(
        event_id=event_id,
        title=raw["title"],
        description=raw["description"],
        choices=choices,
    )


def load_events() -> dict[str, EventTemplate]:
    """Carrega todos os eventos do JSON."""
    path = resolve_data_path(_EVENTS_FILE)
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {
        key: _parse_event(key, data)
        for key, data in raw.items()
    }
