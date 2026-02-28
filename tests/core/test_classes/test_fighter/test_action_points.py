import pytest

from src.core.classes.fighter.action_points import (
    AP_GAIN_PASSIVE,
    AP_LIMIT_PER_LEVEL,
    ActionPoints,
)


class TestActionPointsInit:
    def test_starts_at_zero(self):
        ap = ActionPoints(level=1)
        assert ap.current == 0

    def test_limit_level_1(self):
        assert ActionPoints(level=1).limit == AP_LIMIT_PER_LEVEL[1]

    def test_limit_level_3(self):
        assert ActionPoints(level=3).limit == AP_LIMIT_PER_LEVEL[3]

    def test_limit_level_5(self):
        assert ActionPoints(level=5).limit == AP_LIMIT_PER_LEVEL[5]

    def test_limit_increases_with_level(self):
        limits = [ActionPoints(level=lvl).limit for lvl in range(1, 6)]
        assert limits == sorted(limits)


class TestActionPointsGain:
    def test_gain_increases_current(self):
        ap = ActionPoints(level=1)
        ap.gain(1)
        assert ap.current == 1

    def test_gain_returns_actual_gained(self):
        ap = ActionPoints(level=1)
        actual = ap.gain(1)
        assert actual == 1

    def test_gain_capped_at_limit(self):
        ap = ActionPoints(level=1)  # limit=2
        ap.gain(999)
        assert ap.current == ap.limit

    def test_gain_returns_zero_when_full(self):
        ap = ActionPoints(level=1)
        ap.gain(999)
        actual = ap.gain(1)
        assert actual == 0


class TestActionPointsSpend:
    def test_spend_reduces_current(self):
        ap = ActionPoints(level=5)  # limit=10
        ap.gain(5)
        ap.spend(3)
        assert ap.current == 2

    def test_spend_returns_true_on_success(self):
        ap = ActionPoints(level=1)
        ap.gain(2)
        assert ap.spend(1) is True

    def test_spend_fails_when_insufficient(self):
        ap = ActionPoints(level=1)
        assert ap.spend(1) is False

    def test_spend_does_not_reduce_on_failure(self):
        ap = ActionPoints(level=1)
        ap.gain(1)
        ap.spend(2)
        assert ap.current == 1


class TestActionPointsTurnEnd:
    def test_passive_gain_when_no_spend(self):
        ap = ActionPoints(level=1)
        ap.on_turn_end()
        assert ap.current == AP_GAIN_PASSIVE

    def test_no_passive_gain_when_spent(self):
        ap = ActionPoints(level=5)
        ap.gain(5)
        ap.spend(1)
        ap.on_turn_end()
        assert ap.current == 4  # 5-1=4, no passive gain

    def test_passive_gain_resets_each_turn(self):
        ap = ActionPoints(level=1)
        ap.on_turn_end()  # +1 (passive), total=1
        ap.on_turn_end()  # +1 (passive, no spend this turn), total=2
        assert ap.current == 2

    def test_passive_gain_respects_limit(self):
        ap = ActionPoints(level=1)  # limit=2
        ap.gain(2)  # full
        ap.on_turn_end()
        assert ap.current == 2  # still at limit
