"""PlayerAction — representa a escolha do jogador durante o turno."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class PlayerActionType(Enum):
    """Tipos de acao que o jogador pode escolher."""

    BASIC_ATTACK = auto()
    SKILL = auto()
    ITEM = auto()
    MOVE = auto()
    DEFEND = auto()
    END_TURN = auto()


@dataclass(frozen=True)
class PlayerAction:
    """Escolha imutavel do jogador: tipo de acao + alvo/skill/item."""

    action_type: PlayerActionType
    target_name: str = ""
    skill_id: str = ""
    consumable_id: str = ""
