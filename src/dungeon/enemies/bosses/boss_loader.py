"""Loader de boss templates a partir de JSONs."""

from __future__ import annotations

import json

from src.core._paths import resolve_data_path
from src.dungeon.enemies.bosses.boss_template import BossTemplate

_BOSS_DIR = "data/dungeon/enemies/bosses"
_BOSS_IDS = ("goblin_king", "ancient_golem", "lich_lord")


def load_boss_template(boss_id: str) -> BossTemplate:
    """Carrega um boss template por ID."""
    path = resolve_data_path(f"{_BOSS_DIR}/{boss_id}.json")
    raw = json.loads(path.read_text(encoding="utf-8"))
    return BossTemplate.from_dict(raw)


def load_all_bosses() -> dict[str, BossTemplate]:
    """Carrega todos os boss templates conhecidos."""
    return {bid: load_boss_template(bid) for bid in _BOSS_IDS}
