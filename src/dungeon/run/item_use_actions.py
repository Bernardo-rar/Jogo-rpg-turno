"""Uso de consumiveis fora de combate."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.core.effects.effect_category import EffectCategory
from src.core.items.consumable_effect import ConsumableEffect
from src.core.items.consumable_effect_type import ConsumableEffectType
from src.core.items.inventory import Inventory
from src.core.items.inventory_slot import InventorySlot

if TYPE_CHECKING:
    from src.core.characters.character import Character
    from src.core.items.consumable import Consumable


def apply_consumable_on_target(consumable: Consumable, target: Character) -> str:
    """Aplica consumivel fora de combate. Retorna descricao do resultado."""
    messages: list[str] = []
    for effect in consumable.effects:
        msg = _apply_single_effect(effect, target)
        if msg:
            messages.append(msg)
    if not messages:
        return "No effect outside combat"
    return "; ".join(messages)


def _apply_single_effect(effect: ConsumableEffect, target: Character) -> str:
    """Aplica um efeito atomico. Retorna descricao ou string vazia."""
    applier = _APPLIERS.get(effect.effect_type)
    if applier is None:
        return ""
    return applier(effect, target)


def _apply_heal_hp(effect: ConsumableEffect, target: Character) -> str:
    healed = target.heal(effect.base_power)
    return f"Healed {healed} HP"


def _apply_heal_mana(effect: ConsumableEffect, target: Character) -> str:
    restored = target.restore_mana(effect.base_power)
    return f"Restored {restored} Mana"


def _apply_cleanse(effect: ConsumableEffect, target: Character) -> str:
    _remove_negative_effects(target)
    return "Cleansed all negative effects"


def _remove_negative_effects(target: Character) -> None:
    """Remove todos os efeitos que NAO sao buffs."""
    negatives = [
        e for e in target.effect_manager.active_effects
        if e.category != EffectCategory.BUFF
    ]
    for eff in negatives:
        target.effect_manager.remove_effect(eff)


def get_usable_consumables(inventory: Inventory) -> list[InventorySlot]:
    """Retorna consumiveis que podem ser usados fora de combate."""
    return [
        slot for slot in inventory.slots
        if slot.consumable.usable_outside_combat
    ]


_APPLIERS: dict[ConsumableEffectType, object] = {
    ConsumableEffectType.HEAL_HP: _apply_heal_hp,
    ConsumableEffectType.HEAL_MANA: _apply_heal_mana,
    ConsumableEffectType.CLEANSE: _apply_cleanse,
}
