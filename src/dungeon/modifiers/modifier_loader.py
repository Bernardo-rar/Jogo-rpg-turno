"""Carrega RunModifiers a partir do JSON em data/dungeon/modifiers/."""

from __future__ import annotations

import json
from pathlib import Path

from src.core._paths import resolve_data_path
from src.dungeon.modifiers.run_modifier import RunModifier

_MODIFIERS_PATH = "data/dungeon/modifiers/modifiers.json"


def load_modifiers() -> dict[str, RunModifier]:
    """Carrega todos os RunModifier do JSON."""
    path = resolve_data_path(_MODIFIERS_PATH)
    raw = json.loads(path.read_text(encoding="utf-8"))
    return _parse_modifiers(raw)


def _parse_modifiers(raw: dict) -> dict[str, RunModifier]:
    """Converte dict raw em dict de RunModifier."""
    return {
        modifier_id: RunModifier.from_dict(modifier_id, data)
        for modifier_id, data in raw.items()
    }
