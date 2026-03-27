"""Aplica efeitos de Skill aos alvos, retornando CombatEvents."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from src.core.combat.combat_engine import CombatEvent, EventType
from src.core.combat.damage import resolve_damage
from src.core.elements.combo.combo_detector import ComboDetector
from src.core.elements.combo.combo_resolver import ComboOutcome, resolve_combo
from src.core.elements.combo.element_marker import ElementMarker
from src.core.elements.element_type import ElementType
from src.core.effects.ailments.ailment_factory import (
    create_amnesia,
    create_bleed,
    create_burn,
    create_cold,
    create_confusion,
    create_curse,
    create_freeze,
    create_injury,
    create_paralysis,
    create_poison,
    create_scorch,
    create_sickness,
    create_virus,
    create_weakness,
)
from src.core.effects.buff_factory import create_flat_buff, create_flat_debuff
from src.core.skills.skill_effect import SkillEffect
from src.core.skills.skill_effect_type import SkillEffectType

if TYPE_CHECKING:
    from src.core.characters.character import Character

_DEFAULT_AILMENT_DURATION = 3

_combo_detector: ComboDetector | None = None


def set_combo_detector(detector: ComboDetector | None) -> None:
    """Configura o ComboDetector usado pelo fluxo de dano."""
    global _combo_detector  # noqa: PLW0603
    _combo_detector = detector


def get_combo_detector() -> ComboDetector | None:
    """Retorna o ComboDetector atual (ou None se nao configurado)."""
    return _combo_detector


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
        if effect.element is not None:
            events.extend(_handle_elemental_combo(
                effect.element, target, rnd, combatant,
            ))
    return events


def _handle_elemental_combo(
    element: ElementType, target: Character,
    rnd: int, combatant: Character,
) -> list[CombatEvent]:
    """Adiciona marker elemental e resolve combo se houver."""
    target.effect_manager.add_effect(ElementMarker(element))
    outcome = resolve_combo(
        element, target.effect_manager, _combo_detector,
    )
    if outcome is None:
        return []
    return _apply_combo_bonus(outcome, target, rnd, combatant)


def _apply_combo_bonus(
    outcome: ComboOutcome, target: Character,
    rnd: int, combatant: Character,
) -> list[CombatEvent]:
    """Aplica dano bonus do combo e retorna evento."""
    if outcome.bonus_damage > 0:
        target.take_damage(outcome.bonus_damage)
    return [CombatEvent(
        round_number=rnd, actor_name=combatant.name,
        target_name=target.name,
        event_type=EventType.DAMAGE,
        value=outcome.bonus_damage,
        description=outcome.combo_name,
    )]


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


def _apply_trigger_mechanic(
    effect: SkillEffect, targets: list[Character],
    rnd: int, combatant: Character,
) -> list[CombatEvent]:
    """Ativa mecanica de classe via mechanic_id dispatch."""
    if effect.mechanic_id is None:
        return []
    handler = _MECHANIC_DISPATCH.get(effect.mechanic_id)
    if handler is None:
        return []
    events: list[CombatEvent] = []
    param = effect.mechanic_param
    for target in targets:
        handler(target, param)
        events.append(CombatEvent(
            round_number=rnd, actor_name=combatant.name,
            target_name=target.name,
            event_type=EventType.SKILL_USE,
            description=effect.mechanic_id,
        ))
    return events


def _apply_resource_gain(
    effect: SkillEffect, targets: list[Character],
    rnd: int, combatant: Character,
) -> list[CombatEvent]:
    """Concede recurso de classe ao alvo."""
    if effect.resource_type is None:
        return []
    events: list[CombatEvent] = []
    for target in targets:
        resource = getattr(target, effect.resource_type, None)
        if resource is None:
            continue
        gain_fn = getattr(resource, "gain", None)
        if gain_fn is None:
            continue
        gain_fn(effect.base_power)
        events.append(CombatEvent(
            round_number=rnd, actor_name=combatant.name,
            target_name=target.name,
            event_type=EventType.BUFF,
            value=effect.base_power,
            description=f"+{effect.base_power} {effect.resource_type}",
        ))
    return events


def _apply_shield(
    effect: SkillEffect, targets: list[Character],
    rnd: int, combatant: Character,
) -> list[CombatEvent]:
    """Cria barreira/temp HP no alvo."""
    events: list[CombatEvent] = []
    for target in targets:
        target.barrier.add(effect.base_power)
        events.append(CombatEvent(
            round_number=rnd, actor_name=combatant.name,
            target_name=target.name,
            event_type=EventType.BUFF,
            value=effect.base_power,
            description="shield",
        ))
    return events


def _apply_counter_attack(
    effect: SkillEffect, targets: list[Character],
    rnd: int, combatant: Character,
) -> list[CombatEvent]:
    """Contra-ataque reativo (dano baseado no ATK do reator).

    Filtra o proprio combatant dos alvos — skills SELF com
    COUNTER_ATTACK nao devem causar dano a si mesmo.
    """
    events: list[CombatEvent] = []
    attack = effect.base_power + combatant.attack_power
    valid_targets = [t for t in targets if t is not combatant]
    for target in valid_targets:
        defense = target.defense_for(combatant.preferred_attack_type)
        result = resolve_damage(attack_power=attack, defense=defense)
        target.take_damage(result.final_damage)
        events.append(CombatEvent(
            round_number=rnd, actor_name=combatant.name,
            target_name=target.name, damage=result,
            description="counter_attack",
        ))
    return events


def _mechanic_stance_offensive(target: Character, param: str | None) -> None:
    change = getattr(target, "change_stance", None)
    if change is not None:
        from src.core.classes.fighter.stance import Stance
        change(Stance.OFFENSIVE)


def _mechanic_stance_defensive(target: Character, param: str | None) -> None:
    change = getattr(target, "change_stance", None)
    if change is not None:
        from src.core.classes.fighter.stance import Stance
        change(Stance.DEFENSIVE)


def _mechanic_stance_normal(target: Character, param: str | None) -> None:
    change = getattr(target, "change_stance", None)
    if change is not None:
        from src.core.classes.fighter.stance import Stance
        change(Stance.NORMAL)


def _mechanic_reckless_stance(target: Character, param: str | None) -> None:
    toggle = getattr(target, "toggle_reckless", None)
    if toggle is not None:
        toggle()


def _mechanic_activate_overcharge(target: Character, param: str | None) -> None:
    fn = getattr(target, "activate_overcharge", None)
    if fn is not None:
        fn()


def _mechanic_activate_overcharged(target: Character, param: str | None) -> None:
    fn = getattr(target, "activate_overcharged", None)
    if fn is not None:
        fn()


def _mechanic_switch_aura_offensive(target: Character, param: str | None) -> None:
    fn = getattr(target, "change_aura", None)
    if fn is not None:
        from src.core.classes.paladin.aura import Aura
        fn(Aura.ATTACK)


def _mechanic_switch_aura_defensive(target: Character, param: str | None) -> None:
    fn = getattr(target, "change_aura", None)
    if fn is not None:
        from src.core.classes.paladin.aura import Aura
        fn(Aura.PROTECTION)


def _mechanic_apply_hunters_mark(target: Character, param: str | None) -> None:
    fn = getattr(target, "mark_target", None)
    if fn is not None:
        fn(param or "")


def _mechanic_shift_destruction(target: Character, param: str | None) -> None:
    fn = getattr(target, "attack_action", None)
    if fn is not None:
        fn()


def _mechanic_shift_vitality(target: Character, param: str | None) -> None:
    fn = getattr(target, "defensive_action", None)
    if fn is not None:
        fn()


def _mechanic_shift_balance(target: Character, param: str | None) -> None:
    fn = getattr(target, "end_of_turn_decay", None)
    if fn is not None:
        fn()


def _mechanic_set_metamagic(target: Character, param: str | None) -> None:
    fn = getattr(target, "set_metamagic", None)
    if fn is not None:
        from src.core.elements.element_type import ElementType
        element = ElementType[param] if param else ElementType.FIRE
        fn(element)


def _mechanic_transform_animal_form(target: Character, param: str | None) -> None:
    fn = getattr(target, "transform", None)
    if fn is not None:
        from src.core.classes.druid.animal_form import AnimalForm
        form = AnimalForm[param] if param else AnimalForm.BEAR
        fn(form)


def _mechanic_create_field_condition(target: Character, param: str | None) -> None:
    fn = getattr(target, "create_field_condition", None)
    if fn is not None:
        from src.core.classes.druid.field_condition import FieldConditionType
        condition = FieldConditionType[param] if param else FieldConditionType.SNOW
        fn(condition)


def _mechanic_enter_stealth(target: Character, param: str | None) -> None:
    fn = getattr(target, "enter_stealth", None)
    if fn is not None:
        fn()


def _mechanic_envenom_weapon(target: Character, param: str | None) -> None:
    fn = getattr(target, "envenom_weapon", None)
    if fn is not None:
        fn()


_MECHANIC_DISPATCH: dict[str, Callable[..., None]] = {
    "change_stance_offensive": _mechanic_stance_offensive,
    "change_stance_defensive": _mechanic_stance_defensive,
    "change_stance_normal": _mechanic_stance_normal,
    "activate_reckless_stance": _mechanic_reckless_stance,
    "activate_overcharge": _mechanic_activate_overcharge,
    "activate_overcharged": _mechanic_activate_overcharged,
    "switch_aura_offensive": _mechanic_switch_aura_offensive,
    "switch_aura_defensive": _mechanic_switch_aura_defensive,
    "apply_hunters_mark": _mechanic_apply_hunters_mark,
    "shift_destruction": _mechanic_shift_destruction,
    "shift_vitality": _mechanic_shift_vitality,
    "shift_balance": _mechanic_shift_balance,
    "set_metamagic": _mechanic_set_metamagic,
    "transform_animal_form": _mechanic_transform_animal_form,
    "create_field_condition": _mechanic_create_field_condition,
    "enter_stealth": _mechanic_enter_stealth,
    "envenom_weapon": _mechanic_envenom_weapon,
}


_APPLIERS: dict[SkillEffectType, Callable[..., list[CombatEvent]]] = {
    SkillEffectType.DAMAGE: _apply_damage,
    SkillEffectType.HEAL: _apply_heal,
    SkillEffectType.BUFF: _apply_buff,
    SkillEffectType.DEBUFF: _apply_debuff,
    SkillEffectType.APPLY_AILMENT: _apply_ailment,
    SkillEffectType.TRIGGER_CLASS_MECHANIC: _apply_trigger_mechanic,
    SkillEffectType.RESOURCE_GAIN: _apply_resource_gain,
    SkillEffectType.SHIELD: _apply_shield,
    SkillEffectType.COUNTER_ATTACK: _apply_counter_attack,
}

_AILMENT_FACTORIES: dict[str, Callable[..., object]] = {
    # DoTs: (base_power=damage_per_tick, duration)
    "poison": create_poison,
    "virus": create_virus,
    "bleed": create_bleed,
    "burn": create_burn,
    "scorch": create_scorch,
    # CCs: ignore base_power, use only duration
    "freeze": lambda bp, dur: create_freeze(dur),
    "paralysis": lambda bp, dur: create_paralysis(dur),
    "confusion": lambda bp, dur: create_confusion(dur),
    # Debuff ailments: base_power = reduction_percent
    "cold": lambda bp, dur: create_cold(dur, float(bp)),
    "weakness": lambda bp, dur: create_weakness(dur, float(bp)),
    "injury": lambda bp, dur: create_injury(dur, float(bp)),
    "sickness": lambda bp, dur: create_sickness(dur, float(bp)),
    # Resource locks: ignore base_power
    "amnesia": lambda bp, dur: create_amnesia(dur),
    "curse": lambda bp, dur: create_curse(dur),
}
