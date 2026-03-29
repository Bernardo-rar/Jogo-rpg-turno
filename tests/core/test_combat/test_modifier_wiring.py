"""Testes para wiring de run modifiers no combate."""

from __future__ import annotations

import pytest

from src.core.combat.skill_effect_applier import (
    apply_skill_effect,
    get_run_modifier_effect,
    set_run_modifier_effect,
)
from src.core.skills.skill_effect import SkillEffect
from src.core.skills.skill_effect_type import SkillEffectType
from src.dungeon.modifiers.run_modifier import ModifierEffect

from tests.core.test_combat.conftest import _build_char


@pytest.fixture(autouse=True)
def _clear_modifier():
    """Garante que o modifier global e limpo antes e depois de cada teste."""
    set_run_modifier_effect(None)
    yield
    set_run_modifier_effect(None)


class TestRunModifierEffectAccessors:

    def test_no_modifier_returns_none(self) -> None:
        assert get_run_modifier_effect() is None

    def test_set_and_get_modifier(self) -> None:
        effect = ModifierEffect(damage_dealt_mult=0.8)
        set_run_modifier_effect(effect)
        assert get_run_modifier_effect() is effect

    def test_clear_modifier(self) -> None:
        effect = ModifierEffect()
        set_run_modifier_effect(effect)
        set_run_modifier_effect(None)
        assert get_run_modifier_effect() is None


class TestDamageDealtMultScalesAttack:

    def test_damage_dealt_mult_reduces_damage(self) -> None:
        caster = _build_char("Caster")
        target_a = _build_char("TargetA")
        target_b = _build_char("TargetB")
        effect = SkillEffect(
            effect_type=SkillEffectType.DAMAGE, base_power=20,
        )
        events_no_mod = apply_skill_effect(effect, [target_a], 1, caster)
        set_run_modifier_effect(ModifierEffect(damage_dealt_mult=0.5))
        events_mod = apply_skill_effect(effect, [target_b], 1, caster)
        assert events_mod[0].damage.final_damage < events_no_mod[0].damage.final_damage

    def test_no_modifier_no_change(self) -> None:
        caster = _build_char("Caster")
        target = _build_char("Target")
        effect = SkillEffect(
            effect_type=SkillEffectType.DAMAGE, base_power=20,
        )
        events = apply_skill_effect(effect, [target], 1, caster)
        assert events[0].damage.final_damage > 0


class TestHealingMultScalesHeal:

    def test_healing_mult_reduces_heal(self) -> None:
        caster = _build_char("Healer")
        target_a = _build_char("TA")
        target_b = _build_char("TB")
        target_a.take_damage(30)
        target_b.take_damage(30)
        effect = SkillEffect(
            effect_type=SkillEffectType.HEAL, base_power=5,
        )
        events_no_mod = apply_skill_effect(effect, [target_a], 1, caster)
        set_run_modifier_effect(ModifierEffect(healing_mult=0.5))
        events_mod = apply_skill_effect(effect, [target_b], 1, caster)
        assert events_mod[0].value < events_no_mod[0].value

    def test_healing_mult_1_no_change(self) -> None:
        caster = _build_char("Healer")
        target = _build_char("Target")
        target.take_damage(30)
        effect = SkillEffect(
            effect_type=SkillEffectType.HEAL, base_power=5,
        )
        hp_before = target.current_hp
        apply_skill_effect(effect, [target], 1, caster)
        assert target.current_hp > hp_before
