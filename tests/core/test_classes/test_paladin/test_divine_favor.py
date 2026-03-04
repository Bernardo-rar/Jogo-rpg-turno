from src.core.classes.paladin.divine_favor import DivineFavor


class TestDivineFavorCreation:
    def test_starts_at_zero(self):
        df = DivineFavor(max_stacks=10)
        assert df.current == 0

    def test_max_stacks(self):
        df = DivineFavor(max_stacks=10)
        assert df.max_stacks == 10


class TestDivineFavorGain:
    def test_gain_increases_current(self):
        df = DivineFavor(max_stacks=10)
        gained = df.gain(3)
        assert df.current == 3
        assert gained == 3

    def test_gain_default_one(self):
        df = DivineFavor(max_stacks=10)
        df.gain()
        assert df.current == 1

    def test_gain_capped_at_max(self):
        df = DivineFavor(max_stacks=5)
        gained = df.gain(8)
        assert df.current == 5
        assert gained == 5

    def test_gain_partial_overflow(self):
        df = DivineFavor(max_stacks=10)
        df.gain(8)
        gained = df.gain(5)
        assert df.current == 10
        assert gained == 2


class TestDivineFavorSpend:
    def test_spend_reduces_current(self):
        df = DivineFavor(max_stacks=10)
        df.gain(7)
        result = df.spend(3)
        assert result is True
        assert df.current == 4

    def test_spend_insufficient_returns_false(self):
        df = DivineFavor(max_stacks=10)
        df.gain(2)
        result = df.spend(5)
        assert result is False
        assert df.current == 2

    def test_spend_exact_amount(self):
        df = DivineFavor(max_stacks=10)
        df.gain(5)
        result = df.spend(5)
        assert result is True
        assert df.current == 0
