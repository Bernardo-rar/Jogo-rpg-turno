"""SynergyLoader — loads synergy definitions from JSON."""

from __future__ import annotations

import json

from src.core._paths import resolve_data_path
from src.core.combat.synergy.synergy_config import SynergyConfig

_SYNERGIES_FILE = "data/dungeon/enemies/synergies.json"

_cache: dict[str, SynergyConfig] | None = None


def load_synergies() -> dict[str, SynergyConfig]:
    """Loads all synergy definitions from JSON. Cached."""
    global _cache
    if _cache is not None:
        return _cache
    path = resolve_data_path(_SYNERGIES_FILE)
    raw = json.loads(path.read_text(encoding="utf-8"))
    _cache = {
        key: SynergyConfig.from_dict(data)
        for key, data in raw.items()
    }
    return _cache


def get_synergy(synergy_id: str) -> SynergyConfig | None:
    """Returns a single synergy config by ID, or None."""
    return load_synergies().get(synergy_id)
