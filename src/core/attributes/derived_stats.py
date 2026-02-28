"""Funcoes puras para calcular stats derivados a partir de atributos primarios.

Cada funcao recebe os valores necessarios como parametros (DI),
nao depende de nenhuma classe concreta.
Os modificadores de classe (mod_hp, mod_atk_physical, etc.) sao injetados.
"""

LEVEL_1_HP_MULTIPLIER = 2
MANA_BASE_MULTIPLIER = 10


def calculate_hp(
    hit_dice: int, con: int, vida_mod: int, mod_hp: int, level: int
) -> int:
    """HP = ((hit_dice + CON + vida_mod) [* 2 se lvl1]) * mod_hp."""
    base = hit_dice + con + vida_mod
    if level == 1:
        base *= LEVEL_1_HP_MULTIPLIER
    return base * mod_hp


def calculate_mana(mana_multiplier: int, mind: int) -> int:
    """Mana = multiplicador_classe_nivel * MIND * 10.

    O mana_multiplier varia por classe e nivel (ex: guerreiro lvl1=6, lvl2+=4).
    """
    return mana_multiplier * mind * MANA_BASE_MULTIPLIER


def calculate_physical_attack(
    weapon_die: int, strength: int, dexterity: int, mod_atk_physical: int
) -> int:
    """Ataque fisico = (dado_arma + (STR + DEX)) * mod_atk_fisico."""
    return (weapon_die + strength + dexterity) * mod_atk_physical


def calculate_magical_attack(
    weapon_die: int, wisdom: int, intelligence: int, mod_atk_magical: int
) -> int:
    """Ataque magico = (dado_arma + (WIS + INT)) * mod_atk_magico."""
    return (weapon_die + wisdom + intelligence) * mod_atk_magical


def calculate_physical_defense(
    dexterity: int, constitution: int, strength: int, mod_def_physical: int
) -> int:
    """Defesa fisica = (DEX + CON + STR) * mod_def_fisico."""
    return (dexterity + constitution + strength) * mod_def_physical


def calculate_magical_defense(
    constitution: int, wisdom: int, intelligence: int, mod_def_magical: int
) -> int:
    """Defesa magica = (CON + WIS + INT) * mod_def_magico."""
    return (constitution + wisdom + intelligence) * mod_def_magical


def calculate_hp_regen(constitution: int, regen_hp_mod: int) -> int:
    """Regen HP = CON * regen_hp_mod."""
    return constitution * regen_hp_mod


def calculate_mana_regen(mind: int, regen_mana_mod: int) -> int:
    """Regen Mana = MIND * regen_mana_mod."""
    return mind * regen_mana_mod
