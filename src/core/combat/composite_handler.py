"""CompositeHandler - encadeia TurnHandlers em sequencia."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.combat.combat_engine import CombatEvent, TurnContext, TurnHandler


class CompositeHandler:
    """Tenta cada handler em ordem; retorna eventos do primeiro que agir."""

    def __init__(self, handlers: tuple[TurnHandler, ...]) -> None:
        self._handlers = handlers

    def execute_turn(self, context: TurnContext) -> list[CombatEvent]:
        for handler in self._handlers:
            events = handler.execute_turn(context)
            if events:
                return events
        return []
