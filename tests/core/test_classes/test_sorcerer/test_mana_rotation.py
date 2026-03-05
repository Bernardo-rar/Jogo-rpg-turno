import pytest

from src.core.classes.sorcerer.mana_rotation import (
    ManaRotation,
    ManaRotationConfig,
    load_mana_rotation_config,
)


class TestManaRotationConfig:
    def test_load_from_json(self):
        config = load_mana_rotation_config()
        assert isinstance(config, ManaRotationConfig)

    def test_config_has_gain_ratio(self):
        config = load_mana_rotation_config()
        assert config.gain_ratio > 0.0

    def test_config_has_decay_per_turn(self):
        config = load_mana_rotation_config()
        assert config.decay_per_turn > 0

    def test_config_has_max_ratio(self):
        config = load_mana_rotation_config()
        assert config.max_ratio > 0.0

    def test_config_is_frozen(self):
        config = load_mana_rotation_config()
        with pytest.raises(AttributeError):
            config.gain_ratio = 0.5


class TestManaRotationCreation:
    def test_starts_at_zero(self):
        rotation = ManaRotation(max_mana=100)
        assert rotation.current == 0

    def test_max_stored(self):
        rotation = ManaRotation(max_mana=100)
        assert rotation.max_mana == 100

    def test_ratio_at_zero(self):
        rotation = ManaRotation(max_mana=100)
        assert rotation.ratio == 0.0

    def test_ratio_zero_max_returns_zero(self):
        rotation = ManaRotation(max_mana=0)
        assert rotation.ratio == 0.0


class TestManaRotationGain:
    def test_gain_increases_current(self):
        rotation = ManaRotation(max_mana=100)
        gained = rotation.gain(10)
        assert rotation.current == 10
        assert gained == 10

    def test_gain_capped_at_max(self):
        rotation = ManaRotation(max_mana=50)
        gained = rotation.gain(80)
        assert rotation.current == 50
        assert gained == 50

    def test_gain_partial_overflow(self):
        rotation = ManaRotation(max_mana=100)
        rotation.gain(90)
        gained = rotation.gain(20)
        assert rotation.current == 100
        assert gained == 10

    def test_ratio_at_half(self):
        rotation = ManaRotation(max_mana=100)
        rotation.gain(50)
        assert rotation.ratio == 0.5


class TestManaRotationDecay:
    def test_decay_reduces_current(self):
        rotation = ManaRotation(max_mana=100)
        rotation.gain(50)
        decayed = rotation.decay(10)
        assert rotation.current == 40
        assert decayed == 10

    def test_decay_does_not_go_below_zero(self):
        rotation = ManaRotation(max_mana=100)
        rotation.gain(5)
        decayed = rotation.decay(10)
        assert rotation.current == 0
        assert decayed == 5

    def test_decay_from_zero(self):
        rotation = ManaRotation(max_mana=100)
        decayed = rotation.decay(10)
        assert rotation.current == 0
        assert decayed == 0


class TestManaRotationUpdateMax:
    def test_update_max_increases(self):
        rotation = ManaRotation(max_mana=100)
        rotation.update_max(200)
        assert rotation.max_mana == 200

    def test_update_max_clamps_current(self):
        rotation = ManaRotation(max_mana=100)
        rotation.gain(100)
        rotation.update_max(50)
        assert rotation.max_mana == 50
        assert rotation.current == 50
