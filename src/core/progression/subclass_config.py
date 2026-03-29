"""Subclass config — define subclasses disponiveis por classe."""

from __future__ import annotations

import json
from dataclasses import dataclass

from src.core._paths import resolve_data_path

_CONFIG_FILE = "data/subclasses/subclass_registry.json"


@dataclass(frozen=True)
class StatBonus:
    """Bonus percentual de stat da subclass."""

    stat: str
    percent: float


@dataclass(frozen=True)
class SubclassOption:
    """Uma opcao de subclass para escolha no level 3."""

    subclass_id: str
    name: str
    description: str
    skill_ids: tuple[str, ...]
    passive_bonuses: tuple[StatBonus, ...]


@dataclass(frozen=True)
class ClassSubclasses:
    """Par de subclasses de uma classe."""

    class_id: str
    option_a: SubclassOption
    option_b: SubclassOption


def load_subclass_registry() -> dict[str, ClassSubclasses]:
    """Carrega registry de subclasses do JSON."""
    path = resolve_data_path(_CONFIG_FILE)
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {
        class_id: _parse_class(class_id, data)
        for class_id, data in raw.items()
    }


def _parse_class(class_id: str, data: dict) -> ClassSubclasses:
    return ClassSubclasses(
        class_id=class_id,
        option_a=_parse_option(data["option_a"]),
        option_b=_parse_option(data["option_b"]),
    )


def _parse_option(data: dict) -> SubclassOption:
    bonuses = tuple(
        StatBonus(stat=b["stat"], percent=b["percent"])
        for b in data.get("passive_bonuses", [])
    )
    return SubclassOption(
        subclass_id=data["subclass_id"],
        name=data["name"],
        description=data["description"],
        skill_ids=tuple(data.get("skill_ids", [])),
        passive_bonuses=bonuses,
    )
