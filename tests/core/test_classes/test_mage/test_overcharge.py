import pytest

from src.core.classes.mage.overcharge import OverchargeConfig, load_overcharge_config


class TestOverchargeConfig:
    def test_is_frozen(self):
        config = OverchargeConfig(atk_multiplier=1.5, mana_cost_per_turn=30)
        with pytest.raises(AttributeError):
            config.atk_multiplier = 2.0

    def test_atk_multiplier_stored(self):
        config = OverchargeConfig(atk_multiplier=1.5, mana_cost_per_turn=30)
        assert config.atk_multiplier == 1.5

    def test_mana_cost_stored(self):
        config = OverchargeConfig(atk_multiplier=1.5, mana_cost_per_turn=30)
        assert config.mana_cost_per_turn == 30


class TestLoadOverchargeConfig:
    def test_loads_from_json(self):
        config = load_overcharge_config("data/classes/mage_overcharge.json")
        assert isinstance(config, OverchargeConfig)

    def test_atk_multiplier_value(self):
        config = load_overcharge_config("data/classes/mage_overcharge.json")
        assert config.atk_multiplier == 1.5

    def test_mana_cost_value(self):
        config = load_overcharge_config("data/classes/mage_overcharge.json")
        assert config.mana_cost_per_turn == 30
