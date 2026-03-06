from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path

FAMILIAR_DATA_PATH = "data/classes/warlock_familiars.json"


class FamiliarType(Enum):
    """Tipos de familiar do Warlock."""

    IMP = auto()
    RAVEN = auto()
    SPIDER = auto()
    SHADOW_CAT = auto()


@dataclass(frozen=True)
class FamiliarConfig:
    """Configuracao de um familiar: stat bonus passivo."""

    stat_bonus_type: str
    stat_bonus_pct: float


def load_familiar_configs(
    filepath: str = FAMILIAR_DATA_PATH,
) -> dict[FamiliarType, FamiliarConfig]:
    """Carrega configuracoes de familiares do JSON."""
    with open(Path(filepath), encoding="utf-8") as f:
        data = json.load(f)
    return {
        FamiliarType[name]: FamiliarConfig(**values)
        for name, values in data.items()
    }
