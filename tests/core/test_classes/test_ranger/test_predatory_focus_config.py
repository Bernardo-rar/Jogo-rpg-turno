import pytest

from src.core.classes.ranger.predatory_focus_config import (
    PredatoryFocusConfig,
    load_predatory_focus_config,
)


class TestPredatoryFocusConfig:
    def test_is_frozen(self):
        config = PredatoryFocusConfig(
            max_stacks=20,
            stacks_per_hit=2,
            miss_loss_multiplier=2.0,
            crit_chance_per_stack=0.02,
            crit_damage_per_stack=0.05,
            decay_per_turn=1,
            atk_bonus_per_stack=0.005,
        )
        with pytest.raises(AttributeError):
            config.max_stacks = 10

    def test_loads_from_json(self):
        config = load_predatory_focus_config()
        assert isinstance(config, PredatoryFocusConfig)

    def test_max_stacks(self):
        config = load_predatory_focus_config()
        assert config.max_stacks == 20

    def test_stacks_per_hit(self):
        config = load_predatory_focus_config()
        assert config.stacks_per_hit == 2

    def test_miss_loss_multiplier(self):
        config = load_predatory_focus_config()
        assert config.miss_loss_multiplier == 2.0

    def test_crit_chance_per_stack(self):
        config = load_predatory_focus_config()
        assert config.crit_chance_per_stack == 0.02

    def test_crit_damage_per_stack(self):
        config = load_predatory_focus_config()
        assert config.crit_damage_per_stack == 0.05

    def test_decay_per_turn(self):
        config = load_predatory_focus_config()
        assert config.decay_per_turn == 1

    def test_atk_bonus_per_stack(self):
        config = load_predatory_focus_config()
        assert config.atk_bonus_per_stack == 0.005
