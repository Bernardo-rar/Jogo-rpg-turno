"""Enum de stats derivados que efeitos podem modificar."""

from enum import Enum, auto


class ModifiableStat(Enum):
    """Stats derivados que efeitos podem modificar.

    Mapeados 1:1 com properties do Character.
    Atributos primarios (STR, DEX, etc) usam AttributeType.
    """

    PHYSICAL_ATTACK = auto()
    MAGICAL_ATTACK = auto()
    PHYSICAL_DEFENSE = auto()
    MAGICAL_DEFENSE = auto()
    SPEED = auto()
    MAX_HP = auto()
    MAX_MANA = auto()
    HP_REGEN = auto()
    MANA_REGEN = auto()
    HEALING_RECEIVED = auto()
