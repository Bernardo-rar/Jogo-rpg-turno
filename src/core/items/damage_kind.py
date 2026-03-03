"""Sub-tipos de dano fisico das armas."""

from enum import Enum, auto


class DamageKind(Enum):
    """Cortante, perfurante ou contundente."""

    SLASHING = auto()
    PIERCING = auto()
    BLUDGEONING = auto()
