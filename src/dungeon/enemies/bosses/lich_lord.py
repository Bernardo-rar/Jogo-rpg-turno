"""Lich Lord — boss do Floor 3.

Phase 1 (>50% HP): Magia forte + debuffs.
Phase 2 (<=50% HP): Desespero — AoE + ailments agressivos.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.core.combat.action_economy import ActionType
from src.core.combat.skill_handler import execute_skill
from src.core.skills.skill_effect_type import SkillEffectType
from src.dungeon.enemies.ai.ai_utils import (
    do_basic_attack,
    filter_by_effect,
    get_usable_skills,
    get_valid_attack_targets,
)
from src.dungeon.enemies.ai.target_selection import (
    pick_highest_threat,
    pick_lowest_hp_ratio,
)

if TYPE_CHECKING:
    from src.core.combat.combat_engine import CombatEvent, TurnContext

PHASE1_KEY = "lich_lord_p1"
PHASE2_KEY = "lich_lord_p2"


class LichLordPhase1:
    """Magia forte: debuff maior ameaça + ataque mágico."""

    def execute_turn(self, context: TurnContext) -> list[CombatEvent]:
        events: list[CombatEvent] = []
        events.extend(_try_debuff(context))
        events.extend(_try_damage_skill_or_attack(context))
        return events


class LichLordPhase2:
    """Desespero: AoE ailment + AoE damage agressivo."""

    def execute_turn(self, context: TurnContext) -> list[CombatEvent]:
        events: list[CombatEvent] = []
        events.extend(_try_ailment(context))
        events.extend(_try_aoe_or_attack(context))
        return events


def _try_debuff(context: TurnContext) -> list[CombatEvent]:
    skills = get_usable_skills(context)
    debuffs = filter_by_effect(skills, SkillEffectType.DEBUFF)
    bonus = [s for s in debuffs if s.action_type == ActionType.BONUS_ACTION]
    if bonus:
        return execute_skill(bonus[0], context)
    return []


def _try_ailment(context: TurnContext) -> list[CombatEvent]:
    skills = get_usable_skills(context)
    ailments = filter_by_effect(skills, SkillEffectType.APPLY_AILMENT)
    bonus = [s for s in ailments if s.action_type == ActionType.BONUS_ACTION]
    if bonus:
        return execute_skill(bonus[0], context)
    action = [s for s in ailments if s.action_type == ActionType.ACTION]
    if action:
        return execute_skill(action[0], context)
    return []


def _try_damage_skill_or_attack(
    context: TurnContext,
) -> list[CombatEvent]:
    skills = get_usable_skills(context)
    damage = filter_by_effect(skills, SkillEffectType.DAMAGE)
    action_dmg = [s for s in damage if s.action_type == ActionType.ACTION]
    if action_dmg:
        return execute_skill(action_dmg[0], context)
    return _attack_target(context, pick_highest_threat)


def _try_aoe_or_attack(context: TurnContext) -> list[CombatEvent]:
    skills = get_usable_skills(context)
    damage = filter_by_effect(skills, SkillEffectType.DAMAGE)
    action_dmg = [s for s in damage if s.action_type == ActionType.ACTION]
    if action_dmg:
        return execute_skill(action_dmg[0], context)
    return _attack_target(context, pick_lowest_hp_ratio)


def _attack_target(context: TurnContext, picker) -> list[CombatEvent]:
    targets = get_valid_attack_targets(context)
    target = picker(targets)
    if target is None:
        return []
    return do_basic_attack(context, target)
