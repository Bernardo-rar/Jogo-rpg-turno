import pytest

from src.core.classes.paladin.glory_config import GloryConfig, load_glory_config


class TestGloryConfig:
    def test_is_frozen(self):
        config = GloryConfig(favor_cost=5, duration_turns=3, aura_boost_multiplier=2.0)
        with pytest.raises(AttributeError):
            config.favor_cost = 10

    def test_loads_from_json(self):
        config = load_glory_config()
        assert isinstance(config, GloryConfig)

    def test_favor_cost(self):
        config = load_glory_config()
        assert config.favor_cost == 5

    def test_duration_turns(self):
        config = load_glory_config()
        assert config.duration_turns == 3

    def test_aura_boost_multiplier(self):
        config = load_glory_config()
        assert config.aura_boost_multiplier == 2.0
