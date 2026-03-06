from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

BARD_CONFIG_DATA_PATH = "data/classes/bard_config.json"


@dataclass(frozen=True)
class BardConfig:
    """Configuracao do Bardo: passivas e mecanicas."""

    speed_bonus_pct: float
    buff_effectiveness_bonus: float
    debuff_effectiveness_bonus: float
    extra_bonus_actions: int


def load_bard_config(
    filepath: str = BARD_CONFIG_DATA_PATH,
) -> BardConfig:
    """Carrega configuracao do Bardo do JSON."""
    with open(Path(filepath), encoding="utf-8") as f:
        data = json.load(f)
    return BardConfig(**data)
