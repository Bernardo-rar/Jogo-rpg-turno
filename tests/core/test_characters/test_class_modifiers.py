import pytest

from src.core.characters.class_modifiers import ClassModifiers


class TestClassModifiersCreation:
    def test_create_fighter_modifiers(self):
        mods = ClassModifiers(
            hit_dice=12,
            mod_hp_flat=0,
            mod_hp_mult=10,
            mana_multiplier=6,
            mod_atk_physical=10,
            mod_atk_magical=6,
            mod_def_physical=5,
            mod_def_magical=3,
            regen_hp_mod=5,
            regen_mana_mod=3,
        )
        assert mods.hit_dice == 12
        assert mods.mod_hp_mult == 10

    def test_modifiers_are_immutable(self):
        mods = ClassModifiers(
            hit_dice=12,
            mod_hp_flat=0,
            mod_hp_mult=10,
            mana_multiplier=6,
            mod_atk_physical=10,
            mod_atk_magical=6,
            mod_def_physical=5,
            mod_def_magical=3,
            regen_hp_mod=5,
            regen_mana_mod=3,
        )
        with pytest.raises(AttributeError):
            mods.hit_dice = 8


class TestClassModifiersFromJson:
    def test_load_fighter_from_json(self):
        mods = ClassModifiers.from_json("data/classes/fighter.json")
        assert mods.hit_dice == 12
        assert mods.mod_atk_physical == 10
        assert mods.mod_def_physical == 5

    def test_all_fields_loaded(self):
        mods = ClassModifiers.from_json("data/classes/fighter.json")
        assert mods.mod_hp_flat == 0
        assert mods.mod_hp_mult == 10
        assert mods.mana_multiplier == 6
        assert mods.mod_atk_magical == 6
        assert mods.mod_def_magical == 3
        assert mods.regen_hp_mod == 5
        assert mods.regen_mana_mod == 3
