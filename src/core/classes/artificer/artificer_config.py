from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

ARTIFICER_CONFIG_DATA_PATH = "data/classes/artificer_config.json"


@dataclass(frozen=True)
class ArtificerConfig:
    """Configuracao do Artifice: passivas e mecanicas."""

    mana_regen_bonus: float
    magical_defense_bonus: float
    scroll_potentiation: float


def load_artificer_config(
    filepath: str = ARTIFICER_CONFIG_DATA_PATH,
) -> ArtificerConfig:
    """Carrega configuracao do Artifice do JSON."""
    with open(Path(filepath), encoding="utf-8") as f:
        data = json.load(f)
    return ArtificerConfig(**data)
