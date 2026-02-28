from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path

STANCE_DATA_PATH = "data/classes/fighter_stances.json"


class Stance(Enum):
    """Estancias do Guerreiro: modificam ataque e defesa."""

    NORMAL = auto()
    OFFENSIVE = auto()
    DEFENSIVE = auto()


@dataclass(frozen=True)
class StanceModifier:
    """Multiplicadores de ataque e defesa por estancia."""

    atk_multiplier: float
    def_multiplier: float


def load_stance_modifiers(
    filepath: str = STANCE_DATA_PATH,
) -> dict[Stance, StanceModifier]:
    """Carrega modificadores de estancia do JSON."""
    with open(Path(filepath), encoding="utf-8") as f:
        data = json.load(f)
    return {
        Stance[name]: StanceModifier(**values)
        for name, values in data.items()
    }
