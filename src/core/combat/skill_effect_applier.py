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
    actor_name: str,
) -> list[CombatEvent]:
    """Aplica um SkillEffect a todos os alvos. Retorna eventos gerados."""
    applier = _APPLIERS.get(effect.effect_type)
    if applier is None:
        return []
    return applier(effect, targets, context_round, actor_name)


def _apply_damage(
    effect: SkillEffect, targets: list[Character],
    rnd: int, actor: str,
) -> list[CombatEvent]:
    events: list[CombatEvent] = []
    for target in targets:
        defense = _pick_defense(effect, target)
        result = resolve_damage(
            attack_power=effect.base_power, defense=defense,
        )
        target.take_damage(result.final_damage)
        events.append(CombatEvent(
            round_number=rnd, actor_name=actor,
            target_name=target.name, damage=result,
        ))
    return events


def _pick_defense(effect: SkillEffect, target: Character) -> int:
    if effect.element is not None:
        return target.magical_defense
    return target.physical_defense


def _apply_heal(
    effect: SkillEffect, targets: list[Character],
    rnd: int, actor: str,
) -> list[CombatEvent]:
    events: list[CombatEvent] = []
    for target in targets:
        healed = target.heal(effect.base_power)
        events.append(CombatEvent(
            round_number=rnd, actor_name=actor,
            target_name=target.name,
            event_type=EventType.HEAL, value=healed,
        ))
    return events


def _apply_buff(
    effect: SkillEffect, targets: list[Character],
    rnd: int, actor: str,
) -> list[CombatEvent]:
    if effect.stat is None:
        return []
    events: list[CombatEvent] = []
    for target in targets:
        buff = create_flat_buff(effect.stat, effect.base_power, effect.duration)
        target.effect_manager.add_effect(buff)
        events.append(CombatEvent(
            round_number=rnd, actor_name=actor,
            target_name=target.name,
            event_type=EventType.BUFF, value=effect.base_power,
        ))
    return events


def _apply_debuff(
    effect: SkillEffect, targets: list[Character],
    rnd: int, actor: str,
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
            round_number=rnd, actor_name=actor,
            target_name=target.name,
            event_type=EventType.DEBUFF, value=effect.base_power,
        ))
    return events


def _apply_ailment(
    effect: SkillEffect, targets: list[Character],
    rnd: int, actor: str,
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
            round_number=rnd, actor_name=actor,
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
