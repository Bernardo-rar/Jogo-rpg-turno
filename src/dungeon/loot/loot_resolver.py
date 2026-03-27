"""Loot resolver — combina gold + drops em um unico resultado."""

from __future__ import annotations

import json
from dataclasses import dataclass
from random import Random

from src.core._paths import resolve_data_path
from src.dungeon.economy.gold_reward import (
    CombatInfo,
    GoldReward,
    calculate_combat_gold,
)
from src.dungeon.loot.drop_table import (
    DropEntry,
    DropTable,
    LootDrop,
    resolve_drops,
)

_DROP_TABLES_FILE = "data/dungeon/loot/drop_tables.json"


@dataclass(frozen=True)
class DropTableConfig:
    """Config de uma drop table com range de quantidade."""

    table: DropTable
    min_drops: int
    max_drops: int


@dataclass(frozen=True)
class LootResult:
    """Resultado completo de loot pos-combate."""

    gold: GoldReward
    drops: tuple[LootDrop, ...]


def _parse_drop_entry(raw: dict) -> DropEntry:
    """Converte dict JSON em DropEntry."""
    return DropEntry(
        item_type=raw["item_type"],
        item_id=raw["item_id"],
        weight=raw["weight"],
        quantity=raw.get("quantity", 1),
    )


def _parse_table_config(raw: dict) -> DropTableConfig:
    """Converte dict JSON em DropTableConfig."""
    entries = tuple(
        _parse_drop_entry(e) for e in raw["pool"]
    )
    count = raw["drop_count"]
    return DropTableConfig(
        table=DropTable(drops=entries),
        min_drops=count["min"],
        max_drops=count["max"],
    )


def load_drop_tables() -> dict[str, DropTableConfig]:
    """Carrega todas as drop tables do JSON."""
    path = resolve_data_path(_DROP_TABLES_FILE)
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {
        key: _parse_table_config(data)
        for key, data in raw.items()
    }


def _select_table_key(info: CombatInfo) -> str:
    """Determina qual drop table usar."""
    if info.is_boss:
        return f"boss{info.tier}"
    if info.is_elite:
        return f"tier{info.tier}_elite"
    return f"tier{info.tier}"


def _resolve_table_drops(
    config: DropTableConfig, rng: Random,
) -> tuple[LootDrop, ...]:
    """Rola quantidade e resolve drops de uma tabela."""
    count = rng.randint(config.min_drops, config.max_drops)
    return tuple(resolve_drops(config.table, count, rng))


def resolve_combat_loot(
    info: CombatInfo,
    rng: Random,
    tables: dict[str, DropTableConfig] | None = None,
) -> LootResult:
    """Resolve gold + drops de um combate."""
    gold = calculate_combat_gold(info, rng)
    if tables is None:
        tables = load_drop_tables()
    table_key = _select_table_key(info)
    table_config = tables[table_key]
    drops = _resolve_table_drops(table_config, rng)
    return LootResult(gold=gold, drops=drops)
