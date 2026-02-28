from __future__ import annotations

from enum import Enum, auto
from typing import Protocol, runtime_checkable

from src.core.characters.position import Position


class AttackRange(Enum):
    """Alcance do ataque: melee ou ranged."""

    MELEE = auto()
    RANGED = auto()


@runtime_checkable
class Targetable(Protocol):
    """Entidade que pode ser alvo de ataques."""

    @property
    def is_alive(self) -> bool: ...

    @property
    def position(self) -> Position: ...


def get_valid_targets(
    attack_range: AttackRange,
    enemies: list[Targetable],
) -> list[Targetable]:
    """Retorna alvos validos baseado no alcance e posicao dos inimigos.

    Melee: so atinge front line. Se nenhum front vivo, fallback para back.
    Ranged: atinge qualquer posicao.
    """
    alive = [e for e in enemies if e.is_alive]
    if attack_range == AttackRange.RANGED:
        return alive
    front = [e for e in alive if e.position == Position.FRONT]
    return front if front else alive
