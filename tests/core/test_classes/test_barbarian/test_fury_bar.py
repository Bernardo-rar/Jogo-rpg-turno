import pytest

from src.core.classes.barbarian.fury_bar import FuryBar


class TestFuryBarCreation:
    def test_starts_at_zero(self):
        bar = FuryBar(max_fury=100)
        assert bar.current == 0

    def test_max_fury(self):
        bar = FuryBar(max_fury=100)
        assert bar.max_fury == 100

    def test_fury_ratio_at_zero(self):
        bar = FuryBar(max_fury=100)
        assert bar.fury_ratio == 0.0

    def test_fury_ratio_zero_max_returns_zero(self):
        bar = FuryBar(max_fury=0)
        assert bar.fury_ratio == 0.0


class TestFuryBarGain:
    def test_gain_increases_current(self):
        bar = FuryBar(max_fury=100)
        gained = bar.gain(10)
        assert bar.current == 10
        assert gained == 10

    def test_gain_capped_at_max(self):
        bar = FuryBar(max_fury=50)
        gained = bar.gain(80)
        assert bar.current == 50
        assert gained == 50

    def test_gain_partial_overflow(self):
        bar = FuryBar(max_fury=100)
        bar.gain(90)
        gained = bar.gain(20)
        assert bar.current == 100
        assert gained == 10

    def test_fury_ratio_at_half(self):
        bar = FuryBar(max_fury=100)
        bar.gain(50)
        assert bar.fury_ratio == 0.5

    def test_fury_ratio_at_max(self):
        bar = FuryBar(max_fury=100)
        bar.gain(100)
        assert bar.fury_ratio == 1.0


class TestFuryBarSpend:
    def test_spend_reduces_current(self):
        bar = FuryBar(max_fury=100)
        bar.gain(50)
        result = bar.spend(20)
        assert result is True
        assert bar.current == 30

    def test_spend_insufficient_returns_false(self):
        bar = FuryBar(max_fury=100)
        bar.gain(10)
        result = bar.spend(20)
        assert result is False
        assert bar.current == 10

    def test_spend_exact_amount(self):
        bar = FuryBar(max_fury=100)
        bar.gain(30)
        result = bar.spend(30)
        assert result is True
        assert bar.current == 0


class TestFuryBarDecay:
    def test_decay_reduces_current(self):
        bar = FuryBar(max_fury=100)
        bar.gain(50)
        decayed = bar.decay(10)
        assert bar.current == 40
        assert decayed == 10

    def test_decay_does_not_go_below_zero(self):
        bar = FuryBar(max_fury=100)
        bar.gain(5)
        decayed = bar.decay(10)
        assert bar.current == 0
        assert decayed == 5

    def test_decay_from_zero(self):
        bar = FuryBar(max_fury=100)
        decayed = bar.decay(10)
        assert bar.current == 0
        assert decayed == 0


class TestFuryBarUpdateMax:
    def test_update_max_increases(self):
        bar = FuryBar(max_fury=100)
        bar.update_max(200)
        assert bar.max_fury == 200

    def test_update_max_clamps_current(self):
        bar = FuryBar(max_fury=100)
        bar.gain(100)
        bar.update_max(50)
        assert bar.max_fury == 50
        assert bar.current == 50
