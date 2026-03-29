"""Slot config: parametros de spell slots carregados do JSON."""

from __future__ import annotations

import json
from dataclasses import dataclass

from src.core._paths import resolve_data_path

_CONFIG_FILE = "data/progression/slot_config.json"

LEVEL_10_THRESHOLD = 10


@dataclass(frozen=True)
class SlotConfig:
    """Configuracao de spell slots."""

    base_slot_budget: int
    budget_per_level: int
    level_10_bonus: int
    base_slot_count: int
    max_slot_count: int
    reaction_slots: int
    passive_limit: int


def load_slot_config() -> SlotConfig:
    """Carrega config de slots do JSON."""
    path = resolve_data_path(_CONFIG_FILE)
    raw = json.loads(path.read_text(encoding="utf-8"))
    return SlotConfig(**raw)
