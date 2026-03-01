from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path

DIVINITY_DATA_PATH = "data/classes/cleric_divinities.json"


class Divinity(Enum):
    """Divindades do Clerigo: definem elemento e bonus de cura."""

    FIRE = auto()
    WATER = auto()
    ICE = auto()
    EARTH = auto()
    LIGHTNING = auto()
    HOLY = auto()
    CHAOS = auto()


@dataclass(frozen=True)
class DivinityConfig:
    """Configuracao de uma divindade: bonus de cura."""

    healing_bonus: float


def load_divinity_configs(
    filepath: str = DIVINITY_DATA_PATH,
) -> dict[Divinity, DivinityConfig]:
    """Carrega configuracoes de divindade do JSON."""
    with open(Path(filepath), encoding="utf-8") as f:
        data = json.load(f)
    return {
        Divinity[name]: DivinityConfig(**values)
        for name, values in data.items()
    }
