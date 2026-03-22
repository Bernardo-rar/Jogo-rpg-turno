"""Testes para integracao Character + Inventory."""

from __future__ import annotations

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_modifiers import ClassModifiers
from src.core.items.inventory import Inventory


def _default_config(inventory: Inventory | None = None) -> CharacterConfig:
    mods = ClassModifiers(
        hit_dice=10, mod_hp_flat=0, mod_hp_mult=5, mana_multiplier=6,
        mod_atk_physical=5, mod_atk_magical=5,
        mod_def_physical=3, mod_def_magical=3,
        regen_hp_mod=2, regen_mana_mod=2,
    )
    return CharacterConfig(
        class_modifiers=mods,
        threshold_calculator=ThresholdCalculator({}),
        inventory=inventory,
    )


def _make_attrs() -> Attributes:
    attrs = Attributes()
    for attr_type in AttributeType:
        attrs.set(attr_type, 10)
    return attrs


class TestCharacterInventory:
    def test_default_inventory_is_none(self) -> None:
        char = Character("Test", _make_attrs(), _default_config())
        assert char.inventory is None

    def test_with_inventory(self) -> None:
        inv = Inventory()
        char = Character("Test", _make_attrs(), _default_config(inventory=inv))
        assert char.inventory is inv

    def test_inventory_is_mutable(self) -> None:
        inv = Inventory()
        char = Character("Test", _make_attrs(), _default_config(inventory=inv))
        assert char.inventory is not None
        assert char.inventory.available_slots == 20
