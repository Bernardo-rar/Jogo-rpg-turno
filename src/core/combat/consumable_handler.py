"""ConsumableHandler - TurnHandler que executa consumiveis no combate."""

from __future__ import annotations

from src.core.combat.action_economy import ActionType
from src.core.combat.combat_engine import CombatEvent, TurnContext
from src.core.combat.consumable_effect_applier import apply_consumable_effect
from src.core.combat.target_resolver import resolve_targets
from src.core.items.consumable import Consumable
from src.core.items.consumable_category import ConsumableCategory


class ConsumableHandler:
    """Seleciona e executa o primeiro consumivel viavel."""

    def execute_turn(self, context: TurnContext) -> list[CombatEvent]:
        item = _pick_consumable(context)
        if item is None:
            return []
        return _execute_consumable(item, context)


def _pick_consumable(context: TurnContext) -> Consumable | None:
    """Retorna primeiro consumivel viavel (pula healing se HP cheio)."""
    inventory = context.combatant.inventory
    if inventory is None:
        return None
    economy = context.action_economy
    mana = context.combatant.current_mana
    for slot in inventory.slots:
        consumable = slot.consumable
        if not _is_usable(consumable, mana, economy, context):
            continue
        return consumable
    return None


def _is_usable(
    consumable: Consumable, mana: int,
    economy, context: TurnContext,
) -> bool:
    if consumable.mana_cost > mana:
        return False
    if not economy.is_available(_ACTION_TYPE):
        return False
    if _is_wasteful_heal(consumable, context):
        return False
    if _is_wasteful_cleanse(consumable, context):
        return False
    return True


def _is_wasteful_heal(consumable: Consumable, context: TurnContext) -> bool:
    if consumable.category != ConsumableCategory.HEALING:
        return False
    combatant = context.combatant
    return combatant.current_hp >= combatant.max_hp


def _is_wasteful_cleanse(consumable: Consumable, context: TurnContext) -> bool:
    """Pula cleanse se nao ha efeitos negativos ativos."""
    if consumable.category != ConsumableCategory.CLEANSE:
        return False
    effects = context.combatant.effect_manager.active_effects
    return len(effects) == 0


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


_ACTION_TYPE = ActionType.BONUS_ACTION
