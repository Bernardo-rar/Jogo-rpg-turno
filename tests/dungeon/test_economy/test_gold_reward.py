"""Testes para o sistema de recompensa de gold."""

from __future__ import annotations

from random import Random

from src.dungeon.economy.gold_reward import (
    CombatInfo,
    GoldReward,
    calculate_combat_gold,
    load_gold_config,
)


class TestLoadGoldConfig:

    def test_loads_config_from_json(self) -> None:
        config = load_gold_config()
        assert config.gold_per_enemy is not None
        assert config.elite_multiplier == 1.5

    def test_config_has_tier1_range(self) -> None:
        config = load_gold_config()
        tier1 = config.gold_per_enemy[1]
        assert tier1.min_gold == 3
        assert tier1.max_gold == 8

    def test_config_has_boss_gold(self) -> None:
        config = load_gold_config()
        assert config.boss_gold[1] == 100
        assert config.boss_gold[2] == 200
        assert config.boss_gold[3] == 300


class TestGoldReward:

    def test_gold_reward_total_equals_base_plus_bonus(self) -> None:
        reward = GoldReward(base=10, bonus=5, total=15)
        assert reward.total == reward.base + reward.bonus


class TestCalculateCombatGold:

    def test_tier1_gold_in_range(self) -> None:
        rng = Random(42)
        info = CombatInfo(enemy_count=1, tier=1)
        reward = calculate_combat_gold(info, rng)
        assert 3 <= reward.total <= 8

    def test_elite_multiplier_applied(self) -> None:
        rng = Random(42)
        normal_info = CombatInfo(enemy_count=3, tier=1)
        normal = calculate_combat_gold(normal_info, rng)
        rng = Random(42)
        elite_info = CombatInfo(
            enemy_count=3, tier=1, is_elite=True,
        )
        elite = calculate_combat_gold(elite_info, rng)
        assert elite.total > normal.total

    def test_boss_gold_fixed(self) -> None:
        rng = Random(42)
        info = CombatInfo(
            enemy_count=1, tier=1, is_boss=True,
        )
        reward = calculate_combat_gold(info, rng)
        assert reward.total == 100

    def test_boss_gold_tier2(self) -> None:
        rng = Random(42)
        info = CombatInfo(
            enemy_count=1, tier=2, is_boss=True,
        )
        reward = calculate_combat_gold(info, rng)
        assert reward.total == 200

    def test_gold_scales_with_enemy_count(self) -> None:
        rng1 = Random(42)
        one_info = CombatInfo(enemy_count=1, tier=1)
        one_enemy = calculate_combat_gold(one_info, rng1)
        rng2 = Random(42)
        three_info = CombatInfo(enemy_count=3, tier=1)
        three_enemies = calculate_combat_gold(three_info, rng2)
        assert three_enemies.total > one_enemy.total

    def test_tier2_gold_higher_than_tier1(self) -> None:
        rng1 = Random(42)
        t1_info = CombatInfo(enemy_count=3, tier=1)
        tier1 = calculate_combat_gold(t1_info, rng1)
        rng2 = Random(42)
        t2_info = CombatInfo(enemy_count=3, tier=2)
        tier2 = calculate_combat_gold(t2_info, rng2)
        assert tier2.total > tier1.total
