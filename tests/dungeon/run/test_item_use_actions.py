"""Testes para item_use_actions — uso de consumiveis fora de combate."""

from __future__ import annotations

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_modifiers import ClassModifiers
from src.core.effects.ailments.poison import Poison
from src.core.items.consumable import Consumable
from src.core.items.consumable_category import ConsumableCategory
from src.core.items.consumable_effect import ConsumableEffect
from src.core.items.consumable_effect_type import ConsumableEffectType
from src.core.items.inventory import Inventory
from src.core.items.inventory_slot import InventorySlot
from src.core.skills.target_type import TargetType
from src.dungeon.run.item_use_actions import (
    apply_consumable_on_target,
    get_usable_consumables,
)

_MODS = ClassModifiers(
    hit_dice=10,
    mod_hp_flat=0,
    mod_hp_mult=1,
    mana_multiplier=1,
    mod_atk_physical=2,
    mod_atk_magical=1,
    mod_def_physical=1,
    mod_def_magical=1,
    regen_hp_mod=0,
    regen_mana_mod=0,
)

_EMPTY_THRESHOLDS = ThresholdCalculator({})


def _make_char(name: str = "Hero") -> Character:
    attrs = Attributes()
    for attr_type in AttributeType:
        attrs.set(attr_type, 10)
    config = CharacterConfig(
        class_modifiers=_MODS,
        threshold_calculator=_EMPTY_THRESHOLDS,
    )
    return Character(name, attrs, config)


def _heal_consumable(power: int = 50) -> Consumable:
    return Consumable(
        consumable_id="hp_pot",
        name="Health Potion",
        category=ConsumableCategory.HEALING,
        mana_cost=0,
        target_type=TargetType.SELF,
        effects=(ConsumableEffect(
            effect_type=ConsumableEffectType.HEAL_HP, base_power=power,
        ),),
        usable_outside_combat=True,
    )


def _mana_consumable(power: int = 30) -> Consumable:
    return Consumable(
        consumable_id="mana_pot",
        name="Mana Potion",
        category=ConsumableCategory.HEALING,
        mana_cost=0,
        target_type=TargetType.SELF,
        effects=(ConsumableEffect(
            effect_type=ConsumableEffectType.HEAL_MANA, base_power=power,
        ),),
        usable_outside_combat=True,
    )


def _cleanse_consumable() -> Consumable:
    return Consumable(
        consumable_id="antidote",
        name="Antidote",
        category=ConsumableCategory.CLEANSE,
        mana_cost=0,
        target_type=TargetType.SINGLE_ALLY,
        effects=(ConsumableEffect(
            effect_type=ConsumableEffectType.CLEANSE,
        ),),
        usable_outside_combat=True,
    )


def _combat_only_consumable() -> Consumable:
    return Consumable(
        consumable_id="molotov",
        name="Molotov",
        category=ConsumableCategory.OFFENSIVE,
        mana_cost=5,
        target_type=TargetType.ALL_ENEMIES,
        effects=(ConsumableEffect(
            effect_type=ConsumableEffectType.DAMAGE, base_power=40,
        ),),
        usable_outside_combat=False,
    )


class TestApplyConsumableOnTarget:
    def test_heal_hp_outside_combat(self) -> None:
        char = _make_char()
        char.take_damage(20)
        hp_before = char.current_hp
        consumable = _heal_consumable(50)
        result = apply_consumable_on_target(consumable, char)
        assert char.current_hp > hp_before
        assert "HP" in result

    def test_heal_mana_outside_combat(self) -> None:
        char = _make_char()
        # Gastar mana
        char._current_mana = max(0, char.current_mana - 20)
        mana_before = char.current_mana
        consumable = _mana_consumable(30)
        result = apply_consumable_on_target(consumable, char)
        assert char.current_mana > mana_before
        assert "mana" in result.lower() or "Mana" in result

    def test_cleanse_outside_combat(self) -> None:
        char = _make_char()
        dot = Poison(damage_per_tick=5, duration=3)
        char.effect_manager.add_effect(dot)
        assert len(char.effect_manager.active_effects) > 0
        consumable = _cleanse_consumable()
        result = apply_consumable_on_target(consumable, char)
        assert "Cleanse" in result or "cleanse" in result.lower()

    def test_damage_effect_ignored_outside(self) -> None:
        char = _make_char()
        consumable = _combat_only_consumable()
        hp_before = char.current_hp
        result = apply_consumable_on_target(consumable, char)
        assert char.current_hp == hp_before
        assert "No effect" in result


class TestGetUsableConsumables:
    def test_get_usable_filters_correctly(self) -> None:
        inventory = Inventory()
        hp_pot = _heal_consumable()
        molotov = _combat_only_consumable()
        inventory.add_item(hp_pot, 3)
        inventory.add_item(molotov, 2)
        usable = get_usable_consumables(inventory)
        assert len(usable) == 1
        assert usable[0].consumable.consumable_id == "hp_pot"

    def test_empty_inventory_returns_empty(self) -> None:
        inventory = Inventory()
        usable = get_usable_consumables(inventory)
        assert usable == []

    def test_all_combat_only_returns_empty(self) -> None:
        inventory = Inventory()
        inventory.add_item(_combat_only_consumable(), 5)
        usable = get_usable_consumables(inventory)
        assert usable == []

    def test_multiple_usable_returned(self) -> None:
        inventory = Inventory()
        inventory.add_item(_heal_consumable(), 2)
        inventory.add_item(_mana_consumable(), 3)
        usable = get_usable_consumables(inventory)
        assert len(usable) == 2
