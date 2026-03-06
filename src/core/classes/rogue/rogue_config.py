from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

ROGUE_CONFIG_DATA_PATH = "data/classes/rogue_config.json"


@dataclass(frozen=True)
class RogueConfig:
    """Configuracao do Ladino: passivas e mecanicas."""

    crit_bonus_per_dex: float
    poison_damage_bonus: float
    speed_bonus_pct: float
    extra_skill_slots: int
    crit_speed_boost_pct: float
    crit_speed_boost_duration: int


def load_rogue_config(
    filepath: str = ROGUE_CONFIG_DATA_PATH,
) -> RogueConfig:
    """Carrega configuracao do Ladino do JSON."""
    with open(Path(filepath), encoding="utf-8") as f:
        data = json.load(f)
    return RogueConfig(**data)
