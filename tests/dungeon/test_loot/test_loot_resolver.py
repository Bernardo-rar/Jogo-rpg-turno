"""Testes para o loot resolver (gold + drops combinados)."""

from __future__ import annotations

from random import Random

from src.dungeon.economy.gold_reward import CombatInfo
from src.dungeon.loot.loot_resolver import (
    LootResult,
    load_drop_tables,
    resolve_combat_loot,
)


class TestLoadDropTables:

    def test_loads_tier1_table(self) -> None:
        tables = load_drop_tables()
        assert "tier1" in tables

    def test_loads_tier1_elite_table(self) -> None:
        tables = load_drop_tables()
        assert "tier1_elite" in tables

    def test_loads_boss1_table(self) -> None:
        tables = load_drop_tables()
        assert "boss1" in tables

    def test_tier1_has_drop_count_range(self) -> None:
        tables = load_drop_tables()
        tier1 = tables["tier1"]
        assert tier1.min_drops >= 1
        assert tier1.max_drops >= tier1.min_drops


class TestLootResult:

    def test_frozen_dataclass(self) -> None:
        from src.dungeon.economy.gold_reward import GoldReward
        result = LootResult(
            gold=GoldReward(base=10, bonus=0, total=10),
            drops=(),
        )
        assert result.gold.total == 10
        assert len(result.drops) == 0


class TestResolveCombatLoot:

    def test_combat_loot_has_gold_and_drops(self) -> None:
        rng = Random(42)
        info = CombatInfo(enemy_count=3, tier=1)
        result = resolve_combat_loot(info, rng)
        assert result.gold.total > 0
        assert len(result.drops) >= 1

    def test_elite_loot_has_more_drops_than_normal(self) -> None:
        normal_info = CombatInfo(enemy_count=3, tier=1)
        elite_info = CombatInfo(
            enemy_count=3, tier=1, is_elite=True,
        )
        normal_drops_total = 0
        elite_drops_total = 0
        sample_size = 100
        for i in range(sample_size):
            rng = Random(i)
            normal = resolve_combat_loot(normal_info, rng)
            normal_drops_total += len(normal.drops)
        for i in range(sample_size):
            rng = Random(i)
            elite = resolve_combat_loot(elite_info, rng)
            elite_drops_total += len(elite.drops)
        assert elite_drops_total > normal_drops_total

    def test_boss_loot_has_more_drops(self) -> None:
        normal_info = CombatInfo(enemy_count=3, tier=1)
        boss_info = CombatInfo(
            enemy_count=1, tier=1, is_boss=True,
        )
        normal_drops_total = 0
        boss_drops_total = 0
        sample_size = 100
        for i in range(sample_size):
            rng = Random(i)
            normal = resolve_combat_loot(normal_info, rng)
            normal_drops_total += len(normal.drops)
        for i in range(sample_size):
            rng = Random(i)
            boss = resolve_combat_loot(boss_info, rng)
            boss_drops_total += len(boss.drops)
        assert boss_drops_total > normal_drops_total

    def test_drops_are_from_correct_pool(self) -> None:
        rng = Random(42)
        info = CombatInfo(enemy_count=2, tier=1)
        result = resolve_combat_loot(info, rng)
        tables = load_drop_tables()
        valid_ids = {
            e.item_id for e in tables["tier1"].table.drops
        }
        for drop in result.drops:
            assert drop.item_id in valid_ids
