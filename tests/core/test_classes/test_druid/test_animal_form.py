from __future__ import annotations

import pytest

from src.core.classes.druid.animal_form import (
    AnimalForm,
    AnimalFormModifier,
    load_animal_form_modifiers,
)


class TestAnimalFormEnum:
    def test_has_five_members(self) -> None:
        assert len(AnimalForm) == 5

    def test_humanoid_exists(self) -> None:
        assert AnimalForm.HUMANOID is not None

    def test_bear_exists(self) -> None:
        assert AnimalForm.BEAR is not None

    def test_wolf_exists(self) -> None:
        assert AnimalForm.WOLF is not None

    def test_eagle_exists(self) -> None:
        assert AnimalForm.EAGLE is not None

    def test_serpent_exists(self) -> None:
        assert AnimalForm.SERPENT is not None

    def test_values_are_unique(self) -> None:
        values = [f.value for f in AnimalForm]
        assert len(values) == len(set(values))


class TestAnimalFormModifier:
    def test_is_frozen(self) -> None:
        mod = AnimalFormModifier(
            phys_atk_multiplier=1.0,
            mag_atk_multiplier=1.0,
            phys_def_multiplier=1.0,
            mag_def_multiplier=1.0,
            speed_multiplier=1.0,
            hp_regen_multiplier=1.0,
        )
        with pytest.raises(AttributeError):
            mod.phys_atk_multiplier = 2.0  # type: ignore[misc]

    def test_has_all_fields(self) -> None:
        mod = AnimalFormModifier(
            phys_atk_multiplier=1.1,
            mag_atk_multiplier=1.2,
            phys_def_multiplier=1.3,
            mag_def_multiplier=1.4,
            speed_multiplier=1.5,
            hp_regen_multiplier=1.6,
        )
        assert mod.phys_atk_multiplier == 1.1
        assert mod.mag_atk_multiplier == 1.2
        assert mod.phys_def_multiplier == 1.3
        assert mod.mag_def_multiplier == 1.4
        assert mod.speed_multiplier == 1.5
        assert mod.hp_regen_multiplier == 1.6


class TestLoadAnimalFormModifiers:
    def test_loads_all_five_forms(self) -> None:
        mods = load_animal_form_modifiers()
        assert len(mods) == 5

    def test_keys_are_animal_form_enum(self) -> None:
        mods = load_animal_form_modifiers()
        for key in mods:
            assert isinstance(key, AnimalForm)

    def test_values_are_modifier(self) -> None:
        mods = load_animal_form_modifiers()
        for val in mods.values():
            assert isinstance(val, AnimalFormModifier)

    def test_humanoid_is_neutral(self) -> None:
        mods = load_animal_form_modifiers()
        h = mods[AnimalForm.HUMANOID]
        assert h.phys_atk_multiplier == 1.0
        assert h.mag_atk_multiplier == 1.0
        assert h.phys_def_multiplier == 1.0
        assert h.mag_def_multiplier == 1.0
        assert h.speed_multiplier == 1.0
        assert h.hp_regen_multiplier == 1.0

    def test_bear_boosts_defense(self) -> None:
        mods = load_animal_form_modifiers()
        bear = mods[AnimalForm.BEAR]
        assert bear.phys_def_multiplier > 1.0
        assert bear.mag_def_multiplier > 1.0

    def test_bear_reduces_speed(self) -> None:
        mods = load_animal_form_modifiers()
        bear = mods[AnimalForm.BEAR]
        assert bear.speed_multiplier < 1.0

    def test_wolf_boosts_physical_attack(self) -> None:
        mods = load_animal_form_modifiers()
        wolf = mods[AnimalForm.WOLF]
        assert wolf.phys_atk_multiplier > 1.0

    def test_eagle_boosts_speed(self) -> None:
        mods = load_animal_form_modifiers()
        eagle = mods[AnimalForm.EAGLE]
        assert eagle.speed_multiplier > 1.0

    def test_eagle_boosts_magical_attack(self) -> None:
        mods = load_animal_form_modifiers()
        eagle = mods[AnimalForm.EAGLE]
        assert eagle.mag_atk_multiplier > 1.0

    def test_serpent_boosts_magical_attack(self) -> None:
        mods = load_animal_form_modifiers()
        serpent = mods[AnimalForm.SERPENT]
        assert serpent.mag_atk_multiplier > 1.0
