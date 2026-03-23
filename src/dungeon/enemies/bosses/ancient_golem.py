"""Ancient Golem — boss do Floor 2.

Phase 1 (>40% HP): Tank pesado, self-buff de defesa.
Phase 2 (<=40% HP): Modo agressivo com AoE stomp.
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
from src.dungeon.enemies.ai.target_selection import pick_highest_threat

if TYPE_CHECKING:
    from src.core.combat.combat_engine import CombatEvent, TurnContext

PHASE1_KEY = "ancient_golem_p1"
PHASE2_KEY = "ancient_golem_p2"


class AncientGolemPhase1:
    """Tanque defensivo: buff de defesa + ataque na maior ameaça."""

    def execute_turn(self, context: TurnContext) -> list[CombatEvent]:
        events: list[CombatEvent] = []
        events.extend(_try_defense_buff(context))
        events.extend(_attack_highest_threat(context))
        return events


class AncientGolemPhase2:
    """Modo agressivo: AoE stomp + ataque forte."""

    def execute_turn(self, context: TurnContext) -> list[CombatEvent]:
        events: list[CombatEvent] = []
        events.extend(_try_buff(context))
        events.extend(_try_aoe_stomp(context))
        return events


def _try_defense_buff(context: TurnContext) -> list[CombatEvent]:
    skills = get_usable_skills(context)
    buffs = filter_by_effect(skills, SkillEffectType.BUFF)
    bonus = [s for s in buffs if s.action_type == ActionType.BONUS_ACTION]
    if bonus:
        return execute_skill(bonus[0], context)
    return []


def _try_buff(context: TurnContext) -> list[CombatEvent]:
    skills = get_usable_skills(context)
    buffs = filter_by_effect(skills, SkillEffectType.BUFF)
    bonus = [s for s in buffs if s.action_type == ActionType.BONUS_ACTION]
    if bonus:
        return execute_skill(bonus[0], context)
    return []


def _try_aoe_stomp(context: TurnContext) -> list[CombatEvent]:
    skills = get_usable_skills(context)
    aoe = filter_by_effect(skills, SkillEffectType.DAMAGE)
    action_aoe = [s for s in aoe if s.action_type == ActionType.ACTION]
    if action_aoe:
        return execute_skill(action_aoe[0], context)
    return _attack_highest_threat(context)


def _attack_highest_threat(context: TurnContext) -> list[CombatEvent]:
    targets = get_valid_attack_targets(context)
    target = pick_highest_threat(targets)
    if target is None:
        return []
    return do_basic_attack(context, target)
