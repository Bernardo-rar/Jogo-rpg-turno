"""Carrega armaduras do JSON."""

from __future__ import annotations

import json

from src.core._paths import resolve_data_path
from src.core.items.armor import Armor

ARMORS_DATA_PATH = "data/armors/armors.json"


def load_armors(filepath: str = ARMORS_DATA_PATH) -> dict[str, Armor]:
    """Carrega todas as armaduras do JSON. Retorna dict armor_id -> Armor."""
    path = resolve_data_path(filepath)
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {
        armor_id: Armor.from_dict(data)
        for armor_id, data in raw.items()
    }
