"""Testes unitarios para CombatStatsMixin — derived combat stats."""

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_modifiers import ClassModifiers
from src.core.combat.damage import DamageType

SIMPLE_MODS = ClassModifiers(
    hit_dice=10,
    mod_hp_flat=0,
    mod_hp_mult=1,
    mana_multiplier=1,
    mod_atk_physical=2,
    mod_atk_magical=3,
    mod_def_physical=2,
    mod_def_magical=3,
    regen_hp_mod=0,
    regen_mana_mod=0,
)

EMPTY_THRESHOLDS = ThresholdCalculator({})


def _make_char(
    str_val: int = 10,
    dex_val: int = 10,
    con_val: int = 10,
    int_val: int = 10,
    wis_val: int = 10,
    cha_val: int = 10,
    mind_val: int = 10,
    mods: ClassModifiers | None = None,
) -> Character:
    """Cria Character com atributos customizaveis."""
    attrs = Attributes({
        AttributeType.STRENGTH: str_val,
        AttributeType.DEXTERITY: dex_val,
        AttributeType.CONSTITUTION: con_val,
        AttributeType.INTELLIGENCE: int_val,
        AttributeType.WISDOM: wis_val,
        AttributeType.CHARISMA: cha_val,
        AttributeType.MIND: mind_val,
    })
    config = CharacterConfig(
        class_modifiers=mods or SIMPLE_MODS,
        threshold_calculator=EMPTY_THRESHOLDS,
    )
    return Character("TestChar", attrs, config)


class TestAttackPowerPhysical:

    def test_attack_power_physical(self) -> None:
        """attack_power retorna physical_attack quando preferred_attack_type e PHYSICAL."""
        char = _make_char(str_val=12, dex_val=8)
        # physical_attack = (weapon_die=0 + STR + DEX) * mod_atk_physical
        # = (0 + 12 + 8) * 2 = 40
        assert char.physical_attack == 40
        assert char.preferred_attack_type == DamageType.PHYSICAL
        assert char.attack_power == char.physical_attack


class TestAttackPowerMagical:

    def test_attack_power_magical(self) -> None:
        """attack_power retorna magical_attack quando preferred_attack_type e MAGICAL."""
        magical_mods = ClassModifiers(
            hit_dice=10,
            mod_hp_flat=0,
            mod_hp_mult=1,
            mana_multiplier=1,
            mod_atk_physical=2,
            mod_atk_magical=3,
            mod_def_physical=2,
            mod_def_magical=3,
            regen_hp_mod=0,
            regen_mana_mod=0,
            preferred_attack_type=DamageType.MAGICAL,
        )
        char = _make_char(wis_val=14, int_val=6, mods=magical_mods)
        # magical_attack = (weapon_die=0 + WIS + INT) * mod_atk_magical
        # = (0 + 14 + 6) * 3 = 60
        assert char.magical_attack == 60
        assert char.preferred_attack_type == DamageType.MAGICAL
        assert char.attack_power == char.magical_attack


class TestDefenseForPhysical:

    def test_defense_for_physical(self) -> None:
        """defense_for(PHYSICAL) retorna physical_defense."""
        char = _make_char(dex_val=10, con_val=8, str_val=12)
        # physical_defense = (DEX + CON + STR) * mod_def_physical
        # = (10 + 8 + 12) * 2 = 60
        assert char.physical_defense == 60
        assert char.defense_for(DamageType.PHYSICAL) == char.physical_defense


class TestDefenseForMagical:

    def test_defense_for_magical(self) -> None:
        """defense_for(MAGICAL) retorna magical_defense."""
        char = _make_char(con_val=6, wis_val=14, int_val=10)
        # magical_defense = (CON + WIS + INT) * mod_def_magical
        # = (6 + 14 + 10) * 3 = 90
        assert char.magical_defense == 90
        assert char.defense_for(DamageType.MAGICAL) == char.magical_defense
