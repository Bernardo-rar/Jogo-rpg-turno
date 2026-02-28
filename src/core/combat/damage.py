from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

MIN_DAMAGE = 1
DEFAULT_CRIT_MULTIPLIER = 2
BASE_CRIT_CHANCE = 0.05
MAX_CRIT_CHANCE = 1.0
PERCENT_DIVISOR = 100


class DamageType(Enum):
    """Tipo de dano: fisico ou magico."""

    PHYSICAL = auto()
    MAGICAL = auto()


@dataclass(frozen=True)
class DamageResult:
    """Resultado imutavel de uma resolucao de dano."""

    raw_damage: int
    defense_value: int
    is_critical: bool
    final_damage: int


def resolve_damage(
    attack_power: int,
    defense: int,
    *,
    is_critical: bool = False,
) -> DamageResult:
    """Resolve dano: aplica critico ao ataque, subtrai defesa, minimo MIN_DAMAGE.

    Critico multiplica attack_power ANTES de subtrair defesa.
    """
    effective = attack_power * DEFAULT_CRIT_MULTIPLIER if is_critical else attack_power
    final = max(MIN_DAMAGE, effective - defense)
    return DamageResult(
        raw_damage=attack_power,
        defense_value=defense,
        is_critical=is_critical,
        final_damage=final,
    )


def calculate_crit_chance(bonus_pct: int) -> float:
    """Chance de critico = base (5%) + bonus de thresholds/buffs.

    bonus_pct e um inteiro representando porcentagem (ex: 10 = 10%).
    Retorna float entre 0 e MAX_CRIT_CHANCE (1.0).
    """
    return min(MAX_CRIT_CHANCE, BASE_CRIT_CHANCE + bonus_pct / PERCENT_DIVISOR)
