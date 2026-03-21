"""Tests for ResourceCost frozen dataclass."""

import pytest

from src.core.skills.resource_cost import ResourceCost


class TestResourceCostCreation:
    """ResourceCost e um value object imutavel."""

    def test_create_with_type_and_amount(self) -> None:
        cost = ResourceCost(resource_type="action_points", amount=2)

        assert cost.resource_type == "action_points"
        assert cost.amount == 2

    def test_create_fury_cost(self) -> None:
        cost = ResourceCost(resource_type="fury_bar", amount=20)

        assert cost.resource_type == "fury_bar"
        assert cost.amount == 20

    def test_create_zero_amount_for_toggle_check(self) -> None:
        cost = ResourceCost(resource_type="stealth", amount=0)

        assert cost.amount == 0

    def test_is_frozen(self) -> None:
        cost = ResourceCost(resource_type="holy_power", amount=1)

        with pytest.raises(AttributeError):
            cost.amount = 5  # type: ignore[misc]

    def test_equality(self) -> None:
        a = ResourceCost(resource_type="action_points", amount=2)
        b = ResourceCost(resource_type="action_points", amount=2)

        assert a == b

    def test_different_costs_not_equal(self) -> None:
        a = ResourceCost(resource_type="action_points", amount=2)
        b = ResourceCost(resource_type="action_points", amount=3)

        assert a != b


class TestResourceCostFromDict:
    """Parsing de dicts JSON."""

    def test_from_dict_basic(self) -> None:
        data = {"resource_type": "fury_bar", "amount": 20}

        cost = ResourceCost.from_dict(data)

        assert cost.resource_type == "fury_bar"
        assert cost.amount == 20

    def test_from_dict_zero_amount(self) -> None:
        data = {"resource_type": "stealth", "amount": 0}

        cost = ResourceCost.from_dict(data)

        assert cost.amount == 0
