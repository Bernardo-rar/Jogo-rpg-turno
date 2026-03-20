"""Aplica efeitos de Skill aos alvos, retornando CombatEvents."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from src.core.combat.combat_engine import CombatEvent, EventType
from src.core.combat.damage import resolve_damage
from src.core.effects.ailments.ailment_factory import (
    create_bleed,
    create_burn,
    create_poison,
)
from src.core.effects.buff_factory import create_flat_buff, create_flat_debuff
from src.core.skills.skill_effect import SkillEffect
from src.core.skills.skill_effect_type import SkillEffectType

if TYPE_CHECKING:
    from src.core.characters.character import Character

_DEFAULT_AILMENT_DURATION = 3


def apply_skill_effect(
    effect: SkillEffect, targets: list[Character], context_round: int,
    combatant: Character,
) -> list[CombatEvent]:
    """Aplica um SkillEffect a todos os alvos. Retorna eventos gerados."""
    applier = _APPLIERS.get(effect.effect_type)
    if applier is None:
        return []
    return applier(effect, targets, context_round, combatant)


def _apply_damage(
    effect: SkillEffect, targets: list[Character],
    rnd: int, combatant: Character,
) -> list[CombatEvent]:
    events: list[CombatEvent] = []
    attack = effect.base_power + _pick_attack(effect, combatant)
    for target in targets:
        defense = _pick_defense(effect, target)
        result = resolve_damage(attack_power=attack, defense=defense)
        target.take_damage(result.final_damage)
        events.append(CombatEvent(
            round_number=rnd, actor_name=combatant.name,
            target_name=target.name, damage=result,
            element=effect.element,
        ))
    return events


def _pick_attack(effect: SkillEffect, combatant: Character) -> int:
    if effect.element is not None:
        return combatant.magical_attack
    return combatant.physical_attack


def _pick_defense(effect: SkillEffect, target: Character) -> int:
    if effect.element is not None:
        return target.magical_defense
    return target.physical_defense


def _apply_heal(
    effect: SkillEffect, targets: list[Character],
    rnd: int, combatant: Character,
) -> list[CombatEvent]:
    events: list[CombatEvent] = []
    heal_power = effect.base_power + combatant.magical_attack
    for target in targets:
        healed = target.heal(heal_power)
        events.append(CombatEvent(
            round_number=rnd, actor_name=combatant.name,
            target_name=target.name,
            event_type=EventType.HEAL, value=healed,
        ))
    return events


def _apply_buff(
    effect: SkillEffect, targets: list[Character],
    rnd: int, combatant: Character,
) -> list[CombatEvent]:
    if effect.stat is None:
        return []
    events: list[CombatEvent] = []
    for target in targets:
        buff = create_flat_buff(effect.stat, effect.base_power, effect.duration)
        target.effect_manager.add_effect(buff)
        events.append(CombatEvent(
            round_number=rnd, actor_name=combatant.name,
            target_name=target.name,
            event_type=EventType.BUFF, value=effect.base_power,
            description=effect.stat.name.lower(),
        ))
    return events


def _apply_debuff(
    effect: SkillEffect, targets: list[Character],
    rnd: int, combatant: Character,
) -> list[CombatEvent]:
    if effect.stat is None:
        return []
    events: list[CombatEvent] = []
    for target in targets:
        debuff = create_flat_debuff(
            effect.stat, effect.base_power, effect.duration,
        )
        target.effect_manager.add_effect(debuff)
        events.append(CombatEvent(
            round_number=rnd, actor_name=combatant.name,
            target_name=target.name,
            event_type=EventType.DEBUFF, value=effect.base_power,
            description=effect.stat.name.lower(),
        ))
    return events


def _apply_ailment(
    effect: SkillEffect, targets: list[Character],
    rnd: int, combatant: Character,
) -> list[CombatEvent]:
    factory = _AILMENT_FACTORIES.get(effect.ailment_id or "")
    if factory is None:
        return []
    events: list[CombatEvent] = []
    dur = effect.duration or _DEFAULT_AILMENT_DURATION
    for target in targets:
        ailment = factory(effect.base_power, dur)
        target.effect_manager.add_effect(ailment)
        events.append(CombatEvent(
            round_number=rnd, actor_name=combatant.name,
            target_name=target.name,
            event_type=EventType.AILMENT,
            description=effect.ailment_id or "",
        ))
    return events


_APPLIERS: dict[SkillEffectType, Callable[..., list[CombatEvent]]] = {
    SkillEffectType.DAMAGE: _apply_damage,
    SkillEffectType.HEAL: _apply_heal,
    SkillEffectType.BUFF: _apply_buff,
    SkillEffectType.DEBUFF: _apply_debuff,
    SkillEffectType.APPLY_AILMENT: _apply_ailment,
}

_AILMENT_FACTORIES: dict[str, Callable[..., object]] = {
    "poison": create_poison,
    "burn": create_burn,
    "bleed": create_bleed,
}
