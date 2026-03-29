"""Testes do loader de XP reward config."""

from src.core.progression.xp_reward_config import (
    XpRewardConfig,
    load_xp_reward_config,
)


class TestLoadXpRewardConfig:
    """Testes de carregamento do JSON."""

    def test_loads_from_json(self) -> None:
        config = load_xp_reward_config()
        assert isinstance(config, XpRewardConfig)

    def test_normal_t1_xp(self) -> None:
        config = load_xp_reward_config()
        assert config.base_xp("normal", 1) == 25

    def test_elite_t1_xp(self) -> None:
        config = load_xp_reward_config()
        assert config.base_xp("elite", 1) == 50

    def test_boss_t1_xp(self) -> None:
        config = load_xp_reward_config()
        assert config.base_xp("boss", 1) == 80

    def test_no_death_mult(self) -> None:
        config = load_xp_reward_config()
        assert config.bonuses.no_death_mult == 1.10

    def test_fast_clear_mult(self) -> None:
        config = load_xp_reward_config()
        assert config.bonuses.fast_clear_mult == 1.15

    def test_fast_clear_max_rounds(self) -> None:
        config = load_xp_reward_config()
        assert config.bonuses.fast_clear_max_rounds == 5

    def test_unknown_encounter_type_returns_zero(self) -> None:
        config = load_xp_reward_config()
        assert config.base_xp("unknown", 1) == 0

    def test_unknown_tier_returns_zero(self) -> None:
        config = load_xp_reward_config()
        assert config.base_xp("normal", 99) == 0
