"""ActionResolver — resolve PlayerAction em list[CombatEvent]."""

from __future__ import annotations

from typing import Callable

from src.core.characters.character import Character
from src.core.characters.position import Position
from src.core.combat.position_modifiers import scale_dealt, scale_taken
from src.core.combat.action_economy import ActionEconomy, ActionType
from src.core.combat.combat_engine import CombatEvent, EventType, TurnContext
from src.core.combat.consumable_effect_applier import apply_consumable_effect
from src.core.combat.damage import DamageResult, resolve_damage
from src.core.combat.player_action import PlayerAction, PlayerActionType
from src.core.combat.qte.qte_config import QteResult
from src.core.combat.skill_effect_applier import (
    apply_skill_effect,
    get_run_modifier_effect,
)
from src.core.combat.target_resolver import resolve_targets
from src.core.skills.class_resource_resolver import can_afford_all, spend_all
from src.core.effects.modifiable_stat import ModifiableStat
from src.core.items.consumable import Consumable
from src.core.skills.skill import Skill
from src.core.skills.skill_effect import SkillEffect
from src.core.skills.skill_effect_type import SkillEffectType
from src.core.skills.target_type import TargetType

DEFEND_BUFF_PERCENT = 50.0
DEFEND_BUFF_DURATION = 1
DEFEND_SOURCE = "guard"

_pending_qte_result: QteResult | None = None


def set_qte_result(result: QteResult | None) -> None:
    """Set by UI before resolving a skill with QTE."""
    global _pending_qte_result
    _pending_qte_result = result


def get_qte_result() -> QteResult | None:
    """Consumes the pending QTE result (one-shot)."""
    global _pending_qte_result
    result = _pending_qte_result
    _pending_qte_result = None
    return result


def resolve_player_action(
    action: PlayerAction,
    context: TurnContext,
) -> list[CombatEvent]:
    """Resolve uma acao do jogador em eventos de combate."""
    resolver = _RESOLVERS.get(action.action_type)
    if resolver is None:
        return []
    return resolver(action, context)


def _resolve_basic_attack(
    action: PlayerAction, context: TurnContext,
) -> list[CombatEvent]:
    from src.core.combat.basic_attack_resource import on_basic_attack

    if not context.action_economy.use(ActionType.ACTION):
        return []
    target = _find_alive_target(action.target_name, context)
    if target is None:
        return []
    atk_type = context.combatant.preferred_attack_type
    raw_atk = scale_dealt(context.combatant.attack_power, context.combatant.position)
    attack = _apply_dealt_mult(raw_atk)
    result = resolve_damage(
        attack_power=attack,
        defense=target.defense_for(atk_type),
    )
    raw_final = scale_taken(result.final_damage, target.position)
    final = _apply_taken_mult(raw_final)
    target.take_damage(final)
    on_basic_attack(context.combatant)
    scaled = _replace_final(result, final)
    return [CombatEvent(
        round_number=context.round_number,
        actor_name=context.combatant.name,
        target_name=target.name,
        damage=scaled,
    )]


def _resolve_move(
    action: PlayerAction, context: TurnContext,
) -> list[CombatEvent]:
    if not context.action_economy.use(ActionType.BONUS_ACTION):
        return []
    combatant = context.combatant
    new_pos = _opposite_position(combatant.position)
    combatant.change_position(new_pos)
    return [CombatEvent(
        round_number=context.round_number,
        actor_name=combatant.name,
        target_name=combatant.name,
        event_type=EventType.SKILL_USE,
        description=f"Moved to {new_pos.name}",
    )]


def _resolve_defend(
    action: PlayerAction, context: TurnContext,
) -> list[CombatEvent]:
    if not context.action_economy.use(ActionType.REACTION):
        return []
    combatant = context.combatant
    _apply_guard_buffs(combatant)
    return [CombatEvent(
        round_number=context.round_number,
        actor_name=combatant.name,
        target_name=combatant.name,
        event_type=EventType.BUFF,
        description="Defending",
    )]


