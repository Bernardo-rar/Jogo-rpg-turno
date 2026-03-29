"""Distribuicao automatica de pontos baseada em prioridade da classe."""

from __future__ import annotations

import json

from src.core._paths import resolve_data_path
from src.core.attributes.attribute_types import AttributeType

_CONFIG_FILE = "data/progression/recommended_attributes.json"


def load_recommended() -> dict[str, RecommendedConfig]:
    """Carrega prioridades recomendadas por classe."""
    path = resolve_data_path(_CONFIG_FILE)
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {
        class_id: _parse_config(data)
        for class_id, data in raw.items()
    }


class RecommendedConfig:
    """Prioridade de atributos para uma classe."""

    def __init__(
        self,
        physical: list[AttributeType],
        mental: list[AttributeType],
    ) -> None:
        self.physical = physical
        self.mental = mental


def _parse_config(data: dict) -> RecommendedConfig:
    return RecommendedConfig(
        physical=[AttributeType[n] for n in data["physical"]],
        mental=[AttributeType[n] for n in data["mental"]],
    )


def auto_distribute(
    points: int, priority: list[AttributeType],
) -> dict[AttributeType, int]:
    """Distribui pontos na ordem de prioridade.

    Primeiro atributo recebe ceil(pontos/len), segundo o proximo, etc.
    Distribui round-robin na ordem de prioridade.
    """
    dist: dict[AttributeType, int] = {a: 0 for a in priority}
    remaining = points
    idx = 0
    while remaining > 0:
        attr = priority[idx % len(priority)]
        dist[attr] += 1
        remaining -= 1
        idx += 1
    return dist
