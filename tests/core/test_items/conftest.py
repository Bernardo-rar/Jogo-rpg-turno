"""Fixtures e constantes compartilhadas para testes de items."""

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_modifiers import ClassModifiers
from src.core.combat.damage import DamageType
from src.core.combat.targeting import AttackRange
from src.core.items.damage_kind import DamageKind
from src.core.items.weapon import Weapon
from src.core.items.weapon_category import WeaponCategory
from src.core.items.weapon_type import WeaponType

SIMPLE_MODS = ClassModifiers(
    hit_dice=10, vida_mod=0, mod_hp=5,
    mana_multiplier=6,
    mod_atk_physical=5, mod_atk_magical=5,
    mod_def_physical=3, mod_def_magical=3,
    regen_hp_mod=2, regen_mana_mod=2,
)

EMPTY_THRESHOLDS = ThresholdCalculator({})

LONGSWORD = Weapon(
    name="Longsword",
    weapon_type=WeaponType.SWORD,
    damage_kind=DamageKind.SLASHING,
    damage_type=DamageType.PHYSICAL,
    weapon_die=8,
    attack_range=AttackRange.MELEE,
    category=WeaponCategory.MARTIAL,
)

ARCANE_STAFF = Weapon(
    name="Arcane Staff",
    weapon_type=WeaponType.STAFF,
    damage_kind=DamageKind.BLUDGEONING,
    damage_type=DamageType.MAGICAL,
    weapon_die=8,
    attack_range=AttackRange.RANGED,
    category=WeaponCategory.MAGICAL,
)


def make_attrs(value: int = 10) -> Attributes:
    """Cria Attributes com todos os atributos no mesmo valor."""
    attrs = Attributes()
    for attr_type in AttributeType:
        attrs.set(attr_type, value)
    return attrs


def make_item_config(**overrides: object) -> CharacterConfig:
    """Cria CharacterConfig com defaults simples para testes de items."""
    defaults: dict[str, object] = {
        "class_modifiers": SIMPLE_MODS,
        "threshold_calculator": EMPTY_THRESHOLDS,
    }
    defaults.update(overrides)
    return CharacterConfig(**defaults)  # type: ignore[arg-type]
