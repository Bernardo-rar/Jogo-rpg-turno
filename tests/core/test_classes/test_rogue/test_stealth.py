from __future__ import annotations

from src.core.classes.rogue.stealth import Stealth


class TestStealthDefault:
    def test_starts_inactive(self) -> None:
        stealth = Stealth()
        assert stealth.is_active is False

    def test_guaranteed_crit_false_when_inactive(self) -> None:
        stealth = Stealth()
        assert stealth.guaranteed_crit is False


class TestStealthEnter:
    def test_enter_activates(self) -> None:
        stealth = Stealth()
        result = stealth.enter()
        assert result is True
        assert stealth.is_active is True

    def test_enter_sets_guaranteed_crit(self) -> None:
        stealth = Stealth()
        stealth.enter()
        assert stealth.guaranteed_crit is True

    def test_enter_when_already_active_returns_false(self) -> None:
        stealth = Stealth()
        stealth.enter()
        result = stealth.enter()
        assert result is False


class TestStealthBreak:
    def test_break_deactivates(self) -> None:
        stealth = Stealth()
        stealth.enter()
        result = stealth.break_stealth()
        assert result is True
        assert stealth.is_active is False

    def test_break_clears_guaranteed_crit(self) -> None:
        stealth = Stealth()
        stealth.enter()
        stealth.break_stealth()
        assert stealth.guaranteed_crit is False

    def test_break_when_inactive_returns_false(self) -> None:
        stealth = Stealth()
        result = stealth.break_stealth()
        assert result is False


class TestStealthCycle:
    def test_can_reenter_after_break(self) -> None:
        stealth = Stealth()
        stealth.enter()
        stealth.break_stealth()
        result = stealth.enter()
        assert result is True
        assert stealth.is_active is True

    def test_enter_break_enter_cycle(self) -> None:
        stealth = Stealth()
        stealth.enter()
        assert stealth.guaranteed_crit is True
        stealth.break_stealth()
        assert stealth.guaranteed_crit is False
        stealth.enter()
        assert stealth.guaranteed_crit is True
