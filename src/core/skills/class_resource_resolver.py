"""Funcoes puras para checar e gastar recursos de classe via duck typing."""

from __future__ import annotations

from src.core.skills.resource_cost import ResourceCost


def can_afford_resource(combatant: object, cost: ResourceCost) -> bool:
    """Checa se o combatant tem recurso suficiente.

    Usa getattr para achar o recurso e .current para ler o valor.
    Retorna False se o recurso nao existir no combatant.
    """
    resource = getattr(combatant, cost.resource_type, None)
    if resource is None:
        return False
    current = getattr(resource, "current", None)
    if current is None:
        return False
    return current >= cost.amount


def spend_resource(combatant: object, cost: ResourceCost) -> bool:
    """Gasta recurso do combatant.

    Usa getattr para achar o recurso e .spend(amount) para gastar.
    Retorna False se nao puder gastar.
    """
    resource = getattr(combatant, cost.resource_type, None)
    if resource is None:
        return False
    spend_fn = getattr(resource, "spend", None)
    if spend_fn is None:
        return False
    return spend_fn(cost.amount)
