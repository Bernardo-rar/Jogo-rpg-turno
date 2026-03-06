from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

WARLOCK_CONFIG_DATA_PATH = "data/classes/warlock_config.json"


@dataclass(frozen=True)
class WarlockConfig:
    """Configuracao do Warlock: insanidade, sede, passivas."""

    insanity_on_cast: int
    insanity_on_damage_ratio: float
    insanity_decay_per_turn: int
    insanity_atk_bonus_at_max: float
    insanity_def_penalty_at_max: float
    thirst_atk_bonus: float
    thirst_regen_bonus: float
    thirst_def_bonus: float
    life_drain_ratio: float
    spell_ramp_bonus: float
    spell_ramp_cha_scaling: float


def load_warlock_config(
    filepath: str = WARLOCK_CONFIG_DATA_PATH,
) -> WarlockConfig:
    """Carrega configuracao do Warlock do JSON."""
    with open(Path(filepath), encoding="utf-8") as f:
        data = json.load(f)
    return WarlockConfig(**data)
