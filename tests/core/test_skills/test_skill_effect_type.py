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

    def test_has_five_members(self) -> None:
        assert len(SkillEffectType) == 5
