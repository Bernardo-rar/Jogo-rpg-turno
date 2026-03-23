"""Carrega EncounterTemplates a partir de JSON."""

from __future__ import annotations

import json

from src.core._paths import resolve_data_path
from src.dungeon.encounters.encounter_difficulty import EncounterDifficulty
from src.dungeon.encounters.encounter_template import EncounterTemplate

_TEMPLATES_FILE = "data/dungeon/encounters/templates.json"


def load_encounter_templates() -> dict[str, EncounterTemplate]:
    """Carrega todos os templates de encounter."""
    path = resolve_data_path(_TEMPLATES_FILE)
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {
        tid: EncounterTemplate.from_dict(data) for tid, data in raw.items()
    }


def load_templates_by_difficulty(
    difficulty: EncounterDifficulty,
) -> dict[str, EncounterTemplate]:
    """Filtra templates por dificuldade."""
    all_templates = load_encounter_templates()
    return {
        tid: t for tid, t in all_templates.items()
        if t.difficulty == difficulty
    }
