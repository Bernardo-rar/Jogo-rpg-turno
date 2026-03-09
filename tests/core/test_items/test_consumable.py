"""Testes para Consumable frozen dataclass."""

from __future__ import annotations

import pytest

from src.core.elements.element_type import ElementType
from src.core.items.consumable import Consumable
from src.core.items.consumable_category import ConsumableCategory
from src.core.items.consumable_effect import ConsumableEffect
from src.core.items.consumable_effect_type import ConsumableEffectType
from src.core.skills.target_type import TargetType


def _heal_effect() -> ConsumableEffect:
    return ConsumableEffect(
        effect_type=ConsumableEffectType.HEAL_HP, base_power=50,
    )


def _damage_effect() -> ConsumableEffect:
    return ConsumableEffect(
        effect_type=ConsumableEffectType.DAMAGE,
        base_power=40,
        element=ElementType.FIRE,
    )


class TestConsumableCreation:
    def test_create_healing_potion(self) -> None:
        c = Consumable(
            consumable_id="hp_pot",
            name="Health Potion",
            category=ConsumableCategory.HEALING,
            mana_cost=5,
            target_type=TargetType.SELF,
            effects=(_heal_effect(),),
        )
        assert c.consumable_id == "hp_pot"
        assert c.name == "Health Potion"
        assert c.category == ConsumableCategory.HEALING

    def test_create_offensive_item(self) -> None:
        c = Consumable(
            consumable_id="molotov",
            name="Molotov",
            category=ConsumableCategory.OFFENSIVE,
            mana_cost=10,
            target_type=TargetType.ALL_ENEMIES,
            effects=(_damage_effect(),),
        )
        assert c.target_type == TargetType.ALL_ENEMIES

    def test_defaults(self) -> None:
        c = Consumable(
            consumable_id="test",
            name="Test",
            category=ConsumableCategory.HEALING,
            mana_cost=0,
            target_type=TargetType.SELF,
            effects=(),
        )
        assert c.max_stack == 10
        assert c.description == ""

    def test_custom_max_stack(self) -> None:
        c = Consumable(
            consumable_id="bomb",
            name="Bomb",
            category=ConsumableCategory.OFFENSIVE,
            mana_cost=10,
            target_type=TargetType.ALL_ENEMIES,
            effects=(_damage_effect(),),
            max_stack=5,
        )
        assert c.max_stack == 5

    def test_is_frozen(self) -> None:
        c = Consumable(
            consumable_id="test",
            name="Test",
            category=ConsumableCategory.HEALING,
            mana_cost=0,
            target_type=TargetType.SELF,
            effects=(),
        )
        with pytest.raises(AttributeError):
            c.name = "Changed"  # type: ignore[misc]

    def test_effects_is_tuple(self) -> None:
        c = Consumable(
            consumable_id="test",
            name="Test",
            category=ConsumableCategory.HEALING,
            mana_cost=0,
            target_type=TargetType.SELF,
            effects=(_heal_effect(), _damage_effect()),
        )
        assert isinstance(c.effects, tuple)
        assert len(c.effects) == 2


class TestConsumableFromDict:
    def test_from_dict_basic(self) -> None:
        data: dict[str, object] = {
            "name": "Small Health Potion",
            "category": "HEALING",
            "mana_cost": 5,
            "target_type": "SELF",
            "effects": [{"effect_type": "HEAL_HP", "base_power": 50}],
        }
        c = Consumable.from_dict("health_potion_small", data)
        assert c.consumable_id == "health_potion_small"
        assert c.name == "Small Health Potion"
        assert c.category == ConsumableCategory.HEALING
        assert c.mana_cost == 5

    def test_from_dict_with_element(self) -> None:
        data: dict[str, object] = {
            "name": "Molotov",
            "category": "OFFENSIVE",
            "mana_cost": 10,
            "target_type": "ALL_ENEMIES",
            "effects": [
                {"effect_type": "DAMAGE", "base_power": 40, "element": "FIRE"},
            ],
        }
        c = Consumable.from_dict("molotov", data)
        assert c.effects[0].element == ElementType.FIRE

    def test_from_dict_defaults(self) -> None:
        data: dict[str, object] = {
            "name": "Test",
            "category": "ESCAPE",
            "mana_cost": 0,
            "target_type": "ALL_ALLIES",
            "effects": [{"effect_type": "FLEE"}],
        }
        c = Consumable.from_dict("test", data)
        assert c.max_stack == 10
        assert c.description == ""

    def test_from_dict_all_fields(self) -> None:
        data: dict[str, object] = {
            "name": "Super Potion",
            "category": "HEALING",
            "mana_cost": 15,
            "target_type": "SINGLE_ALLY",
            "effects": [{"effect_type": "HEAL_HP", "base_power": 100}],
            "max_stack": 3,
            "description": "Cura poderosa",
        }
        c = Consumable.from_dict("super_pot", data)
        assert c.max_stack == 3
        assert c.description == "Cura poderosa"
