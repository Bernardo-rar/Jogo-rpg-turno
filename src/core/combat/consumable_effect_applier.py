"""Aplica efeitos de Consumable aos alvos, retornando CombatEvents."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from src.core.combat.combat_engine import CombatEvent, EventType
from src.core.combat.damage import resolve_damage
from src.core.effects.buff_factory import create_flat_buff
from src.core.effects.stat_buff import StatBuff
from src.core.items.consumable_effect import ConsumableEffect
from src.core.items.consumable_effect_type import ConsumableEffectType

if TYPE_CHECKING:
    from src.core.characters.character import Character


def apply_consumable_effect(
    effect: ConsumableEffect, targets: list[Character],
    rnd: int, actor: str,
) -> list[CombatEvent]:
    """Aplica um ConsumableEffect a todos os alvos."""
    applier = _APPLIERS.get(effect.effect_type)
    if applier is None:
        return []
    return applier(effect, targets, rnd, actor)


def _apply_heal_hp(
    effect: ConsumableEffect, targets: list[Character],
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


def _apply_heal_mana(
    effect: ConsumableEffect, targets: list[Character],
    rnd: int, actor: str,
) -> list[CombatEvent]:
    events: list[CombatEvent] = []
    for target in targets:
        restored = target.restore_mana(effect.base_power)
        events.append(CombatEvent(
            round_number=rnd, actor_name=actor,
            target_name=target.name,
            event_type=EventType.MANA_RESTORE, value=restored,
        ))
    return events


def _apply_damage(
    effect: ConsumableEffect, targets: list[Character],
    rnd: int, actor: str,
) -> list[CombatEvent]:
    events: list[CombatEvent] = []
    for target in targets:
        defense = target.physical_defense
        if effect.element is not None:
            defense = target.magical_defense
        result = resolve_damage(
            attack_power=effect.base_power, defense=defense,
        )
        target.take_damage(result.final_damage)
        events.append(CombatEvent(
            round_number=rnd, actor_name=actor,
            target_name=target.name, damage=result,
        ))
    return events


def _apply_buff(
    effect: ConsumableEffect, targets: list[Character],
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


def _apply_cleanse(
    effect: ConsumableEffect, targets: list[Character],
    rnd: int, actor: str,
) -> list[CombatEvent]:
    events: list[CombatEvent] = []
    for target in targets:
        _remove_negative_effects(target)
        events.append(CombatEvent(
            round_number=rnd, actor_name=actor,
            target_name=target.name,
            event_type=EventType.CLEANSE,
            description="cleanse",
        ))
    return events


def _remove_negative_effects(target: Character) -> None:
    """Remove todos os efeitos que NAO sao StatBuff."""
    negatives = [
        e for e in target.effect_manager.active_effects
        if not isinstance(e, StatBuff)
    ]
    for effect in negatives:
        target.effect_manager.remove_effect(effect)


def _apply_flee(
    effect: ConsumableEffect, targets: list[Character],
    rnd: int, actor: str,
) -> list[CombatEvent]:
    return [CombatEvent(
        round_number=rnd, actor_name=actor,
        target_name="", event_type=EventType.FLEE,
    )]


_APPLIERS: dict[ConsumableEffectType, Callable[..., list[CombatEvent]]] = {
    ConsumableEffectType.HEAL_HP: _apply_heal_hp,
    ConsumableEffectType.HEAL_MANA: _apply_heal_mana,
    ConsumableEffectType.DAMAGE: _apply_damage,
    ConsumableEffectType.BUFF: _apply_buff,
    ConsumableEffectType.CLEANSE: _apply_cleanse,
    ConsumableEffectType.FLEE: _apply_flee,
}
