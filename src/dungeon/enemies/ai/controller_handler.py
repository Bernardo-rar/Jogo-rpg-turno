"""ControllerHandler - IA de archetype CONTROLLER: CC e debuff."""

from __future__ import annotations

from src.core.combat.combat_engine import CombatEvent, TurnContext
from src.core.combat.skill_handler import execute_skill
from src.core.skills.skill_effect_type import SkillEffectType
from src.dungeon.enemies.ai.ai_utils import (
    do_basic_attack,
    filter_by_effect,
    get_usable_skills,
    get_valid_attack_targets,
)
from src.dungeon.enemies.ai.target_selection import pick_highest_threat


class ControllerHandler:
    """CC highest threat -> debuff se ja CC'd -> basic attack."""

    def execute_turn(self, context: TurnContext) -> list[CombatEvent]:
        cc_events = _try_cc(context)
        if cc_events:
            return cc_events
        debuff_events = _try_debuff(context)
        if debuff_events:
            return debuff_events
        return _fallback_attack(context)


def _try_cc(context: TurnContext) -> list[CombatEvent]:
    """Aplica ailment no alvo mais perigoso."""
    skills = get_usable_skills(context)
    cc_skills = filter_by_effect(skills, SkillEffectType.APPLY_AILMENT)
    if not cc_skills:
        return []
    return execute_skill(cc_skills[0], context)


def _try_debuff(context: TurnContext) -> list[CombatEvent]:
    """Aplica debuff se nao tem CC disponivel."""
    skills = get_usable_skills(context)
    debuffs = filter_by_effect(skills, SkillEffectType.DEBUFF)
    if not debuffs:
        return []
    return execute_skill(debuffs[0], context)


def _fallback_attack(context: TurnContext) -> list[CombatEvent]:
    """Ataque basico no alvo mais perigoso."""
    valid = get_valid_attack_targets(context)
    target = pick_highest_threat(valid) if valid else None
    if target is None:
        return []
    return do_basic_attack(context, target)
