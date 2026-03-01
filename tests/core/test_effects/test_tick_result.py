"""Testes para TickResult frozen dataclass."""

import dataclasses

import pytest

from src.core.effects.tick_result import TickResult


class TestTickResult:
    def test_defaults_are_zero(self):
        result = TickResult()
        assert result.damage == 0
        assert result.healing == 0
        assert result.mana_change == 0
        assert result.message == ""

    def test_create_with_damage(self):
        result = TickResult(damage=15)
        assert result.damage == 15

    def test_create_with_healing(self):
        result = TickResult(healing=10)
        assert result.healing == 10

    def test_create_with_message(self):
        result = TickResult(damage=5, message="Poison deals 5 damage")
        assert result.message == "Poison deals 5 damage"

    def test_is_frozen(self):
        result = TickResult(damage=10)
        assert dataclasses.is_dataclass(result)
        with pytest.raises(dataclasses.FrozenInstanceError):
            result.damage = 20  # type: ignore[misc]

    def test_skip_turn_defaults_to_false(self):
        result = TickResult()
        assert result.skip_turn is False

    def test_create_with_skip_turn_true(self):
        result = TickResult(skip_turn=True, message="Frozen!")
        assert result.skip_turn is True
        assert result.message == "Frozen!"
