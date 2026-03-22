"""DpsHandler - IA de archetype DPS: maximiza dano."""

from __future__ import annotations

from src.core.combat.action_economy import ActionType
from src.core.combat.combat_engine import CombatEvent, TurnContext
from src.core.combat.skill_handler import execute_skill
from src.core.skills.skill_effect_type import SkillEffectType
from src.core.skills.target_type import TargetType
from src.dungeon.enemies.ai.ai_utils import (
    do_basic_attack,
    filter_by_effect,
    get_usable_skills,
    get_valid_attack_targets,
)
from src.dungeon.enemies.ai.target_selection import (
    pick_backline_targets,
    pick_lowest_hp_ratio,
)

_AOE_TARGET_THRESHOLD = 3


class DpsHandler:
    """AoE se 3+ alvos -> backline lowest HP -> any lowest HP."""

    def execute_turn(self, context: TurnContext) -> list[CombatEvent]:
        events: list[CombatEvent] = []
        events.extend(_try_bonus_buff(context))
        events.extend(_try_main_action(context))
        return events


def _try_bonus_buff(context: TurnContext) -> list[CombatEvent]:
    """Usa buff de bonus action se disponivel."""
    skills = get_usable_skills(context)
    buffs = [
        s for s in skills
        if s.action_type == ActionType.BONUS_ACTION
        and SkillEffectType.BUFF in {e.effect_type for e in s.effects}
    ]
    if not buffs:
        return []
    return execute_skill(buffs[0], context)


def _try_main_action(context: TurnContext) -> list[CombatEvent]:
    """AoE se 3+ inimigos, senao ataque basico no melhor alvo."""
    alive_enemies = [e for e in context.enemies if e.is_alive]
    if len(alive_enemies) >= _AOE_TARGET_THRESHOLD:
        aoe = _pick_aoe_skill(context)
        if aoe:
            return execute_skill(aoe, context)
    target = _pick_dps_target(context)
    if target is None:
        return []
    return do_basic_attack(context, target)


def _pick_aoe_skill(context: TurnContext):
    skills = get_usable_skills(context)
    aoe_damage = [
        s for s in skills
        if s.target_type == TargetType.ALL_ENEMIES
        and SkillEffectType.DAMAGE in {e.effect_type for e in s.effects}
    ]
    return aoe_damage[0] if aoe_damage else None


def _pick_dps_target(context: TurnContext):
    """Backline -> lowest HP entre alvos validos."""
    valid = get_valid_attack_targets(context)
    if not valid:
        return None
    backline = pick_backline_targets(valid)
    if backline:
        return pick_lowest_hp_ratio(backline)
    return pick_lowest_hp_ratio(valid)
