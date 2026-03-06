from src.core.classes.warlock.insanity_bar import InsanityBar


class TestInsanityBarCreation:
    def test_starts_at_zero(self):
        bar = InsanityBar()
        assert bar.current == 0

    def test_ratio_at_zero(self):
        bar = InsanityBar()
        assert bar.ratio == 0.0

    def test_max_is_100(self):
        bar = InsanityBar()
        assert bar.MAX_INSANITY == 100


class TestInsanityBarGain:
    def test_gain_increases_current(self):
        bar = InsanityBar()
        gained = bar.gain(10)
        assert bar.current == 10
        assert gained == 10

    def test_gain_capped_at_max(self):
        bar = InsanityBar()
        gained = bar.gain(150)
        assert bar.current == 100
        assert gained == 100

    def test_gain_partial_overflow(self):
        bar = InsanityBar()
        bar.gain(90)
        gained = bar.gain(20)
        assert bar.current == 100
        assert gained == 10

    def test_ratio_at_half(self):
        bar = InsanityBar()
        bar.gain(50)
        assert bar.ratio == 0.5

    def test_ratio_at_max(self):
        bar = InsanityBar()
        bar.gain(100)
        assert bar.ratio == 1.0


class TestInsanityBarDecay:
    def test_decay_reduces_current(self):
        bar = InsanityBar()
        bar.gain(50)
        decayed = bar.decay(10)
        assert bar.current == 40
        assert decayed == 10

    def test_decay_does_not_go_below_zero(self):
        bar = InsanityBar()
        bar.gain(5)
        decayed = bar.decay(10)
        assert bar.current == 0
        assert decayed == 5

    def test_decay_from_zero(self):
        bar = InsanityBar()
        decayed = bar.decay(10)
        assert bar.current == 0
        assert decayed == 0


class TestInsanityBarReset:
    def test_reset_clears_to_zero(self):
        bar = InsanityBar()
        bar.gain(80)
        bar.reset()
        assert bar.current == 0
        assert bar.ratio == 0.0