def _resolve_end_turn(
    action: PlayerAction, context: TurnContext,
) -> list[CombatEvent]:
    return []


def _apply_guard_buffs(combatant: Character) -> None:
    from src.core.effects.stat_buff import StatBuff
    from src.core.effects.stat_modifier import StatModifier

    phys_mod = StatModifier(
        stat=ModifiableStat.PHYSICAL_DEFENSE, percent=DEFEND_BUFF_PERCENT,
    )
    mag_mod = StatModifier(
        stat=ModifiableStat.MAGICAL_DEFENSE, percent=DEFEND_BUFF_PERCENT,
    )
    combatant.effect_manager.add_effect(
        StatBuff(phys_mod, DEFEND_BUFF_DURATION, source=DEFEND_SOURCE),
    )
    combatant.effect_manager.add_effect(
        StatBuff(mag_mod, DEFEND_BUFF_DURATION, source=DEFEND_SOURCE),
    )


def _find_alive_target(
    name: str, context: TurnContext,
) -> Character | None:
    all_chars = context.allies + context.enemies
    for char in all_chars:
        if char.name == name and char.is_alive:
            return char
    return None


def _opposite_position(position: Position) -> Position:
    if position == Position.FRONT:
        return Position.BACK
    return Position.FRONT


def _resolve_skill(
    action: PlayerAction, context: TurnContext,
) -> list[CombatEvent]:
    skill = _find_skill(action.skill_id, context.combatant)
    if skill is None:
        return []
    if not _can_use_skill(skill, context):
        return []
    if not context.action_economy.use(skill.action_type):
        return []
    context.combatant.spend_mana(skill.mana_cost)
    spend_all(context.combatant, skill.resource_costs)
    targets = _resolve_player_targets(skill.target_type, action, context)
    effects = _maybe_apply_qte(skill)
    events: list[CombatEvent] = []
    for effect in effects:
        events.extend(apply_skill_effect(
            effect, targets, context.round_number, context.combatant,
        ))
    _grant_player_actions(skill, context.action_economy)
    _start_skill_cooldown(context.combatant, skill)
    return events


def _can_use_skill(skill: Skill, context: TurnContext) -> bool:
    """Verifica se o jogador pode usar a skill."""
    if skill.mana_cost > context.combatant.current_mana:
        return False
    if not can_afford_all(context.combatant, skill.resource_costs):
        return False
    bar = context.combatant.skill_bar
    return bar.cooldown_tracker.is_ready(skill.skill_id)


def _find_skill(skill_id: str, combatant: Character) -> Skill | None:
    bar = combatant.skill_bar
    if bar is None:
        return None
    return next(
        (s for s in bar.all_skills if s.skill_id == skill_id), None,
    )


def _grant_player_actions(skill: Skill, economy: ActionEconomy) -> None:
    """Aplica GRANT_ACTION effects da skill na economy do jogador."""
    for effect in skill.effects:
        if effect.effect_type == SkillEffectType.GRANT_ACTION:
            _grant_single_player(effect, economy)


def _grant_single_player(effect: SkillEffect, economy: ActionEconomy) -> None:
    """Concede uma acao baseado no resource_type do effect."""
    action_type = _parse_grant_action_type(effect)
    if action_type is not None:
        economy.grant(action_type)


def _parse_grant_action_type(effect: SkillEffect) -> ActionType | None:
    """Converte resource_type string em ActionType enum."""
    if effect.resource_type is None:
        return None
    try:
        return ActionType[effect.resource_type.upper()]
    except KeyError:
        return None


def _start_skill_cooldown(combatant: Character, skill: Skill) -> None:
    bar = combatant.skill_bar
    if bar is not None and skill.cooldown_turns > 0:
        bar.cooldown_tracker.start_cooldown(
            skill.skill_id, skill.cooldown_turns,
        )


