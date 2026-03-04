from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path

AURA_DATA_PATH = "data/classes/paladin_auras.json"


class Aura(Enum):
    """Auras do Paladino: buffs persistentes para si e aliados."""

    NONE = auto()
    PROTECTION = auto()
    ATTACK = auto()
    VITALITY = auto()


@dataclass(frozen=True)
class AuraModifier:
    """Multiplicadores de defesa, ataque e regen por aura."""

    def_multiplier: float
    atk_multiplier: float
    regen_multiplier: float


def load_aura_modifiers(
    filepath: str = AURA_DATA_PATH,
) -> dict[Aura, AuraModifier]:
    """Carrega modificadores de aura do JSON."""
    with open(Path(filepath), encoding="utf-8") as f:
        data = json.load(f)
    return {
        Aura[name]: AuraModifier(**values)
        for name, values in data.items()
    }
