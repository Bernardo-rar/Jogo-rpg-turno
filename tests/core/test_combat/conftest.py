"""Fixtures e constantes compartilhadas para testes de combate."""

import pytest

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_modifiers import ClassModifiers
from src.core.elements.elemental_profile import ElementalProfile

SIMPLE_MODS = ClassModifiers(
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

# Alias para backward compatibility
SIMPLE_MODIFIERS = SIMPLE_MODS

EMPTY_THRESHOLDS = ThresholdCalculator({})


def _build_char(
    name: str,
    speed: int = 10,
    profile: ElementalProfile | None = None,
) -> Character:
    """Cria Character com attrs=10, mods simples. Aceita speed e profile."""
    attrs = Attributes()
    for attr_type in AttributeType:
        attrs.set(attr_type, 10)
    if speed != 10:
        attrs.set(AttributeType.DEXTERITY, speed)
    config = CharacterConfig(
        class_modifiers=SIMPLE_MODS,
        threshold_calculator=EMPTY_THRESHOLDS,
        elemental_profile=profile,
    )
    return Character(name, attrs, config)


@pytest.fixture
def make_char():
    """Fixture-factory para criar Characters de teste com defaults simples."""
    return _build_char
