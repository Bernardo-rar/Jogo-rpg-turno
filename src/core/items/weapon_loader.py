"""Carrega armas do JSON."""

from __future__ import annotations

import json

from src.core._paths import resolve_data_path
from src.core.items.weapon import Weapon

WEAPONS_DATA_PATH = "data/weapons/weapons.json"


def load_weapons(filepath: str = WEAPONS_DATA_PATH) -> dict[str, Weapon]:
    """Carrega todas as armas do JSON. Retorna dict weapon_id -> Weapon."""
    path = resolve_data_path(filepath)
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {
        weapon_id: Weapon.from_dict(data)
        for weapon_id, data in raw.items()
    }
