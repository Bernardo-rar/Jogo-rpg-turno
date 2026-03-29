"""Testes para campo usable_outside_combat do Consumable."""

from __future__ import annotations

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
        effect_type=ConsumableEffectType.DAMAGE, base_power=40,
    )


class TestUsableOutsideCombat:
    def test_health_potion_usable_outside(self) -> None:
        c = Consumable(
            consumable_id="hp_pot",
            name="Health Potion",
            category=ConsumableCategory.HEALING,
            mana_cost=0,
            target_type=TargetType.SELF,
            effects=(_heal_effect(),),
            usable_outside_combat=True,
        )
        assert c.usable_outside_combat is True

    def test_molotov_not_usable_outside(self) -> None:
        c = Consumable(
            consumable_id="molotov",
            name="Molotov",
            category=ConsumableCategory.OFFENSIVE,
            mana_cost=5,
            target_type=TargetType.ALL_ENEMIES,
            effects=(_damage_effect(),),
            usable_outside_combat=False,
        )
        assert c.usable_outside_combat is False

    def test_default_is_false(self) -> None:
        c = Consumable(
            consumable_id="test",
            name="Test",
            category=ConsumableCategory.HEALING,
            mana_cost=0,
            target_type=TargetType.SELF,
            effects=(),
        )
        assert c.usable_outside_combat is False

    def test_from_dict_parses_flag_true(self) -> None:
        data: dict[str, object] = {
            "name": "Small Health Potion",
            "category": "HEALING",
            "mana_cost": 0,
            "target_type": "SELF",
            "effects": [{"effect_type": "HEAL_HP", "base_power": 50}],
            "usable_outside_combat": True,
        }
        c = Consumable.from_dict("health_potion_small", data)
        assert c.usable_outside_combat is True

    def test_from_dict_parses_flag_false(self) -> None:
        data: dict[str, object] = {
            "name": "Molotov",
            "category": "OFFENSIVE",
            "mana_cost": 5,
            "target_type": "ALL_ENEMIES",
            "effects": [{"effect_type": "DAMAGE", "base_power": 40}],
            "usable_outside_combat": False,
        }
        c = Consumable.from_dict("molotov", data)
        assert c.usable_outside_combat is False

    def test_from_dict_defaults_to_false(self) -> None:
        data: dict[str, object] = {
            "name": "Test",
            "category": "HEALING",
            "mana_cost": 0,
            "target_type": "SELF",
            "effects": [],
        }
        c = Consumable.from_dict("test", data)
        assert c.usable_outside_combat is False
