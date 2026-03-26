"""ActionResolver — resolve PlayerAction em list[CombatEvent]."""

from __future__ import annotations

from typing import Callable

from src.core.characters.character import Character
from src.core.characters.position import Position
from src.core.combat.action_economy import ActionType
from src.core.combat.combat_engine import CombatEvent, EventType, TurnContext
from src.core.combat.consumable_effect_applier import apply_consumable_effect
from src.core.combat.damage import resolve_damage
from src.core.combat.player_action import PlayerAction, PlayerActionType
from src.core.combat.skill_effect_applier import apply_skill_effect
from src.core.combat.target_resolver import resolve_targets
from src.core.skills.class_resource_resolver import can_afford_all, spend_all
from src.core.effects.modifiable_stat import ModifiableStat
from src.core.items.consumable import Consumable
from src.core.skills.skill import Skill
from src.core.skills.target_type import TargetType

DEFEND_BUFF_PERCENT = 50.0
DEFEND_BUFF_DURATION = 1
DEFEND_SOURCE = "guard"


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
    result = resolve_damage(
        attack_power=context.combatant.attack_power,
        defense=target.defense_for(atk_type),
    )
    target.take_damage(result.final_damage)
    on_basic_attack(context.combatant)
    return [CombatEvent(
        round_number=context.round_number,
        actor_name=context.combatant.name,
        target_name=target.name,
        damage=result,
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
    if skill.mana_cost > context.combatant.current_mana:
        return []
    if not can_afford_all(context.combatant, skill.resource_costs):
        return []
    bar = context.combatant.skill_bar
    if not bar.cooldown_tracker.is_ready(skill.skill_id):
        return []
    if not context.action_economy.use(skill.action_type):
        return []
    context.combatant.spend_mana(skill.mana_cost)
    spend_all(context.combatant, skill.resource_costs)
    targets = _resolve_player_targets(skill.target_type, action, context)
    events: list[CombatEvent] = []
    for effect in skill.effects:
        events.extend(apply_skill_effect(
            effect, targets, context.round_number, context.combatant,
        ))
    _start_skill_cooldown(context.combatant, skill)
    return events


def _find_skill(skill_id: str, combatant: Character) -> Skill | None:
    bar = combatant.skill_bar
    if bar is None:
        return None
    return next(
        (s for s in bar.all_skills if s.skill_id == skill_id), None,
    )


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


_ITEM_ACTION_TYPE = ActionType.ACTION


def _resolve_item(
    action: PlayerAction, context: TurnContext,
) -> list[CombatEvent]:
    consumable = _find_consumable(action.consumable_id, context.combatant)
    if consumable is None:
        return []
    if consumable.mana_cost > context.combatant.current_mana:
        return []
    if not context.action_economy.use(_ITEM_ACTION_TYPE):
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


_ResolverFn = Callable[[PlayerAction, TurnContext], list[CombatEvent]]

_RESOLVERS: dict[PlayerActionType, _ResolverFn] = {
    PlayerActionType.BASIC_ATTACK: _resolve_basic_attack,
    PlayerActionType.MOVE: _resolve_move,
    PlayerActionType.DEFEND: _resolve_defend,
    PlayerActionType.END_TURN: _resolve_end_turn,
    PlayerActionType.SKILL: _resolve_skill,
    PlayerActionType.ITEM: _resolve_item,
}
