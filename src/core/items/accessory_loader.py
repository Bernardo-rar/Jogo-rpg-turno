"""Carrega acessorios do JSON."""

from __future__ import annotations

import json

from src.core._paths import resolve_data_path
from src.core.items.accessory import Accessory

ACCESSORIES_DATA_PATH = "data/accessories/accessories.json"


def load_accessories(
    filepath: str = ACCESSORIES_DATA_PATH,
) -> dict[str, Accessory]:
    """Carrega todos os acessorios do JSON. Retorna dict id -> Accessory."""
    path = resolve_data_path(filepath)
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {
        acc_id: Accessory.from_dict(data)
        for acc_id, data in raw.items()
    }
