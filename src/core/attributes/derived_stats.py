"""Funcoes puras para calcular stats derivados a partir de atributos primarios.

Cada funcao recebe os valores necessarios como parametros (DI),
nao depende de nenhuma classe concreta.
Os modificadores de classe (mod_hp_mult, mod_atk_physical, etc.) sao injetados.
"""

from __future__ import annotations

from dataclasses import dataclass

MANA_BASE_MULTIPLIER = 5


@dataclass(frozen=True)
class HpInput:
    """Dados necessarios para calcular HP."""

    hit_dice: int
    con: int
    mod_hp_flat: int
    mod_hp_mult: int
    level: int


@dataclass(frozen=True)
class AttackInput:
    """Dados necessarios para calcular ataque (fisico ou magico)."""

    weapon_die: int
    primary_stat: int
    secondary_stat: int
    modifier: int


@dataclass(frozen=True)
class DefenseInput:
    """Dados necessarios para calcular defesa (fisica ou magica)."""

    primary_stat: int
    secondary_stat: int
    tertiary_stat: int
    modifier: int


def calculate_hp(hp_input: HpInput) -> int:
    """HP = (hit_dice + CON + mod_hp_flat) * (level + 1) * mod_hp_mult.

    Level 1: base * 2 * mod_hp_mult (backward-compatible).
    Level N: base * (N+1) * mod_hp_mult (acumulativo).
    """
    base = hp_input.hit_dice + hp_input.con + hp_input.mod_hp_flat
    level_multiplier = hp_input.level + 1
    return base * level_multiplier * hp_input.mod_hp_mult


def calculate_mana(mana_multiplier: int, mind: int) -> int:
    """Mana = multiplicador_classe_nivel * MIND * 10.

    O mana_multiplier varia por classe e nivel (ex: guerreiro lvl1=6, lvl2+=4).
    """
    return mana_multiplier * mind * MANA_BASE_MULTIPLIER


def calculate_attack(attack_input: AttackInput) -> int:
    """Ataque = (dado_arma + stat_primario + stat_secundario) * modificador."""
    return (
        attack_input.weapon_die
        + attack_input.primary_stat
        + attack_input.secondary_stat
    ) * attack_input.modifier


def calculate_defense(defense_input: DefenseInput) -> int:
    """Defesa = (stat1 + stat2 + stat3) * modificador."""
    return (
        defense_input.primary_stat
        + defense_input.secondary_stat
        + defense_input.tertiary_stat
    ) * defense_input.modifier


def calculate_hp_regen(constitution: int, regen_hp_mod: int, level: int) -> int:
    """Regen HP = CON * level * regen_hp_mod."""
    return constitution * level * regen_hp_mod


def calculate_mana_regen(mind: int, regen_mana_mod: int, level: int) -> int:
    """Regen Mana = MIND * level * regen_mana_mod."""
    return mind * level * regen_mana_mod
