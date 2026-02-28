from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

OVERCHARGE_DATA_PATH = "data/classes/mage_overcharge.json"


@dataclass(frozen=True)
class OverchargeConfig:
    """Configuracao do Overcharge do Mago: multiplicador e custo."""

    atk_multiplier: float
    mana_cost_per_turn: int


def load_overcharge_config(
    filepath: str = OVERCHARGE_DATA_PATH,
) -> OverchargeConfig:
    """Carrega configuracao de overcharge do JSON."""
    with open(Path(filepath), encoding="utf-8") as f:
        data = json.load(f)
    return OverchargeConfig(**data)
