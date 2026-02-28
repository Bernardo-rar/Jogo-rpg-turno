from src.core.classes.mage.barrier import BARRIER_EFFICIENCY, Barrier


class TestBarrierInit:
    def test_starts_at_zero(self):
        barrier = Barrier()
        assert barrier.current == 0

    def test_not_active_when_empty(self):
        barrier = Barrier()
        assert barrier.is_active is False


class TestBarrierAdd:
    def test_add_increases_current(self):
        barrier = Barrier()
        barrier.add(100)
        assert barrier.current == 100

    def test_add_stacks(self):
        barrier = Barrier()
        barrier.add(50)
        barrier.add(30)
        assert barrier.current == 80

    def test_is_active_after_add(self):
        barrier = Barrier()
        barrier.add(10)
        assert barrier.is_active is True


class TestBarrierAbsorb:
    def test_full_absorb_returns_zero_remaining(self):
        barrier = Barrier()
        barrier.add(200)
        remaining = barrier.absorb(100)
        assert remaining == 0

    def test_full_absorb_reduces_barrier(self):
        barrier = Barrier()
        barrier.add(200)
        barrier.absorb(100)
        assert barrier.current == 100

    def test_partial_absorb_returns_remaining(self):
        barrier = Barrier()
        barrier.add(50)
        remaining = barrier.absorb(80)
        assert remaining == 30

    def test_partial_absorb_depletes_barrier(self):
        barrier = Barrier()
        barrier.add(50)
        barrier.absorb(80)
        assert barrier.current == 0

    def test_no_barrier_returns_full_damage(self):
        barrier = Barrier()
        remaining = barrier.absorb(100)
        assert remaining == 100

    def test_not_active_after_full_depletion(self):
        barrier = Barrier()
        barrier.add(50)
        barrier.absorb(50)
        assert barrier.is_active is False


class TestBarrierEfficiency:
    def test_efficiency_constant_is_two(self):
        assert BARRIER_EFFICIENCY == 2
