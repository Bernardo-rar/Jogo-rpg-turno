from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

OVERCHARGED_DATA_PATH = "data/classes/sorcerer_overcharged.json"


@dataclass(frozen=True)
class OverchargedConfig:
    """Configuracao do Overcharged e passivas do Sorcerer."""

    atk_multiplier: float
    mana_cost_per_turn: int
    self_damage_pct: float
    metamagic_mana_cost: int
    born_of_magic_bonus: float


def load_overcharged_config(
    filepath: str = OVERCHARGED_DATA_PATH,
) -> OverchargedConfig:
    """Carrega configuracao de overcharged do JSON."""
    with open(Path(filepath), encoding="utf-8") as f:
        data = json.load(f)
    return OverchargedConfig(**data)
