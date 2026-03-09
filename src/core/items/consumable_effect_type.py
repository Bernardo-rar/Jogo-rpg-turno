"""Tipos de efeito que um consumivel pode produzir."""

from enum import Enum, auto


class ConsumableEffectType(Enum):
    """Categorias de efeito: cura HP/mana, dano, buff, cleanse, fuga."""

    HEAL_HP = auto()
    HEAL_MANA = auto()
    DAMAGE = auto()
    BUFF = auto()
    CLEANSE = auto()
    FLEE = auto()
