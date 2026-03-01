from __future__ import annotations

from src.core.combat.combat_engine import CombatEvent, TurnContext, TurnHandler


class DispatchTurnHandler:
    """Despacha execucao de turno para handlers especificos por combatente.

    Mapeia nome do combatente para um TurnHandler. Se nao encontrar,
    usa o handler default. Respeita OCP: novo comportamento = novo handler.
    """

    def __init__(
        self,
        handlers: dict[str, TurnHandler],
        default: TurnHandler,
    ) -> None:
        self._handlers = handlers
        self._default = default

    def execute_turn(self, context: TurnContext) -> list[CombatEvent]:
        handler = self._handlers.get(context.combatant.name, self._default)
        return handler.execute_turn(context)
