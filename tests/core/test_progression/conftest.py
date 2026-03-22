"""Fixtures e constantes compartilhadas para testes de progressao."""

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.characters.class_modifiers import ClassModifiers

SIMPLE_MODS = ClassModifiers(
    hit_dice=12, mod_hp_flat=0, mod_hp_mult=10,
    mana_multiplier=6, mod_atk_physical=10, mod_atk_magical=6,
    mod_def_physical=5, mod_def_magical=3,
    regen_hp_mod=5, regen_mana_mod=3,
)

EMPTY_THRESHOLDS: dict[str, list[dict[str, int]]] = {}


def make_attrs(
    con: int = 5, intelligence: int = 6, mind: int = 4,
) -> Attributes:
    """Cria Attributes padrao para testes de progressao."""
    attrs = Attributes()
    attrs.set(AttributeType.STRENGTH, 10)
    attrs.set(AttributeType.DEXTERITY, 8)
    attrs.set(AttributeType.CONSTITUTION, con)
    attrs.set(AttributeType.INTELLIGENCE, intelligence)
    attrs.set(AttributeType.WISDOM, 7)
    attrs.set(AttributeType.CHARISMA, 5)
    attrs.set(AttributeType.MIND, mind)
    return attrs
