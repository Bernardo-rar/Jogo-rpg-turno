from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path

FIELD_CONDITION_DATA_PATH = "data/classes/druid_fields.json"


class FieldConditionType(Enum):
    """Tipos de condicao de campo do Druida."""

    SNOW = auto()
    RAIN = auto()
    SANDSTORM = auto()
    FOG = auto()


@dataclass(frozen=True)
class FieldConditionConfig:
    """Configuracao de uma condicao de campo."""

    element_resistance: str
    element_vulnerability: str
    speed_modifier: float
    default_duration: int


def load_field_condition_configs(
    filepath: str = FIELD_CONDITION_DATA_PATH,
) -> dict[FieldConditionType, FieldConditionConfig]:
    """Carrega configuracoes de condicoes de campo do JSON."""
    with open(Path(filepath), encoding="utf-8") as f:
        data = json.load(f)
    return {
        FieldConditionType[name]: FieldConditionConfig(**values)
        for name, values in data.items()
    }
