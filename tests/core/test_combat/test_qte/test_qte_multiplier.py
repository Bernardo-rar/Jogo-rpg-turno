"""Tests for QTE multiplier — applies QteResult to SkillEffects."""

from src.core.combat.qte.qte_config import QteOutcome, QteResult
from src.core.combat.qte.qte_multiplier import apply_qte_multiplier
from src.core.skills.skill_effect import SkillEffect
from src.core.skills.skill_effect_type import SkillEffectType


def _dmg_effect(power: int = 100) -> SkillEffect:
    return SkillEffect(
        effect_type=SkillEffectType.DAMAGE,
        base_power=power,
    )


def _heal_effect(power: int = 50) -> SkillEffect:
    return SkillEffect(
        effect_type=SkillEffectType.HEAL,
        base_power=power,
    )


def _perfect() -> QteResult:
    return QteResult(QteOutcome.PERFECT, 3, 3, 1.30)


def _partial() -> QteResult:
    return QteResult(QteOutcome.PARTIAL, 2, 4, 1.15)


def _failure() -> QteResult:
    return QteResult(QteOutcome.FAILURE, 0, 3, 0.90)


def _skipped() -> QteResult:
    return QteResult(QteOutcome.SKIPPED, 0, 0, 1.0)


class TestApplyQteMultiplier:

    def test_perfect_boosts_damage(self) -> None:
        effects = ((_dmg_effect(100),))
        scaled = apply_qte_multiplier(effects, _perfect())
        assert scaled[0].base_power == 130

    def test_partial_boosts_heal(self) -> None:
        effects = ((_heal_effect(50),))
        scaled = apply_qte_multiplier(effects, _partial())
        assert scaled[0].base_power == 57  # int(50 * 1.15)

    def test_failure_reduces_damage(self) -> None:
        effects = ((_dmg_effect(100),))
        scaled = apply_qte_multiplier(effects, _failure())
        assert scaled[0].base_power == 90

    def test_skipped_no_change(self) -> None:
        effects = ((_dmg_effect(100),))
        scaled = apply_qte_multiplier(effects, _skipped())
        assert scaled[0].base_power == 100

    def test_multiple_effects_all_scaled(self) -> None:
        effects = (_dmg_effect(100), _heal_effect(50))
        scaled = apply_qte_multiplier(effects, _perfect())
        assert scaled[0].base_power == 130
        assert scaled[1].base_power == 65

    def test_buff_effect_not_scaled(self) -> None:
        buff = SkillEffect(
            effect_type=SkillEffectType.BUFF,
            base_power=10,
            stat="PHYSICAL_ATTACK",
            duration=3,
        )
        scaled = apply_qte_multiplier((buff,), _perfect())
        assert scaled[0].base_power == 10
