"""Politicas de stacking para efeitos."""

from enum import Enum, auto


class StackingPolicy(Enum):
    """Como efeitos com mesmo stacking_key interagem.

    REPLACE: novo substitui antigo (padrao para maioria dos buffs/debuffs).
    STACK: ambos coexistem, modificadores sao aditivos.
    REFRESH: mantem existente mas reseta duracao para a do novo.
    """

    REPLACE = auto()
    STACK = auto()
    REFRESH = auto()
