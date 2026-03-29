"""QTE multiplier — applies QteResult multiplier to SkillEffects."""

from __future__ import annotations

from dataclasses import replace

from src.core.combat.qte.qte_config import QteResult
from src.core.skills.skill_effect import SkillEffect
from src.core.skills.skill_effect_type import SkillEffectType

_SCALABLE_TYPES = frozenset({SkillEffectType.DAMAGE, SkillEffectType.HEAL})


def apply_qte_multiplier(
    effects: tuple[SkillEffect, ...],
    qte_result: QteResult,
) -> tuple[SkillEffect, ...]:
    """Returns new SkillEffects with base_power scaled by QTE multiplier.

    Only DAMAGE and HEAL effects are scaled.
    Buffs, debuffs, ailments, etc. are returned unchanged.
    """
    if qte_result.multiplier == 1.0:
        return effects
    return tuple(_scale_effect(e, qte_result.multiplier) for e in effects)


def _scale_effect(
    effect: SkillEffect, multiplier: float,
) -> SkillEffect:
    if effect.effect_type not in _SCALABLE_TYPES:
        return effect
    new_power = int(effect.base_power * multiplier)
    return replace(effect, base_power=new_power)
