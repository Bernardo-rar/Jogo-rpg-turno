from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

GLORY_DATA_PATH = "data/classes/paladin_glory.json"


@dataclass(frozen=True)
class GloryConfig:
    """Configuracao do Glimpse of Glory."""

    favor_cost: int
    duration_turns: int
    aura_boost_multiplier: float


def load_glory_config(
    filepath: str = GLORY_DATA_PATH,
) -> GloryConfig:
    """Carrega configuracao de Glory do JSON."""
    with open(Path(filepath), encoding="utf-8") as f:
        data = json.load(f)
    return GloryConfig(**data)
