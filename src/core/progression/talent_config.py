"""Talent config — define talentos disponiveis."""

from __future__ import annotations

import json
from dataclasses import dataclass

from src.core._paths import resolve_data_path

_CONFIG_FILE = "data/progression/talents.json"

TALENT_LEVELS = frozenset({5, 7, 9})


@dataclass(frozen=True)
class TalentEffect:
    """Bonus de stat de um talento."""

    stat: str
    percent: float


@dataclass(frozen=True)
class Talent:
    """Definicao de um talento."""

    talent_id: str
    name: str
    category: str
    description: str
    allowed_classes: tuple[str, ...]
    effects: tuple[TalentEffect, ...]

    def is_available_for(self, class_id: str) -> bool:
        """True se o talento esta disponivel pra essa classe."""
        if not self.allowed_classes:
            return True
        return class_id in self.allowed_classes


def load_talents() -> dict[str, Talent]:
    """Carrega todos os talentos do JSON."""
    path = resolve_data_path(_CONFIG_FILE)
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {
        tid: _parse_talent(tid, data)
        for tid, data in raw.items()
    }


def _parse_talent(tid: str, data: dict) -> Talent:
    effects = tuple(
        TalentEffect(stat=e["stat"], percent=e["percent"])
        for e in data.get("effects", [])
    )
    return Talent(
        talent_id=tid,
        name=data["name"],
        category=data["category"],
        description=data["description"],
        allowed_classes=tuple(data.get("allowed_classes", [])),
        effects=effects,
    )
