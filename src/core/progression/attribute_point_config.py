"""Configuracao de pontos de atributo ganhos por nivel."""

from __future__ import annotations

import json
from dataclasses import dataclass

from src.core._paths import resolve_data_path


@dataclass(frozen=True)
class LevelAttributePoints:
    """Pontos de atributo ganhos ao subir para um nivel especifico."""

    physical: int
    mental: int

    @property
    def total(self) -> int:
        return self.physical + self.mental


def _zero_points() -> LevelAttributePoints:
    return LevelAttributePoints(physical=0, mental=0)


def get_points_for_level(
    level: int,
    config: dict[int, LevelAttributePoints],
) -> LevelAttributePoints:
    """Retorna pontos de atributo para o nivel dado, ou zero se nao definido."""
    return config.get(level, _zero_points())


def load_attribute_points() -> dict[int, LevelAttributePoints]:
    """Carrega config de pontos do JSON em data/progression/attribute_points.json."""
    path = resolve_data_path("data/progression/attribute_points.json")
    with open(path) as f:
        raw = json.load(f)
    return {
        int(level): LevelAttributePoints(
            physical=data["physical"],
            mental=data["mental"],
        )
        for level, data in raw.items()
    }
