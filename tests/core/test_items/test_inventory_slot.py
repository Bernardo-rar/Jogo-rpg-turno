"""Testes para InventorySlot frozen dataclass."""

from __future__ import annotations

from dataclasses import replace

import pytest

from src.core.items.consumable import Consumable
from src.core.items.consumable_category import ConsumableCategory
from src.core.items.consumable_effect_type import ConsumableEffectType
from src.core.items.consumable_effect import ConsumableEffect
from src.core.items.inventory_slot import InventorySlot
from src.core.skills.target_type import TargetType


def _potion() -> Consumable:
    return Consumable(
        consumable_id="hp_pot",
        name="Health Potion",
        category=ConsumableCategory.HEALING,
        mana_cost=5,
        target_type=TargetType.SELF,
        effects=(
            ConsumableEffect(
                effect_type=ConsumableEffectType.HEAL_HP,
                base_power=50,
            ),
        ),
    )


class TestInventorySlot:
    def test_creation(self) -> None:
        slot = InventorySlot(consumable=_potion(), quantity=3)
        assert slot.consumable.consumable_id == "hp_pot"
        assert slot.quantity == 3

    def test_is_frozen(self) -> None:
        slot = InventorySlot(consumable=_potion(), quantity=1)
        with pytest.raises(AttributeError):
            slot.quantity = 5  # type: ignore[misc]

    def test_replace_creates_new(self) -> None:
        slot = InventorySlot(consumable=_potion(), quantity=3)
        updated = replace(slot, quantity=5)
        assert updated.quantity == 5
        assert slot.quantity == 3

    def test_consumable_reference(self) -> None:
        potion = _potion()
        slot = InventorySlot(consumable=potion, quantity=2)
        assert slot.consumable is potion
