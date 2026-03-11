"""Testes para consumable_loader."""

from __future__ import annotations

from src.core.elements.element_type import ElementType
from src.core.items.consumable_category import ConsumableCategory
from src.core.items.consumable_loader import load_consumables
from src.core.skills.target_type import TargetType


class TestConsumableLoader:
    def test_loads_all_consumables(self) -> None:
        consumables = load_consumables()
        assert len(consumables) == 6

    def test_returns_dict_of_consumable(self) -> None:
        consumables = load_consumables()
        assert "health_potion_small" in consumables
        assert "molotov" in consumables

    def test_health_potion_fields(self) -> None:
        consumables = load_consumables()
        hp = consumables["health_potion_small"]
        assert hp.name == "Small Health Potion"
        assert hp.category == ConsumableCategory.HEALING
        assert hp.mana_cost == 0
        assert hp.target_type == TargetType.SELF

    def test_molotov_has_fire_element(self) -> None:
        consumables = load_consumables()
        molotov = consumables["molotov"]
        assert molotov.effects[0].element == ElementType.FIRE

    def test_smoke_bomb_is_escape(self) -> None:
        consumables = load_consumables()
        bomb = consumables["smoke_bomb"]
        assert bomb.category == ConsumableCategory.ESCAPE
        assert bomb.max_stack == 3

    def test_antidote_targets_single_ally(self) -> None:
        consumables = load_consumables()
        antidote = consumables["antidote"]
        assert antidote.target_type == TargetType.SINGLE_ALLY
