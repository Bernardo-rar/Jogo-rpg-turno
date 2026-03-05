from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

FOCUS_DATA_PATH = "data/classes/ranger_focus.json"


@dataclass(frozen=True)
class PredatoryFocusConfig:
    """Configuracao do Foco Predatorio do Ranger."""

    max_stacks: int
    stacks_per_hit: int
    miss_loss_multiplier: float
    crit_chance_per_stack: float
    crit_damage_per_stack: float
    decay_per_turn: int
    atk_bonus_per_stack: float


def load_predatory_focus_config(
    filepath: str = FOCUS_DATA_PATH,
) -> PredatoryFocusConfig:
    """Carrega configuracao de foco predatorio do JSON."""
    with open(Path(filepath), encoding="utf-8") as f:
        data = json.load(f)
    return PredatoryFocusConfig(**data)
