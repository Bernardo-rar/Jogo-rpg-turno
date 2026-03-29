"""Testes do XP Calculator."""

from src.core.progression.xp_calculator import CombatXpInput, calculate_combat_xp
from src.core.progression.xp_reward_config import load_xp_reward_config


def _config():
    return load_xp_reward_config()


class TestCalculateCombatXp:

    def test_normal_t1_base(self) -> None:
        combat = CombatXpInput("normal", 1, rounds=8, party_deaths=1)
        assert calculate_combat_xp(combat, _config()) == 25

    def test_elite_t2_base(self) -> None:
        combat = CombatXpInput("elite", 2, rounds=8, party_deaths=1)
        assert calculate_combat_xp(combat, _config()) == 90

    def test_boss_t1_base(self) -> None:
        combat = CombatXpInput("boss", 1, rounds=8, party_deaths=1)
        assert calculate_combat_xp(combat, _config()) == 80

    def test_no_death_bonus(self) -> None:
        combat = CombatXpInput("normal", 1, rounds=8, party_deaths=0)
        # 25 * 1.10 = 27.5 → 27
        assert calculate_combat_xp(combat, _config()) == 27

    def test_fast_clear_bonus(self) -> None:
        combat = CombatXpInput("normal", 1, rounds=4, party_deaths=1)
        # 25 * 1.15 = 28.75 → 28
        assert calculate_combat_xp(combat, _config()) == 28

    def test_both_bonuses(self) -> None:
        combat = CombatXpInput("normal", 1, rounds=3, party_deaths=0)
        # 25 * 1.10 * 1.15 = 31.625 → 31
        assert calculate_combat_xp(combat, _config()) == 31

    def test_run_modifier_multiplier(self) -> None:
        combat = CombatXpInput("normal", 1, rounds=8, party_deaths=1, xp_run_mult=1.25)
        # 25 * 1.25 = 31.25 → 31
        assert calculate_combat_xp(combat, _config()) == 31

    def test_unknown_type_returns_zero(self) -> None:
        combat = CombatXpInput("unknown", 1, rounds=3, party_deaths=0)
        assert calculate_combat_xp(combat, _config()) == 0

    def test_elite_t1_no_death_fast(self) -> None:
        combat = CombatXpInput("elite", 1, rounds=5, party_deaths=0)
        # 50 * 1.10 * 1.15 = 63.25 → 63
        assert calculate_combat_xp(combat, _config()) == 63
