import pytest

from src.core.classes.sorcerer.overcharged_config import (
    OverchargedConfig,
    load_overcharged_config,
)


class TestOverchargedConfig:
    def test_load_from_json(self):
        config = load_overcharged_config()
        assert isinstance(config, OverchargedConfig)

    def test_config_has_atk_multiplier(self):
        config = load_overcharged_config()
        assert config.atk_multiplier > 1.0

    def test_config_has_mana_cost_per_turn(self):
        config = load_overcharged_config()
        assert config.mana_cost_per_turn > 0

    def test_config_has_self_damage_pct(self):
        config = load_overcharged_config()
        assert 0.0 < config.self_damage_pct < 1.0

    def test_config_has_metamagic_mana_cost(self):
        config = load_overcharged_config()
        assert config.metamagic_mana_cost > 0

    def test_config_has_born_of_magic_bonus(self):
        config = load_overcharged_config()
        assert config.born_of_magic_bonus > 0.0

    def test_config_is_frozen(self):
        config = load_overcharged_config()
        with pytest.raises(AttributeError):
            config.atk_multiplier = 2.0
