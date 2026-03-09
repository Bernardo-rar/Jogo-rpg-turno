"""ConsumableHandler - TurnHandler que executa consumiveis no combate."""

from __future__ import annotations

from src.core.combat.action_economy import ActionType
from src.core.combat.combat_engine import CombatEvent, TurnContext
from src.core.combat.consumable_effect_applier import apply_consumable_effect
from src.core.combat.target_resolver import resolve_targets
from src.core.items.consumable import Consumable


class ConsumableHandler:
    """Seleciona e executa o primeiro consumivel viavel."""

    def execute_turn(self, context: TurnContext) -> list[CombatEvent]:
        item = _pick_consumable(context)
        if item is None:
            return []
        return _execute_consumable(item, context)


def _pick_consumable(context: TurnContext) -> Consumable | None:
    """Retorna primeiro consumivel com action disponivel."""
    inventory = context.combatant.inventory
    if inventory is None:
        return None
    economy = context.action_economy
    mana = context.combatant.current_mana
    for slot in inventory.slots:
        consumable = slot.consumable
        if consumable.mana_cost <= mana and economy.is_available(_ACTION_TYPE):
            return consumable
    return None


def _execute_consumable(
    item: Consumable, context: TurnContext,
) -> list[CombatEvent]:
    """Consome recursos e aplica efeitos do consumivel."""
    context.action_economy.use(_ACTION_TYPE)
    context.combatant.spend_mana(item.mana_cost)
    targets = resolve_targets(item.target_type, context)
    events: list[CombatEvent] = []
    for effect in item.effects:
        events.extend(apply_consumable_effect(
            effect, targets, context.round_number,
            context.combatant.name,
        ))
    _remove_from_inventory(context, item)
    return events


def _remove_from_inventory(
    context: TurnContext, item: Consumable,
) -> None:
    """Remove 1 unidade do consumivel do inventario."""
    inventory = context.combatant.inventory
    if inventory is not None:
        inventory.remove_item(item.consumable_id)


_ACTION_TYPE = ActionType.ACTION
