"""Tipos de efeito que uma skill pode produzir."""

from enum import Enum, auto


class SkillEffectType(Enum):
    """Categorias de efeito: dano, cura, buff, debuff, ailment."""

    DAMAGE = auto()
    HEAL = auto()
    BUFF = auto()
    DEBUFF = auto()
    APPLY_AILMENT = auto()
    TRIGGER_CLASS_MECHANIC = auto()
    RESOURCE_GAIN = auto()
    SHIELD = auto()
    COUNTER_ATTACK = auto()
    GRANT_ACTION = auto()
