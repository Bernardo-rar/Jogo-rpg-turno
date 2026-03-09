"""Testes para Inventory class."""

from __future__ import annotations

from src.core.items.consumable import Consumable
from src.core.items.consumable_category import ConsumableCategory
from src.core.items.consumable_effect import ConsumableEffect
from src.core.items.consumable_effect_type import ConsumableEffectType
from src.core.items.inventory import Inventory
from src.core.skills.target_type import TargetType


def _make_consumable(cid: str, max_stack: int = 10) -> Consumable:
    return Consumable(
        consumable_id=cid,
        name=cid.replace("_", " ").title(),
        category=ConsumableCategory.HEALING,
        mana_cost=0,
        target_type=TargetType.SELF,
        effects=(
            ConsumableEffect(effect_type=ConsumableEffectType.HEAL_HP, base_power=10),
        ),
        max_stack=max_stack,
    )


class TestInventoryBasic:
    def test_starts_empty(self) -> None:
        inv = Inventory()
        assert len(inv.slots) == 0
        assert inv.available_slots == 20

    def test_add_new_item_creates_slot(self) -> None:
        inv = Inventory()
        result = inv.add_item(_make_consumable("hp_pot"))
        assert result is True
        assert inv.has_item("hp_pot")
        assert inv.get_quantity("hp_pot") == 1

    def test_add_existing_item_increases_quantity(self) -> None:
        inv = Inventory()
        pot = _make_consumable("hp_pot")
        inv.add_item(pot, quantity=3)
        inv.add_item(pot, quantity=2)
        assert inv.get_quantity("hp_pot") == 5

    def test_add_exceeds_max_stack_returns_false(self) -> None:
        inv = Inventory()
        pot = _make_consumable("hp_pot", max_stack=5)
        inv.add_item(pot, quantity=4)
        result = inv.add_item(pot, quantity=3)
        assert result is False
        assert inv.get_quantity("hp_pot") == 4

    def test_is_full(self) -> None:
        inv = Inventory(max_slots=2)
        inv.add_item(_make_consumable("a"))
        inv.add_item(_make_consumable("b"))
        assert inv.is_full is True

    def test_add_item_fails_when_full(self) -> None:
        inv = Inventory(max_slots=2)
        inv.add_item(_make_consumable("a"))
        inv.add_item(_make_consumable("b"))
        result = inv.add_item(_make_consumable("c"))
        assert result is False


class TestInventoryRemove:
    def test_remove_decreases_quantity(self) -> None:
        inv = Inventory()
        inv.add_item(_make_consumable("hp_pot"), quantity=5)
        inv.remove_item("hp_pot", quantity=2)
        assert inv.get_quantity("hp_pot") == 3

    def test_remove_all_removes_slot(self) -> None:
        inv = Inventory()
        inv.add_item(_make_consumable("hp_pot"), quantity=3)
        inv.remove_item("hp_pot", quantity=3)
        assert inv.has_item("hp_pot") is False
        assert inv.available_slots == 20

    def test_remove_nonexistent_returns_false(self) -> None:
        inv = Inventory()
        result = inv.remove_item("nope")
        assert result is False

    def test_remove_more_than_available_returns_false(self) -> None:
        inv = Inventory()
        inv.add_item(_make_consumable("hp_pot"), quantity=2)
        result = inv.remove_item("hp_pot", quantity=5)
        assert result is False
        assert inv.get_quantity("hp_pot") == 2


class TestInventoryQuery:
    def test_get_slot_returns_slot(self) -> None:
        inv = Inventory()
        pot = _make_consumable("hp_pot")
        inv.add_item(pot, quantity=3)
        slot = inv.get_slot("hp_pot")
        assert slot is not None
        assert slot.quantity == 3
        assert slot.consumable is pot

    def test_get_slot_returns_none_if_missing(self) -> None:
        inv = Inventory()
        assert inv.get_slot("nope") is None

    def test_get_quantity_returns_zero_if_missing(self) -> None:
        inv = Inventory()
        assert inv.get_quantity("nope") == 0

    def test_custom_max_slots(self) -> None:
        inv = Inventory(max_slots=5)
        assert inv.available_slots == 5
