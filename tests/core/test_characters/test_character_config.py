"""Testes para CharacterConfig dataclass."""

import dataclasses

import pytest

from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_modifiers import ClassModifiers
from src.core.characters.position import Position
from src.core.effects.effect_manager import EffectManager
from src.core.elements.elemental_profile import ElementalProfile

MODS = ClassModifiers(
    hit_dice=10, mod_hp_flat=0, mod_hp_mult=8, mana_multiplier=6,
    mod_atk_physical=5, mod_atk_magical=3, mod_def_physical=4,
    mod_def_magical=2, regen_hp_mod=3, regen_mana_mod=2,
)
EMPTY_THRESHOLDS = ThresholdCalculator({})


class TestCharacterConfigDefaults:

    def test_default_level_is_1(self) -> None:
        config = CharacterConfig(
            class_modifiers=MODS,
            threshold_calculator=EMPTY_THRESHOLDS,
        )
        assert config.level == 1

    def test_default_position_is_front(self) -> None:
        config = CharacterConfig(
            class_modifiers=MODS,
            threshold_calculator=EMPTY_THRESHOLDS,
        )
        assert config.position == Position.FRONT

    def test_default_elemental_profile_is_none(self) -> None:
        config = CharacterConfig(
            class_modifiers=MODS,
            threshold_calculator=EMPTY_THRESHOLDS,
        )
        assert config.elemental_profile is None

    def test_default_effect_manager_is_none(self) -> None:
        config = CharacterConfig(
            class_modifiers=MODS,
            threshold_calculator=EMPTY_THRESHOLDS,
        )
        assert config.effect_manager is None


class TestCharacterConfigRequired:

    def test_requires_class_modifiers(self) -> None:
        with pytest.raises(TypeError):
            CharacterConfig(threshold_calculator=EMPTY_THRESHOLDS)

    def test_requires_threshold_calculator(self) -> None:
        with pytest.raises(TypeError):
            CharacterConfig(class_modifiers=MODS)


class TestCharacterConfigFrozen:

    def test_is_frozen(self) -> None:
        config = CharacterConfig(
            class_modifiers=MODS,
            threshold_calculator=EMPTY_THRESHOLDS,
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            config.level = 5

    def test_with_all_fields(self) -> None:
        profile = ElementalProfile()
        manager = EffectManager()
        config = CharacterConfig(
            class_modifiers=MODS,
            threshold_calculator=EMPTY_THRESHOLDS,
            level=5,
            position=Position.BACK,
            elemental_profile=profile,
            effect_manager=manager,
        )
        assert config.level == 5
        assert config.position == Position.BACK
        assert config.elemental_profile is profile
        assert config.effect_manager is manager
