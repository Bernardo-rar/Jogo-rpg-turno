"""Tests for ClassResourceResolver — can_afford + spend via duck typing."""

from __future__ import annotations

from src.core.skills.class_resource_resolver import (
    can_afford_resource,
    spend_resource,
)
from src.core.skills.resource_cost import ResourceCost


class _FakeResource:
    """Recurso fake com interface spend/current."""

    def __init__(self, current: int) -> None:
        self._current = current

    @property
    def current(self) -> int:
        return self._current

    def spend(self, amount: int) -> bool:
        if self._current < amount:
            return False
        self._current -= amount
        return True


class _FakeCombatant:
    """Combatant fake com recurso acessivel via atributo."""

    def __init__(self, resource_name: str, resource: _FakeResource) -> None:
        setattr(self, resource_name, resource)


class TestCanAffordResource:
    def test_can_afford_when_enough(self) -> None:
        combatant = _FakeCombatant("action_points", _FakeResource(5))
        cost = ResourceCost("action_points", 3)

        assert can_afford_resource(combatant, cost) is True

    def test_cannot_afford_when_not_enough(self) -> None:
        combatant = _FakeCombatant("action_points", _FakeResource(1))
        cost = ResourceCost("action_points", 3)

        assert can_afford_resource(combatant, cost) is False

    def test_cannot_afford_when_resource_missing(self) -> None:
        combatant = _FakeCombatant("action_points", _FakeResource(5))
        cost = ResourceCost("fury_bar", 10)

        assert can_afford_resource(combatant, cost) is False

    def test_can_afford_exact_amount(self) -> None:
        combatant = _FakeCombatant("fury_bar", _FakeResource(20))
        cost = ResourceCost("fury_bar", 20)

        assert can_afford_resource(combatant, cost) is True

    def test_can_afford_zero_always_true(self) -> None:
        combatant = _FakeCombatant("action_points", _FakeResource(0))
        cost = ResourceCost("action_points", 0)

        assert can_afford_resource(combatant, cost) is True


class TestSpendResource:
    def test_spend_success(self) -> None:
        resource = _FakeResource(5)
        combatant = _FakeCombatant("action_points", resource)
        cost = ResourceCost("action_points", 2)

        result = spend_resource(combatant, cost)

        assert result is True
        assert resource.current == 3

    def test_spend_fails_when_not_enough(self) -> None:
        resource = _FakeResource(1)
        combatant = _FakeCombatant("action_points", resource)
        cost = ResourceCost("action_points", 5)

        result = spend_resource(combatant, cost)

        assert result is False
        assert resource.current == 1

    def test_spend_fails_when_resource_missing(self) -> None:
        combatant = _FakeCombatant("action_points", _FakeResource(5))
        cost = ResourceCost("fury_bar", 10)

        result = spend_resource(combatant, cost)

        assert result is False

    def test_spend_zero_succeeds(self) -> None:
        resource = _FakeResource(5)
        combatant = _FakeCombatant("action_points", resource)
        cost = ResourceCost("action_points", 0)

        result = spend_resource(combatant, cost)

        assert result is True
        assert resource.current == 5
