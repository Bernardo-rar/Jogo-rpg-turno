"""Testes para SkillEffectType enum."""

from __future__ import annotations

from src.core.skills.skill_effect_type import SkillEffectType


class TestSkillEffectType:
    def test_has_damage(self) -> None:
        assert SkillEffectType.DAMAGE is not None

    def test_has_heal(self) -> None:
        assert SkillEffectType.HEAL is not None

    def test_has_buff(self) -> None:
        assert SkillEffectType.BUFF is not None

    def test_has_debuff(self) -> None:
        assert SkillEffectType.DEBUFF is not None

    def test_has_apply_ailment(self) -> None:
        assert SkillEffectType.APPLY_AILMENT is not None

    def test_has_trigger_class_mechanic(self) -> None:
        assert SkillEffectType.TRIGGER_CLASS_MECHANIC is not None

    def test_has_resource_gain(self) -> None:
        assert SkillEffectType.RESOURCE_GAIN is not None

    def test_has_shield(self) -> None:
        assert SkillEffectType.SHIELD is not None

    def test_has_counter_attack(self) -> None:
        assert SkillEffectType.COUNTER_ATTACK is not None

    def test_has_grant_action(self) -> None:
        assert SkillEffectType.GRANT_ACTION is not None

    def test_has_ten_members(self) -> None:
        assert len(SkillEffectType) == 10
