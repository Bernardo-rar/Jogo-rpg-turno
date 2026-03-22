"""Carrega EnemyTemplate a partir dos JSONs em data/dungeon/enemies/."""

from __future__ import annotations

import json
from pathlib import Path

from src.core._paths import resolve_data_path
from src.dungeon.enemies.enemy_template import EnemyTemplate

_TIER_DIR = "data/dungeon/enemies/tier{tier}"


def load_enemy_template(enemy_id: str, tier: int) -> EnemyTemplate:
    """Carrega um EnemyTemplate pelo id e tier."""
    path = _tier_path(tier) / f"{enemy_id}.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    return EnemyTemplate.from_dict(raw)


def load_tier_templates(tier: int) -> dict[str, EnemyTemplate]:
    """Carrega todos os EnemyTemplate de um tier."""
    folder = _tier_path(tier)
    result: dict[str, EnemyTemplate] = {}
    for path in sorted(folder.glob("*.json")):
        raw = json.loads(path.read_text(encoding="utf-8"))
        template = EnemyTemplate.from_dict(raw)
        result[template.enemy_id] = template
    return result


def _tier_path(tier: int) -> Path:
    return resolve_data_path(_TIER_DIR.format(tier=tier))
