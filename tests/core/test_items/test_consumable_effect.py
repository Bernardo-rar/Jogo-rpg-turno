"""Testes para ConsumableEffect frozen dataclass."""

from __future__ import annotations

import pytest

from src.core.effects.modifiable_stat import ModifiableStat
from src.core.elements.element_type import ElementType
from src.core.items.consumable_effect import ConsumableEffect
from src.core.items.consumable_effect_type import ConsumableEffectType


class TestConsumableEffectCreation:
    def test_create_heal_hp(self) -> None:
        ce = ConsumableEffect(
            effect_type=ConsumableEffectType.HEAL_HP, base_power=50,
        )
        assert ce.effect_type == ConsumableEffectType.HEAL_HP
        assert ce.base_power == 50

    def test_create_damage_with_element(self) -> None:
        ce = ConsumableEffect(
            effect_type=ConsumableEffectType.DAMAGE,
            base_power=40,
            element=ElementType.FIRE,
        )
        assert ce.element == ElementType.FIRE

    def test_create_buff_with_stat(self) -> None:
        ce = ConsumableEffect(
            effect_type=ConsumableEffectType.BUFF,
            base_power=15,
            stat=ModifiableStat.PHYSICAL_DEFENSE,
            duration=3,
        )
        assert ce.stat == ModifiableStat.PHYSICAL_DEFENSE
        assert ce.duration == 3

    def test_create_cleanse(self) -> None:
        ce = ConsumableEffect(effect_type=ConsumableEffectType.CLEANSE)
        assert ce.effect_type == ConsumableEffectType.CLEANSE
        assert ce.base_power == 0

    def test_create_flee(self) -> None:
        ce = ConsumableEffect(effect_type=ConsumableEffectType.FLEE)
        assert ce.effect_type == ConsumableEffectType.FLEE

    def test_defaults(self) -> None:
        ce = ConsumableEffect(effect_type=ConsumableEffectType.HEAL_HP)
        assert ce.base_power == 0
        assert ce.element is None
        assert ce.stat is None
        assert ce.duration == 0

    def test_is_frozen(self) -> None:
        ce = ConsumableEffect(
            effect_type=ConsumableEffectType.DAMAGE, base_power=10,
        )
        with pytest.raises(AttributeError):
            ce.base_power = 20  # type: ignore[misc]


class TestConsumableEffectFromDict:
    def test_from_dict_heal_hp(self) -> None:
        data: dict[str, object] = {
            "effect_type": "HEAL_HP", "base_power": 50,
        }
        ce = ConsumableEffect.from_dict(data)
        assert ce.effect_type == ConsumableEffectType.HEAL_HP
        assert ce.base_power == 50

    def test_from_dict_damage_with_element(self) -> None:
        data: dict[str, object] = {
            "effect_type": "DAMAGE",
            "base_power": 40,
            "element": "FIRE",
        }
        ce = ConsumableEffect.from_dict(data)
        assert ce.element == ElementType.FIRE

    def test_from_dict_buff_with_stat(self) -> None:
        data: dict[str, object] = {
            "effect_type": "BUFF",
            "base_power": 15,
            "stat": "PHYSICAL_DEFENSE",
            "duration": 3,
        }
        ce = ConsumableEffect.from_dict(data)
        assert ce.stat == ModifiableStat.PHYSICAL_DEFENSE
        assert ce.duration == 3

    def test_from_dict_defaults(self) -> None:
        data: dict[str, object] = {"effect_type": "CLEANSE"}
        ce = ConsumableEffect.from_dict(data)
        assert ce.base_power == 0
        assert ce.element is None
        assert ce.stat is None
