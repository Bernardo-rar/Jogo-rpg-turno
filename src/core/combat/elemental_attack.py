"""Resolve dano elemental + gera e aplica on-hit effects."""

from __future__ import annotations

from dataclasses import dataclass

from src.core.combat.damage import DamageResult
from src.core.effects.effect_manager import EffectManager
from src.core.elements.elemental_damage import (
    ElementalDamageResult,
    resolve_elemental_damage,
)
from src.core.elements.element_type import ElementType
from src.core.elements.elemental_profile import ElementalProfile
from src.core.elements.on_hit.on_hit_config import OnHitConfig
from src.core.elements.on_hit.on_hit_generator import generate_on_hit
from src.core.elements.on_hit.on_hit_result import OnHitResult


@dataclass(frozen=True)
class ElementalContext:
    """Contexto elemental: elemento, perfil do alvo e configs de on-hit."""

    element: ElementType
    target_profile: ElementalProfile
    on_hit_configs: dict[ElementType, OnHitConfig]


@dataclass(frozen=True)
class ElementalAttackOutcome:
    """Resultado completo de um ataque elemental: dano + on-hit effects."""

    elemental_result: ElementalDamageResult
    on_hit: OnHitResult


def resolve_elemental_attack(
    base_result: DamageResult,
    context: ElementalContext,
) -> ElementalAttackOutcome:
    """Resolve dano elemental + gera on-hit effects.

    1. Aplica resistencia/fraqueza elemental ao dano base.
    2. Gera on-hit effects a partir do config do elemento.
    """
    elemental_result = resolve_elemental_damage(
        base_result, context.element, context.target_profile,
    )
    config = context.on_hit_configs.get(context.element, OnHitConfig())
    on_hit = generate_on_hit(config, elemental_result.final_damage)
    return ElementalAttackOutcome(
        elemental_result=elemental_result,
        on_hit=on_hit,
    )


def apply_on_hit_effects(
    outcome: ElementalAttackOutcome,
    target_manager: EffectManager,
    attacker_manager: EffectManager,
) -> None:
    """Aplica effects do on-hit nos EffectManagers."""
    for effect in outcome.on_hit.effects:
        target_manager.add_effect(effect)
    for effect in outcome.on_hit.self_effects:
        attacker_manager.add_effect(effect)
