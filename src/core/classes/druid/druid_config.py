from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

DRUID_CONFIG_DATA_PATH = "data/classes/druid_config.json"


@dataclass(frozen=True)
class DruidConfig:
    """Configuracao do Druida: custos, passivas."""

    transform_mana_cost: int
    field_mana_cost: int
    healing_bonus: float
    hp_regen_bonus: float
    mana_regen_bonus: float
    nature_atk_bonus: float


def load_druid_config(
    filepath: str = DRUID_CONFIG_DATA_PATH,
) -> DruidConfig:
    """Carrega configuracao do Druida do JSON."""
    with open(Path(filepath), encoding="utf-8") as f:
        data = json.load(f)
    return DruidConfig(**data)
