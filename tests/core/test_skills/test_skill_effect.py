"""Testes para SkillEffect frozen dataclass."""

from __future__ import annotations

import pytest

from src.core.effects.modifiable_stat import ModifiableStat
from src.core.elements.element_type import ElementType
from src.core.skills.skill_effect import SkillEffect
from src.core.skills.skill_effect_type import SkillEffectType


class TestSkillEffectCreation:
    def test_create_damage(self) -> None:
        se = SkillEffect(
            effect_type=SkillEffectType.DAMAGE, base_power=30,
        )
        assert se.effect_type == SkillEffectType.DAMAGE
        assert se.base_power == 30

    def test_create_heal(self) -> None:
        se = SkillEffect(
            effect_type=SkillEffectType.HEAL, base_power=20,
        )
        assert se.effect_type == SkillEffectType.HEAL
        assert se.base_power == 20

    def test_create_buff_with_stat(self) -> None:
        se = SkillEffect(
            effect_type=SkillEffectType.BUFF,
            base_power=10,
            stat=ModifiableStat.PHYSICAL_DEFENSE,
            duration=3,
        )
        assert se.stat == ModifiableStat.PHYSICAL_DEFENSE
        assert se.duration == 3

    def test_create_damage_with_element(self) -> None:
        se = SkillEffect(
            effect_type=SkillEffectType.DAMAGE,
            base_power=25,
            element=ElementType.FIRE,
        )
        assert se.element == ElementType.FIRE

    def test_create_ailment(self) -> None:
        se = SkillEffect(
            effect_type=SkillEffectType.APPLY_AILMENT,
            ailment_id="poison",
            duration=4,
        )
        assert se.ailment_id == "poison"
        assert se.duration == 4

    def test_defaults(self) -> None:
        se = SkillEffect(effect_type=SkillEffectType.DAMAGE)
        assert se.base_power == 0
        assert se.element is None
        assert se.stat is None
        assert se.ailment_id is None
        assert se.duration == 0

    def test_is_frozen(self) -> None:
        se = SkillEffect(effect_type=SkillEffectType.DAMAGE, base_power=10)
        with pytest.raises(AttributeError):
            se.base_power = 20  # type: ignore[misc]


class TestSkillEffectFromDict:
    def test_from_dict_damage(self) -> None:
        data: dict[str, object] = {
            "effect_type": "DAMAGE", "base_power": 30,
        }
        se = SkillEffect.from_dict(data)
        assert se.effect_type == SkillEffectType.DAMAGE
        assert se.base_power == 30

    def test_from_dict_with_element(self) -> None:
        data: dict[str, object] = {
            "effect_type": "DAMAGE",
            "base_power": 25,
            "element": "FIRE",
        }
        se = SkillEffect.from_dict(data)
        assert se.element == ElementType.FIRE

    def test_from_dict_buff_with_stat(self) -> None:
        data: dict[str, object] = {
            "effect_type": "BUFF",
            "base_power": 10,
            "stat": "PHYSICAL_DEFENSE",
            "duration": 3,
        }
        se = SkillEffect.from_dict(data)
        assert se.stat == ModifiableStat.PHYSICAL_DEFENSE
        assert se.duration == 3

    def test_from_dict_ailment(self) -> None:
        data: dict[str, object] = {
            "effect_type": "APPLY_AILMENT",
            "ailment_id": "poison",
            "duration": 4,
        }
        se = SkillEffect.from_dict(data)
        assert se.ailment_id == "poison"

    def test_from_dict_defaults(self) -> None:
        data: dict[str, object] = {"effect_type": "HEAL"}
        se = SkillEffect.from_dict(data)
        assert se.base_power == 0
        assert se.element is None
        assert se.stat is None
