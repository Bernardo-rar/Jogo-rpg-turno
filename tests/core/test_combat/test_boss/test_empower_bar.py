"""Tests for EmpowerBar — boss empower resource."""

import pytest

from src.core.combat.boss.empower_bar import EmpowerBar, EmpowerBarConfig


@pytest.fixture
def config() -> EmpowerBarConfig:
    return EmpowerBarConfig(
        max_value=100,
        gain_per_round=20,
        loss_on_weakness_hit=40,
        empowered_atk_mult=1.50,
        empowered_def_mult=1.20,
        empowered_duration=3,
    )


@pytest.fixture
def bar(config: EmpowerBarConfig) -> EmpowerBar:
    return EmpowerBar(config)


class TestEmpowerBarInit:

    def test_starts_at_zero(self, bar: EmpowerBar) -> None:
        assert bar.current == 0

    def test_not_full_at_start(self, bar: EmpowerBar) -> None:
        assert not bar.is_full

    def test_not_empowered_at_start(self, bar: EmpowerBar) -> None:
        assert not bar.is_empowered


class TestEmpowerBarTick:

    def test_tick_adds_gain(self, bar: EmpowerBar) -> None:
        bar.tick_round()
        assert bar.current == 20

    def test_two_ticks(self, bar: EmpowerBar) -> None:
        bar.tick_round()
        bar.tick_round()
        assert bar.current == 40

    def test_five_ticks_fills_bar(self, bar: EmpowerBar) -> None:
        for _ in range(5):
            bar.tick_round()
        assert bar.is_full

    def test_tick_returns_true_when_full(self, bar: EmpowerBar) -> None:
        for _ in range(4):
            bar.tick_round()
        result = bar.tick_round()
        assert result is True

    def test_tick_returns_false_when_not_full(self, bar: EmpowerBar) -> None:
        result = bar.tick_round()
        assert result is False

    def test_bar_capped_at_max(self, bar: EmpowerBar) -> None:
        for _ in range(10):
            bar.tick_round()
        assert bar.current == 100


class TestEmpowerBarWeakness:

    def test_weakness_hit_reduces_bar(self, bar: EmpowerBar) -> None:
        bar.tick_round()
        bar.tick_round()  # 40
        bar.on_weakness_hit()
        assert bar.current == 0

    def test_weakness_does_not_go_negative(self, bar: EmpowerBar) -> None:
        bar.tick_round()  # 20
        bar.on_weakness_hit()  # -40 => clamp to 0
        assert bar.current == 0

    def test_weakness_during_empowered_has_no_effect(
        self, bar: EmpowerBar,
    ) -> None:
        for _ in range(5):
            bar.tick_round()
        bar.activate_empowered()
        old = bar.current
        bar.on_weakness_hit()
        assert bar.current == old


class TestEmpowerBarEmpoweredState:

    def test_activate_resets_bar(self, bar: EmpowerBar) -> None:
        for _ in range(5):
            bar.tick_round()
        bar.activate_empowered()
        assert bar.current == 0

    def test_is_empowered_after_activate(self, bar: EmpowerBar) -> None:
        for _ in range(5):
            bar.tick_round()
        bar.activate_empowered()
        assert bar.is_empowered

    def test_empowered_lasts_configured_turns(
        self, bar: EmpowerBar,
    ) -> None:
        for _ in range(5):
            bar.tick_round()
        bar.activate_empowered()
        for _ in range(3):
            assert bar.is_empowered
            bar.tick_empowered()
        assert not bar.is_empowered

    def test_tick_empowered_returns_true_on_expiry(
        self, bar: EmpowerBar,
    ) -> None:
        for _ in range(5):
            bar.tick_round()
        bar.activate_empowered()
        bar.tick_empowered()
        bar.tick_empowered()
        result = bar.tick_empowered()
        assert result is True

    def test_tick_empowered_returns_false_before_expiry(
        self, bar: EmpowerBar,
    ) -> None:
        for _ in range(5):
            bar.tick_round()
        bar.activate_empowered()
        result = bar.tick_empowered()
        assert result is False

    def test_bar_does_not_fill_while_empowered(
        self, bar: EmpowerBar,
    ) -> None:
        for _ in range(5):
            bar.tick_round()
        bar.activate_empowered()
        bar.tick_round()
        assert bar.current == 0

    def test_bar_fills_again_after_empowered_ends(
        self, bar: EmpowerBar,
    ) -> None:
        for _ in range(5):
            bar.tick_round()
        bar.activate_empowered()
        for _ in range(3):
            bar.tick_empowered()
        bar.tick_round()
        assert bar.current == 20


class TestEmpowerBarMultipliers:

    def test_atk_mult(self, bar: EmpowerBar) -> None:
        for _ in range(5):
            bar.tick_round()
        bar.activate_empowered()
        assert bar.atk_mult == 1.50

    def test_def_mult(self, bar: EmpowerBar) -> None:
        for _ in range(5):
            bar.tick_round()
        bar.activate_empowered()
        assert bar.def_mult == 1.20

    def test_mult_is_neutral_when_not_empowered(
        self, bar: EmpowerBar,
    ) -> None:
        assert bar.atk_mult == 1.0
        assert bar.def_mult == 1.0
