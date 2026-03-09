"""Testes para CooldownTracker."""

from __future__ import annotations

from src.core.skills.cooldown_tracker import CooldownTracker


class TestCooldownTrackerReady:
    def test_unknown_skill_is_ready(self) -> None:
        ct = CooldownTracker()
        assert ct.is_ready("fireball") is True

    def test_after_start_not_ready(self) -> None:
        ct = CooldownTracker()
        ct.start_cooldown("fireball", 3)
        assert ct.is_ready("fireball") is False

    def test_zero_cooldown_still_ready(self) -> None:
        ct = CooldownTracker()
        ct.start_cooldown("fireball", 0)
        assert ct.is_ready("fireball") is True


class TestCooldownTrackerTick:
    def test_tick_decrements(self) -> None:
        ct = CooldownTracker()
        ct.start_cooldown("fireball", 3)
        ct.tick()
        assert ct.remaining("fireball") == 2

    def test_tick_until_ready(self) -> None:
        ct = CooldownTracker()
        ct.start_cooldown("fireball", 2)
        ct.tick()
        ct.tick()
        assert ct.is_ready("fireball") is True

    def test_tick_does_not_go_negative(self) -> None:
        ct = CooldownTracker()
        ct.start_cooldown("fireball", 1)
        ct.tick()
        ct.tick()
        assert ct.remaining("fireball") == 0

    def test_tick_multiple_skills(self) -> None:
        ct = CooldownTracker()
        ct.start_cooldown("fireball", 2)
        ct.start_cooldown("heal", 3)
        ct.tick()
        assert ct.remaining("fireball") == 1
        assert ct.remaining("heal") == 2


class TestCooldownTrackerRemaining:
    def test_unknown_skill_zero(self) -> None:
        ct = CooldownTracker()
        assert ct.remaining("fireball") == 0

    def test_remaining_after_start(self) -> None:
        ct = CooldownTracker()
        ct.start_cooldown("revive", 5)
        assert ct.remaining("revive") == 5


class TestCooldownTrackerReset:
    def test_reset_clears_all(self) -> None:
        ct = CooldownTracker()
        ct.start_cooldown("fireball", 3)
        ct.start_cooldown("heal", 5)
        ct.reset()
        assert ct.is_ready("fireball") is True
        assert ct.is_ready("heal") is True

    def test_reset_remaining_zero(self) -> None:
        ct = CooldownTracker()
        ct.start_cooldown("fireball", 3)
        ct.reset()
        assert ct.remaining("fireball") == 0


class TestCooldownTrackerOverwrite:
    def test_start_overwrites_existing(self) -> None:
        ct = CooldownTracker()
        ct.start_cooldown("fireball", 3)
        ct.start_cooldown("fireball", 5)
        assert ct.remaining("fireball") == 5
