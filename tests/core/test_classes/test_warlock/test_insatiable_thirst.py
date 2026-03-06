from src.core.classes.warlock.insatiable_thirst import (
    HP_THRESHOLD_RATIO,
    THIRST_TRIGGER_STACKS,
    InsatiableThirst,
)


class TestInsatiableThirstCreation:
    def test_starts_with_zero_stacks(self):
        thirst = InsatiableThirst()
        assert thirst.stacks == 0

    def test_starts_inactive(self):
        thirst = InsatiableThirst()
        assert thirst.is_active is False

    def test_starts_with_zero_remaining(self):
        thirst = InsatiableThirst()
        assert thirst.remaining_turns == 0


class TestInsatiableThirstStacking:
    def test_gains_stack_below_threshold(self):
        thirst = InsatiableThirst()
        thirst.check_and_stack(0.3)
        assert thirst.stacks == 1

    def test_no_stack_above_threshold(self):
        thirst = InsatiableThirst()
        thirst.check_and_stack(0.6)
        assert thirst.stacks == 0

    def test_no_stack_at_exactly_threshold(self):
        thirst = InsatiableThirst()
        thirst.check_and_stack(HP_THRESHOLD_RATIO)
        assert thirst.stacks == 0

    def test_accumulates_stacks(self):
        thirst = InsatiableThirst()
        for _ in range(3):
            thirst.check_and_stack(0.3)
        assert thirst.stacks == 3

    def test_triggers_at_max_stacks(self):
        thirst = InsatiableThirst()
        for i in range(THIRST_TRIGGER_STACKS - 1):
            result = thirst.check_and_stack(0.2)
            assert result is False
        result = thirst.check_and_stack(0.2)
        assert result is True

    def test_no_stacking_while_active(self):
        thirst = InsatiableThirst()
        thirst.activate(duration=3)
        thirst.check_and_stack(0.2)
        assert thirst.stacks == 0


class TestInsatiableThirstActivation:
    def test_activate_sets_active(self):
        thirst = InsatiableThirst()
        thirst.activate(duration=4)
        assert thirst.is_active is True

    def test_activate_sets_duration(self):
        thirst = InsatiableThirst()
        thirst.activate(duration=4)
        assert thirst.remaining_turns == 4

    def test_activate_resets_stacks(self):
        thirst = InsatiableThirst()
        for _ in range(3):
            thirst.check_and_stack(0.2)
        thirst.activate(duration=4)
        assert thirst.stacks == 0


class TestInsatiableThirstTick:
    def test_tick_decrements_duration(self):
        thirst = InsatiableThirst()
        thirst.activate(duration=3)
        thirst.tick()
        assert thirst.remaining_turns == 2

    def test_tick_deactivates_when_expired(self):
        thirst = InsatiableThirst()
        thirst.activate(duration=1)
        thirst.tick()
        assert thirst.is_active is False
        assert thirst.remaining_turns == 0

    def test_tick_noop_when_inactive(self):
        thirst = InsatiableThirst()
        thirst.tick()
        assert thirst.remaining_turns == 0
