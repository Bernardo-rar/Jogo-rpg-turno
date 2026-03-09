"""Carrega consumiveis do JSON."""

from __future__ import annotations

import json

from src.core._paths import resolve_data_path
from src.core.items.consumable import Consumable

CONSUMABLES_DATA_PATH = "data/consumables/consumables.json"


def load_consumables(
    filepath: str = CONSUMABLES_DATA_PATH,
) -> dict[str, Consumable]:
    """Carrega todos os consumiveis do JSON. Retorna dict id -> Consumable."""
    path = resolve_data_path(filepath)
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {
        cid: Consumable.from_dict(cid, data)
        for cid, data in raw.items()
    }
