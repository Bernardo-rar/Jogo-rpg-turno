from src.core.classes.cleric.holy_power import (
    HOLY_POWER_LIMIT,
    HOLY_POWER_PER_HEAL,
    HolyPower,
)


class TestHolyPowerInit:
    def test_starts_at_zero(self):
        hp = HolyPower()
        assert hp.current == 0

    def test_limit_is_five(self):
        hp = HolyPower()
        assert hp.limit == HOLY_POWER_LIMIT


class TestHolyPowerGain:
    def test_gain_increases_current(self):
        hp = HolyPower()
        hp.gain(2)
        assert hp.current == 2

    def test_gain_returns_actual_gained(self):
        hp = HolyPower()
        actual = hp.gain(3)
        assert actual == 3

    def test_gain_capped_at_limit(self):
        hp = HolyPower()
        hp.gain(10)
        assert hp.current == HOLY_POWER_LIMIT

    def test_gain_returns_zero_when_full(self):
        hp = HolyPower()
        hp.gain(HOLY_POWER_LIMIT)
        actual = hp.gain(1)
        assert actual == 0


class TestHolyPowerSpend:
    def test_spend_reduces_current(self):
        hp = HolyPower()
        hp.gain(5)
        hp.spend(3)
        assert hp.current == 2

    def test_spend_returns_true_on_success(self):
        hp = HolyPower()
        hp.gain(3)
        assert hp.spend(2) is True

    def test_spend_fails_when_insufficient(self):
        hp = HolyPower()
        hp.gain(1)
        assert hp.spend(3) is False

    def test_spend_does_not_reduce_on_failure(self):
        hp = HolyPower()
        hp.gain(1)
        hp.spend(3)
        assert hp.current == 1


class TestHolyPowerConstants:
    def test_limit_constant(self):
        assert HOLY_POWER_LIMIT == 5

    def test_per_heal_constant(self):
        assert HOLY_POWER_PER_HEAL == 1
