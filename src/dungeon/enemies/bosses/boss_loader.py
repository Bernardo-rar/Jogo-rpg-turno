"""Loader de boss templates a partir de JSONs."""

from __future__ import annotations

import json
from pathlib import Path

from src.core._paths import resolve_data_path
from src.dungeon.enemies.bosses.boss_template import BossTemplate

_BOSS_DIR = "data/dungeon/enemies/bosses"


def load_boss_template(boss_id: str) -> BossTemplate:
    """Carrega um boss template por ID."""
    path = resolve_data_path(f"{_BOSS_DIR}/{boss_id}.json")
    raw = json.loads(path.read_text(encoding="utf-8"))
    return BossTemplate.from_dict(raw)


def load_all_bosses() -> dict[str, BossTemplate]:
    """Carrega todos os boss templates da pasta."""
    folder = resolve_data_path(_BOSS_DIR)
    result: dict[str, BossTemplate] = {}
    for path in sorted(Path(folder).glob("*.json")):
        raw = json.loads(path.read_text(encoding="utf-8"))
        template = BossTemplate.from_dict(raw)
        result[template.enemy_id] = template
    return result
