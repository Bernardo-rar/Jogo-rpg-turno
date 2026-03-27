"""Tests for new SkillEffectTypes: TRIGGER_CLASS_MECHANIC, RESOURCE_GAIN, SHIELD, COUNTER_ATTACK."""

from __future__ import annotations

from src.core.combat.combat_engine import EventType
from src.core.combat.skill_effect_applier import (
    _MECHANIC_DISPATCH,
    apply_skill_effect,
)
from src.core.skills.skill_effect import SkillEffect
from src.core.skills.skill_effect_type import SkillEffectType

from tests.core.test_combat.conftest import _build_char


class _FakeResource:
    def __init__(self, current: int) -> None:
        self._current = current

    @property
    def current(self) -> int:
        return self._current

    def gain(self, amount: int) -> int:
        self._current += amount
        return amount


class TestTriggerClassMechanic:
    def test_fires_mechanic_from_dispatch(self) -> None:
        called = []
        _MECHANIC_DISPATCH["test_mechanic"] = lambda c, p: called.append(c.name)

        caster = _build_char("Caster")
        target = _build_char("Target")
        effect = SkillEffect(
            effect_type=SkillEffectType.TRIGGER_CLASS_MECHANIC,
            mechanic_id="test_mechanic",
        )
        events = apply_skill_effect(effect, [target], 1, caster)

        assert len(events) == 1
        assert events[0].event_type == EventType.SKILL_USE
        assert called == ["Target"]

        del _MECHANIC_DISPATCH["test_mechanic"]

    def test_no_mechanic_id_returns_empty(self) -> None:
        effect = SkillEffect(
            effect_type=SkillEffectType.TRIGGER_CLASS_MECHANIC,
        )
        events = apply_skill_effect(effect, [_build_char("T")], 1, _build_char("C"))
        assert events == []

    def test_unknown_mechanic_returns_empty(self) -> None:
        effect = SkillEffect(
            effect_type=SkillEffectType.TRIGGER_CLASS_MECHANIC,
            mechanic_id="nonexistent",
        )
        events = apply_skill_effect(effect, [_build_char("T")], 1, _build_char("C"))
        assert events == []


class TestResourceGain:
    def test_gains_resource(self) -> None:
        resource = _FakeResource(5)
        target = _build_char("Target")
        target.action_points = resource
        caster = _build_char("Caster")

        effect = SkillEffect(
            effect_type=SkillEffectType.RESOURCE_GAIN,
            base_power=3,
            resource_type="action_points",
        )
        events = apply_skill_effect(effect, [target], 1, caster)

        assert resource.current == 8
        assert len(events) == 1
        assert events[0].value == 3

    def test_no_resource_type_returns_empty(self) -> None:
        effect = SkillEffect(
            effect_type=SkillEffectType.RESOURCE_GAIN,
            base_power=3,
        )
        events = apply_skill_effect(effect, [_build_char("T")], 1, _build_char("C"))
        assert events == []

    def test_missing_resource_skips_target(self) -> None:
        target = _build_char("Target")
        effect = SkillEffect(
            effect_type=SkillEffectType.RESOURCE_GAIN,
            base_power=3,
            resource_type="fury_bar",
        )
        events = apply_skill_effect(effect, [target], 1, _build_char("C"))
        assert events == []


class TestShield:
    def test_creates_shield_event(self) -> None:
        target = _build_char("Target")
        caster = _build_char("Caster")
        effect = SkillEffect(
            effect_type=SkillEffectType.SHIELD,
            base_power=20,
        )
        events = apply_skill_effect(effect, [target], 1, caster)
        assert len(events) == 1
        assert events[0].value == 20
        assert events[0].description == "shield"


class TestCounterAttack:
    def test_counter_deals_damage(self) -> None:
        caster = _build_char("Reactor")
        target = _build_char("Attacker")
        hp_before = target.current_hp

        effect = SkillEffect(
            effect_type=SkillEffectType.COUNTER_ATTACK,
            base_power=10,
        )
        events = apply_skill_effect(effect, [target], 1, caster)

        assert len(events) == 1
        assert events[0].damage is not None
        assert target.current_hp < hp_before
