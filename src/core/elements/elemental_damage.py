"""Elemental damage resolution - aplica multiplicador elemental ao dano."""

from __future__ import annotations

from dataclasses import dataclass

from src.core.combat.damage import DamageResult
from src.core.elements.element_type import ElementType
from src.core.elements.elemental_profile import ElementalProfile

MIN_ELEMENTAL_DAMAGE = 1


@dataclass(frozen=True)
class ElementalDamageResult:
    """Resultado de dano com informacao elemental.

    Wraps DamageResult sem modificar. Adiciona elemento, multiplicador
    e dano final ajustado pela fraqueza/resistencia do alvo.
    """

    base_result: DamageResult
    element: ElementType
    multiplier: float
    final_damage: int


def resolve_elemental_damage(
    base_result: DamageResult,
    element: ElementType,
    target_profile: ElementalProfile,
) -> ElementalDamageResult:
    """Aplica fraqueza/resistencia elemental ao DamageResult.

    final_damage = max(1, base_result.final_damage * multiplier).
    """
    multiplier = target_profile.get_multiplier(element)
    adjusted = max(
        MIN_ELEMENTAL_DAMAGE,
        int(base_result.final_damage * multiplier),
    )
    return ElementalDamageResult(
        base_result=base_result,
        element=element,
        multiplier=multiplier,
        final_damage=adjusted,
    )
