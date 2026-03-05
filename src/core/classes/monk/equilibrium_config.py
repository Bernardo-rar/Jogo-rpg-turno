from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

EQ_DATA_PATH = "data/classes/monk_equilibrium.json"


@dataclass(frozen=True)
class EquilibriumConfig:
    """Configuracao da barra de Equilibrium do Monk."""

    max_value: int
    vitality_upper: int
    destruction_lower: int
    shift_per_attack: int
    shift_per_defend: int
    decay_per_turn: int
    vitality_def_bonus: float
    vitality_regen_bonus: float
    destruction_atk_bonus: float
    destruction_crit_bonus: float
    balance_atk_bonus: float
    balance_def_bonus: float
    base_hit_count: int
    destruction_extra_hits: int
    debuff_chance_max: float


def load_equilibrium_config(
    filepath: str = EQ_DATA_PATH,
) -> EquilibriumConfig:
    """Carrega configuracao de equilibrium do JSON."""
    with open(Path(filepath), encoding="utf-8") as f:
        data = json.load(f)
    return EquilibriumConfig(**data)
