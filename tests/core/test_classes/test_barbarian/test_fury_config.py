import pytest

from src.core.classes.barbarian.fury_config import FuryConfig, load_fury_config


class TestFuryConfig:
    def test_load_returns_fury_config(self):
        config = load_fury_config()
        assert isinstance(config, FuryConfig)

    def test_fury_max_ratio(self):
        config = load_fury_config()
        assert config.fury_max_ratio == 0.25

    def test_fury_on_damage_ratio(self):
        config = load_fury_config()
        assert config.fury_on_damage_ratio == 0.10

    def test_fury_on_basic_attack(self):
        config = load_fury_config()
        assert config.fury_on_basic_attack == 10

    def test_fury_decay_per_turn(self):
        config = load_fury_config()
        assert config.fury_decay_per_turn == 3

    def test_atk_bonus_at_max_fury(self):
        config = load_fury_config()
        assert config.atk_bonus_at_max_fury == 0.30

    def test_regen_bonus_at_max_fury(self):
        config = load_fury_config()
        assert config.regen_bonus_at_max_fury == 0.20

    def test_missing_hp_atk_bonus(self):
        config = load_fury_config()
        assert config.missing_hp_atk_bonus == 0.25

    def test_is_frozen(self):
        config = load_fury_config()
        with pytest.raises(AttributeError):
            config.fury_max_ratio = 0.5  # type: ignore[misc]
