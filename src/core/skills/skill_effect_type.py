"""Tipos de efeito que uma skill pode produzir."""

from enum import Enum, auto


class SkillEffectType(Enum):
    """Categorias de efeito: dano, cura, buff, debuff, ailment."""

    DAMAGE = auto()
    HEAL = auto()
    BUFF = auto()
    DEBUFF = auto()
    APPLY_AILMENT = auto()
