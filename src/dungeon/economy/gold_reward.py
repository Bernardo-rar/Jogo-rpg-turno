"""Calcula recompensas de gold pos-combate."""

from __future__ import annotations

import json
from dataclasses import dataclass
from random import Random

from src.core._paths import resolve_data_path

_CONFIG_FILE = "data/dungeon/economy/gold_config.json"


@dataclass(frozen=True)
class GoldRange:
    """Faixa de gold por inimigo em um tier."""

    min_gold: int
    max_gold: int


@dataclass(frozen=True)
class GoldConfig:
    """Configuracao de gold carregada do JSON."""

    gold_per_enemy: dict[int, GoldRange]
    elite_multiplier: float
    boss_gold: dict[int, int]


@dataclass(frozen=True)
class GoldReward:
    """Resultado do calculo de gold."""

    base: int
    bonus: int
    total: int


@dataclass(frozen=True)
class CombatInfo:
    """Contexto de combate para calculo de recompensas."""

    enemy_count: int
    tier: int
    is_elite: bool = False
    is_boss: bool = False


def load_gold_config() -> GoldConfig:
    """Carrega configuracao de gold do JSON."""
    path = resolve_data_path(_CONFIG_FILE)
    raw = json.loads(path.read_text(encoding="utf-8"))
    gold_per_enemy = {
        int(k): GoldRange(min_gold=v["min"], max_gold=v["max"])
        for k, v in raw["gold_per_enemy"].items()
    }
    boss_gold = {int(k): v for k, v in raw["boss_gold"].items()}
    return GoldConfig(
        gold_per_enemy=gold_per_enemy,
        elite_multiplier=raw["elite_multiplier"],
        boss_gold=boss_gold,
    )


def _roll_enemy_gold(
    gold_range: GoldRange, enemy_count: int, rng: Random,
) -> int:
    """Rola gold por inimigo e soma."""
    return sum(
        rng.randint(gold_range.min_gold, gold_range.max_gold)
        for _ in range(enemy_count)
    )


def _calculate_elite_bonus(base: int, multiplier: float) -> int:
    """Calcula bonus de elite sobre o base."""
    return int(base * multiplier) - base


def calculate_combat_gold(
    info: CombatInfo, rng: Random, config: GoldConfig | None = None,
) -> GoldReward:
    """Calcula gold total de um combate.

    Boss: gold fixo por tier (ignora enemy_count).
    Elite: gold normal * elite_multiplier.
    Normal: soma de rolls por inimigo.
    """
    if config is None:
        config = load_gold_config()
    if info.is_boss:
        total = config.boss_gold[info.tier]
        return GoldReward(base=total, bonus=0, total=total)
    gold_range = config.gold_per_enemy[info.tier]
    base = _roll_enemy_gold(gold_range, info.enemy_count, rng)
    bonus = 0
    if info.is_elite:
        bonus = _calculate_elite_bonus(base, config.elite_multiplier)
    return GoldReward(base=base, bonus=bonus, total=base + bonus)
