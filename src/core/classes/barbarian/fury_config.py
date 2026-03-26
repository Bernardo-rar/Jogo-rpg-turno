from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

FURY_DATA_PATH = "data/classes/barbarian_fury.json"


@dataclass(frozen=True)
class FuryConfig:
    """Configuracao da Barra de Furia do Barbaro."""

    fury_max_ratio: float
    fury_on_damage_ratio: float
    fury_on_basic_attack: int
    fury_decay_per_turn: int
    atk_bonus_at_max_fury: float
    regen_bonus_at_max_fury: float
    missing_hp_atk_bonus: float
    reckless_atk_multiplier: float
    reckless_def_multiplier: float


def load_fury_config(
    filepath: str = FURY_DATA_PATH,
) -> FuryConfig:
    """Carrega configuracao de furia do JSON."""
    with open(Path(filepath), encoding="utf-8") as f:
        data = json.load(f)
    return FuryConfig(**data)
