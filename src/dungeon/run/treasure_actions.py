"""Treasure actions -- resolve recompensas de salas de tesouro."""

from __future__ import annotations

import json
from dataclasses import dataclass
from random import Random
from typing import TYPE_CHECKING

from src.core._paths import resolve_data_path
from src.dungeon.loot.drop_table import (
    DropEntry,
    DropTable,
    LootDrop,
    resolve_drops,
)

if TYPE_CHECKING:
    from src.dungeon.run.run_state import RunState

_TREASURE_FILE = "data/dungeon/treasure/treasure_tables.json"


@dataclass(frozen=True)
class TreasureResult:
    """Resultado de abrir um bau de tesouro."""

    gold_earned: int
    drops: tuple[LootDrop, ...]


def _load_treasure_table(tier: int = 1) -> dict:
    """Carrega config de tesouro do JSON."""
    path = resolve_data_path(_TREASURE_FILE)
    raw = json.loads(path.read_text(encoding="utf-8"))
    return raw[f"tier{tier}"]


def _roll_gold(config: dict, rng: Random) -> int:
    """Rola gold dentro do range configurado."""
    gold_cfg = config["gold"]
    return rng.randint(gold_cfg["min"], gold_cfg["max"])


def _build_drop_table(pool: list[dict]) -> DropTable:
    """Constroi DropTable a partir do pool JSON."""
    entries = tuple(
        DropEntry(
            item_type=e["item_type"],
            item_id=e["item_id"],
            weight=e["weight"],
            quantity=e.get("quantity", 1),
        )
        for e in pool
    )
    return DropTable(drops=entries)


def _roll_drops(config: dict, rng: Random) -> tuple[LootDrop, ...]:
    """Resolve drops do tesouro."""
    count_cfg = config["drop_count"]
    count = rng.randint(count_cfg["min"], count_cfg["max"])
    table = _build_drop_table(config["pool"])
    return tuple(resolve_drops(table, count, rng))


def resolve_treasure(
    run_state: RunState,
    rng: Random,
    tier: int = 1,
) -> TreasureResult:
    """Resolve tesouro: rola gold e drops, atualiza state."""
    config = _load_treasure_table(tier)
    gold = _roll_gold(config, rng)
    drops = _roll_drops(config, rng)
    run_state.gold += gold
    run_state.pending_loot.extend(drops)
    return TreasureResult(gold_earned=gold, drops=drops)
