"""SkillHandler - TurnHandler que executa skills no combate."""

from __future__ import annotations

from src.core.combat.combat_engine import CombatEvent, EventType, TurnContext
from src.core.combat.skill_effect_applier import apply_skill_effect
from src.core.combat.target_resolver import resolve_targets
from src.core.skills.class_resource_resolver import can_afford_resource, spend_resource
from src.core.skills.skill import Skill
from src.core.skills.skill_effect_type import SkillEffectType
from src.core.skills.target_type import TargetType


class SkillHandler:
    """Seleciona e executa a primeira skill pronta com mana suficiente."""

    def execute_turn(self, context: TurnContext) -> list[CombatEvent]:
        skill = _pick_skill(context)
        if skill is None:
            return []
        return execute_skill(skill, context)


def _pick_skill(context: TurnContext) -> Skill | None:
    """Retorna primeira skill pronta com mana e action disponivel."""
    bar = context.combatant.skill_bar
    if bar is None:
        return None
    economy = context.action_economy
    mana = context.combatant.current_mana
    for skill in bar.ready_skills:
        if skill.mana_cost > mana:
            continue
        if not economy.is_available(skill.action_type):
            continue
        if not _can_afford_all_resources(context.combatant, skill):
            continue
        if _is_wasteful_heal(skill, context):
            continue
        return skill
    return None


def _is_wasteful_heal(skill: Skill, context: TurnContext) -> bool:
    """Pula skills puramente de heal se todos os aliados estao com HP cheio."""
    if not _is_pure_heal(skill):
        return False
    allies = _heal_targets(skill.target_type, context)
    return all(a.current_hp >= a.max_hp for a in allies)


def _is_pure_heal(skill: Skill) -> bool:
    return all(e.effect_type == SkillEffectType.HEAL for e in skill.effects)


def _heal_targets(target_type: TargetType, context: TurnContext):
    if target_type == TargetType.SELF:
        return [context.combatant]
    if target_type == TargetType.SINGLE_ALLY:
        return [a for a in context.allies if a.is_alive]
    if target_type == TargetType.ALL_ALLIES:
        return [a for a in context.allies if a.is_alive]
    return []


def _can_afford_all_resources(combatant: object, skill: Skill) -> bool:
    return all(
        can_afford_resource(combatant, cost)
        for cost in skill.resource_costs
    )


def _spend_all_resources(combatant: object, skill: Skill) -> None:
    for cost in skill.resource_costs:
        spend_resource(combatant, cost)


def execute_skill(skill: Skill, context: TurnContext) -> list[CombatEvent]:
    """Consome recursos e aplica efeitos da skill."""
    context.action_economy.use(skill.action_type)
    context.combatant.spend_mana(skill.mana_cost)
    _spend_all_resources(context.combatant, skill)
    targets = resolve_targets(skill.target_type, context)
    events: list[CombatEvent] = []
    for effect in skill.effects:
        events.extend(apply_skill_effect(
            effect, targets, context.round_number,
            context.combatant,
        ))
    _start_cooldown(context, skill)
    return events


def _start_cooldown(context: TurnContext, skill: Skill) -> None:
    """Inicia cooldown da skill se aplicavel."""
    bar = context.combatant.skill_bar
    if bar is not None and skill.cooldown_turns > 0:
        bar.cooldown_tracker.start_cooldown(
            skill.skill_id, skill.cooldown_turns,
        )
