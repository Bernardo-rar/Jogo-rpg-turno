from enum import Enum, auto


class ActionType(Enum):
    """Tipos de acao disponiveis por turno."""

    ACTION = auto()
    BONUS_ACTION = auto()
    REACTION = auto()
    PASSIVE = auto()


PROACTIVE_ACTIONS = frozenset({ActionType.ACTION, ActionType.BONUS_ACTION})


class ActionEconomy:
    """Controla acoes disponiveis de um personagem durante um turno."""

    def __init__(self) -> None:
        self._available: dict[ActionType, bool] = {
            action: True for action in ActionType
        }

    def is_available(self, action: ActionType) -> bool:
        return self._available[action]

    def use(self, action: ActionType) -> bool:
        if not self._available[action]:
            return False
        self._available[action] = False
        return True

    def grant(self, action: ActionType) -> None:
        """Concede uma acao extra deste tipo no turno atual."""
        self._available[action] = True

    def reset(self) -> None:
        for action in ActionType:
            self._available[action] = True

    @property
    def has_actions(self) -> bool:
        """Retorna True se ainda tem acao normal OU bonus disponivel."""
        return any(
            self._available[action] for action in PROACTIVE_ACTIONS
        )
