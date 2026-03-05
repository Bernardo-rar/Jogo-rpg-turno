import pytest

from src.core.classes.ranger.predatory_focus import PredatoryFocus


class TestPredatoryFocusInit:
    def test_starts_at_zero(self):
        focus = PredatoryFocus(max_stacks=20)
        assert focus.current == 0

    def test_max_stacks(self):
        focus = PredatoryFocus(max_stacks=20)
        assert focus.max_stacks == 20

    def test_focus_ratio_zero_when_empty(self):
        focus = PredatoryFocus(max_stacks=20)
        assert focus.focus_ratio == 0.0


class TestPredatoryFocusGain:
    def test_gain_stacks(self):
        focus = PredatoryFocus(max_stacks=20)
        gained = focus.gain(2)
        assert gained == 2
        assert focus.current == 2

    def test_gain_capped_at_max(self):
        focus = PredatoryFocus(max_stacks=20)
        focus.gain(18)
        gained = focus.gain(5)
        assert gained == 2
        assert focus.current == 20

    def test_gain_at_max_returns_zero(self):
        focus = PredatoryFocus(max_stacks=20)
        focus.gain(20)
        gained = focus.gain(3)
        assert gained == 0

    def test_focus_ratio_at_max(self):
        focus = PredatoryFocus(max_stacks=20)
        focus.gain(20)
        assert focus.focus_ratio == 1.0

    def test_focus_ratio_half(self):
        focus = PredatoryFocus(max_stacks=20)
        focus.gain(10)
        assert focus.focus_ratio == 0.5


class TestPredatoryFocusLose:
    def test_lose_stacks(self):
        focus = PredatoryFocus(max_stacks=20)
        focus.gain(10)
        lost = focus.lose(4)
        assert lost == 4
        assert focus.current == 6

    def test_lose_clamped_at_zero(self):
        focus = PredatoryFocus(max_stacks=20)
        focus.gain(3)
        lost = focus.lose(10)
        assert lost == 3
        assert focus.current == 0

    def test_lose_from_zero(self):
        focus = PredatoryFocus(max_stacks=20)
        lost = focus.lose(5)
        assert lost == 0


class TestPredatoryFocusDecay:
    def test_decay_reduces_stacks(self):
        focus = PredatoryFocus(max_stacks=20)
        focus.gain(10)
        decayed = focus.decay(1)
        assert decayed == 1
        assert focus.current == 9

    def test_decay_clamped_at_zero(self):
        focus = PredatoryFocus(max_stacks=20)
        focus.gain(1)
        decayed = focus.decay(5)
        assert decayed == 1
        assert focus.current == 0


class TestPredatoryFocusEdgeCases:
    def test_focus_ratio_zero_max_returns_zero(self):
        focus = PredatoryFocus(max_stacks=0)
        assert focus.focus_ratio == 0.0