def _resolve_player_targets(
    target_type: TargetType, action: PlayerAction,
    context: TurnContext,
) -> list[Character]:
    """Resolve alvos: auto para SELF/ALL_*, busca por nome para SINGLE_*."""
    if target_type in _AUTO_TARGET_TYPES:
        return resolve_targets(target_type, context)
    target = _find_alive_target(action.target_name, context)
    return [target] if target is not None else []


_AUTO_TARGET_TYPES = frozenset({
    TargetType.SELF, TargetType.ALL_ALLIES, TargetType.ALL_ENEMIES,
})


_ITEM_ACTION_TYPE = ActionType.BONUS_ACTION


def _resolve_item(
    action: PlayerAction, context: TurnContext,
) -> list[CombatEvent]:
    consumable = _find_consumable(action.consumable_id, context.combatant)
    if consumable is None:
        return []
    if consumable.mana_cost > context.combatant.current_mana:
        return []
    if not _spend_item_action(context):
        return []
    context.combatant.spend_mana(consumable.mana_cost)
    targets = _resolve_player_targets(
        consumable.target_type, action, context,
    )
    events: list[CombatEvent] = []
    for effect in consumable.effects:
        events.extend(apply_consumable_effect(
            effect, targets, context.round_number,
            context.combatant.name,
        ))
    _remove_from_inventory(context.combatant, consumable)
    return events


def _find_consumable(
    consumable_id: str, combatant: Character,
) -> Consumable | None:
    inv = combatant.inventory
    if inv is None:
        return None
    slot = inv.get_slot(consumable_id)
    return slot.consumable if slot is not None else None


def _remove_from_inventory(
    combatant: Character, item: Consumable,
) -> None:
    if combatant.inventory is not None:
        combatant.inventory.remove_item(item.consumable_id)


def _spend_item_action(context: TurnContext) -> bool:
    """Gasta acao pra usar item. Rogue usa de graca (1x por turno)."""
    has_free = getattr(context.combatant, "free_item_use", False)
    if has_free:
        return True
    return context.action_economy.use(_ITEM_ACTION_TYPE)


def _maybe_apply_qte(skill: Skill) -> tuple[SkillEffect, ...]:
    """Applies QTE multiplier to skill effects if QTE result is pending."""
    if skill.qte is None:
        return skill.effects
    qte_result = get_qte_result()
    if qte_result is None:
        return skill.effects
    from src.core.combat.qte.qte_multiplier import apply_qte_multiplier
    return apply_qte_multiplier(skill.effects, qte_result)


def _apply_dealt_mult(attack_power: int) -> int:
    """Aplica damage_dealt_mult do modifier de run."""
    mod = get_run_modifier_effect()
    if mod is None:
        return attack_power
    return int(attack_power * mod.damage_dealt_mult)


def _apply_taken_mult(final: int) -> int:
    """Aplica damage_taken_mult do modifier de run."""
    mod = get_run_modifier_effect()
    if mod is None:
        return final
    return max(1, int(final * mod.damage_taken_mult))


def _replace_final(result: DamageResult, final: int) -> DamageResult:
    """Cria DamageResult com final_damage atualizado."""
    if result.final_damage == final:
        return result
    return DamageResult(
        raw_damage=result.raw_damage,
        defense_value=result.defense_value,
        is_critical=result.is_critical,
        final_damage=final,
    )


_ResolverFn = Callable[[PlayerAction, TurnContext], list[CombatEvent]]

_RESOLVERS: dict[PlayerActionType, _ResolverFn] = {
    PlayerActionType.BASIC_ATTACK: _resolve_basic_attack,
    PlayerActionType.MOVE: _resolve_move,
    PlayerActionType.DEFEND: _resolve_defend,
    PlayerActionType.END_TURN: _resolve_end_turn,
    PlayerActionType.SKILL: _resolve_skill,
    PlayerActionType.ITEM: _resolve_item,
}
