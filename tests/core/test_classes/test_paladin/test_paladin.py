import pytest

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_modifiers import ClassModifiers
from src.core.characters.position import Position
from src.core.classes.paladin.aura import Aura
from src.core.classes.paladin.divine_favor import DivineFavor
from src.core.classes.paladin.paladin import Paladin

# Paladin stats: STR=8, DEX=6, CON=8, INT=5, WIS=7, CHA=9, MIND=6
# Modifiers from paladin.json: hit_dice=10, mod_hp=10, mod_atk_physical=8,
#   mod_atk_magical=6, mod_def_physical=5, mod_def_magical=4
# base physical_attack = (0 + 8 + 6) * 8 = 112
# base physical_defense = (6 + 8 + 8) * 5 = 110
# base magical_attack = (0 + 7 + 5) * 6 = 72
# base magical_defense = (8 + 7 + 5) * 4 = 80

PALADIN_MODIFIERS = ClassModifiers.from_json("data/classes/paladin.json")
EMPTY_THRESHOLDS = ThresholdCalculator({})
PALADIN_CONFIG = CharacterConfig(
    class_modifiers=PALADIN_MODIFIERS,
    threshold_calculator=EMPTY_THRESHOLDS,
)


def _paladin_attrs() -> Attributes:
    attrs = Attributes()
    attrs.set(AttributeType.STRENGTH, 8)
    attrs.set(AttributeType.DEXTERITY, 6)
    attrs.set(AttributeType.CONSTITUTION, 8)
    attrs.set(AttributeType.INTELLIGENCE, 5)
    attrs.set(AttributeType.WISDOM, 7)
    attrs.set(AttributeType.CHARISMA, 9)
    attrs.set(AttributeType.MIND, 6)
    return attrs


@pytest.fixture
def paladin() -> Paladin:
    return Paladin(
        "Galahad",
        _paladin_attrs(),
        PALADIN_CONFIG,
    )


class TestPaladinIsCharacter:
    """LSP: Paladin deve funcionar como Character em qualquer contexto."""

    def test_is_instance_of_character(self, paladin: Paladin):
        assert isinstance(paladin, Character)

    def test_has_name(self, paladin: Paladin):
        assert paladin.name == "Galahad"

    def test_has_hp(self, paladin: Paladin):
        assert paladin.max_hp > 0

    def test_take_damage_works(self, paladin: Paladin):
        original = paladin.current_hp
        paladin.take_damage(10)
        assert paladin.current_hp == original - 10

    def test_heal_works(self, paladin: Paladin):
        paladin.take_damage(20)
        paladin.heal(10)
        # CON=8, heal(10) -> int(10 * 1.4) = 14
        assert paladin.current_hp == paladin.max_hp - 20 + 14

    def test_is_alive(self, paladin: Paladin):
        assert paladin.is_alive is True

    def test_speed(self, paladin: Paladin):
        assert paladin.speed == 6  # DEX


class TestPaladinPosition:
    def test_default_position_is_front(self, paladin: Paladin):
        assert paladin.position == Position.FRONT


class TestPaladinBaseStats:
    def test_physical_attack(self, paladin: Paladin):
        assert paladin.physical_attack == 112

    def test_physical_defense(self, paladin: Paladin):
        assert paladin.physical_defense == 110

    def test_magical_attack(self, paladin: Paladin):
        assert paladin.magical_attack == 72

    def test_magical_defense(self, paladin: Paladin):
        assert paladin.magical_defense == 80


class TestPaladinDivineFavor:
    def test_has_divine_favor(self, paladin: Paladin):
        assert isinstance(paladin.divine_favor, DivineFavor)

    def test_favor_starts_at_zero(self, paladin: Paladin):
        assert paladin.divine_favor.current == 0

    def test_gain_favor_from_protect(self, paladin: Paladin):
        paladin.gain_favor_from_protect()
        assert paladin.divine_favor.current == 1

    def test_gain_favor_from_buff(self, paladin: Paladin):
        paladin.gain_favor_from_buff()
        assert paladin.divine_favor.current == 1

    def test_gain_favor_from_heal(self, paladin: Paladin):
        paladin.gain_favor_from_heal()
        assert paladin.divine_favor.current == 1

    def test_multiple_favor_sources_accumulate(self, paladin: Paladin):
        paladin.gain_favor_from_protect()
        paladin.gain_favor_from_buff()
        paladin.gain_favor_from_heal()
        assert paladin.divine_favor.current == 3


class TestPaladinAura:
    def test_default_aura_is_none(self, paladin: Paladin):
        assert paladin.aura == Aura.NONE

    def test_change_aura_to_protection(self, paladin: Paladin):
        paladin.change_aura(Aura.PROTECTION)
        assert paladin.aura == Aura.PROTECTION

    def test_change_aura_to_attack(self, paladin: Paladin):
        paladin.change_aura(Aura.ATTACK)
        assert paladin.aura == Aura.ATTACK

    def test_change_aura_to_vitality(self, paladin: Paladin):
        paladin.change_aura(Aura.VITALITY)
        assert paladin.aura == Aura.VITALITY

    def test_change_back_to_none(self, paladin: Paladin):
        paladin.change_aura(Aura.PROTECTION)
        paladin.change_aura(Aura.NONE)
        assert paladin.aura == Aura.NONE


class TestPaladinProtectionAura:
    def test_protection_aura_boosts_physical_defense(self, paladin: Paladin):
        paladin.change_aura(Aura.PROTECTION)
        # 110 * 1.15 = 126.5 -> 126
        assert paladin.physical_defense == int(110 * 1.15)

    def test_protection_aura_boosts_magical_defense(self, paladin: Paladin):
        paladin.change_aura(Aura.PROTECTION)
        # 80 * 1.15 = 92
        assert paladin.magical_defense == int(80 * 1.15)

    def test_protection_aura_no_attack_change(self, paladin: Paladin):
        paladin.change_aura(Aura.PROTECTION)
        assert paladin.physical_attack == 112


class TestPaladinAttackAura:
    def test_attack_aura_boosts_physical_attack(self, paladin: Paladin):
        paladin.change_aura(Aura.ATTACK)
        # 112 * 1.15 = 128.8 -> 128
        assert paladin.physical_attack == int(112 * 1.15)

    def test_attack_aura_boosts_magical_attack(self, paladin: Paladin):
        paladin.change_aura(Aura.ATTACK)
        # 72 * 1.15 = 82.8 -> 82
        assert paladin.magical_attack == int(72 * 1.15)

    def test_attack_aura_no_defense_change(self, paladin: Paladin):
        paladin.change_aura(Aura.ATTACK)
        assert paladin.physical_defense == 110


class TestPaladinVitalityAura:
    def test_vitality_aura_boosts_hp_regen(self, paladin: Paladin):
        base_regen = paladin.hp_regen
        paladin.change_aura(Aura.VITALITY)
        assert paladin.hp_regen == int(base_regen * 1.15)


class TestPaladinGlimpseOfGlory:
    def test_cannot_activate_without_aura(self, paladin: Paladin):
        paladin.divine_favor.gain(10)
        result = paladin.activate_glimpse_of_glory()
        assert result is False

    def test_cannot_activate_without_favor(self, paladin: Paladin):
        paladin.change_aura(Aura.PROTECTION)
        result = paladin.activate_glimpse_of_glory()
        assert result is False

    def test_activate_spends_favor(self, paladin: Paladin):
        paladin.change_aura(Aura.PROTECTION)
        paladin.divine_favor.gain(10)
        result = paladin.activate_glimpse_of_glory()
        assert result is True
        # favor_cost = 5
        assert paladin.divine_favor.current == 5

    def test_is_glory_active(self, paladin: Paladin):
        paladin.change_aura(Aura.PROTECTION)
        paladin.divine_favor.gain(10)
        paladin.activate_glimpse_of_glory()
        assert paladin.is_glory_active is True

    def test_cannot_activate_twice(self, paladin: Paladin):
        paladin.change_aura(Aura.PROTECTION)
        paladin.divine_favor.gain(10)
        paladin.activate_glimpse_of_glory()
        result = paladin.activate_glimpse_of_glory()
        assert result is False

    def test_glory_doubles_protection_defense_bonus(self, paladin: Paladin):
        paladin.change_aura(Aura.PROTECTION)
        paladin.divine_favor.gain(10)
        paladin.activate_glimpse_of_glory()
        # bonus: 1.0 + (1.15 - 1.0) * 2.0 = 1.30
        glory_mult = 1.0 + (1.15 - 1.0) * 2.0
        assert paladin.physical_defense == int(110 * glory_mult)

    def test_glory_doubles_attack_aura_bonus(self, paladin: Paladin):
        paladin.change_aura(Aura.ATTACK)
        paladin.divine_favor.gain(10)
        paladin.activate_glimpse_of_glory()
        assert paladin.physical_attack == int(112 * 1.30)


class TestPaladinGloryDuration:
    def test_tick_glory_decrements(self, paladin: Paladin):
        paladin.change_aura(Aura.PROTECTION)
        paladin.divine_favor.gain(10)
        paladin.activate_glimpse_of_glory()
        paladin.tick_glory()
        assert paladin.is_glory_active is True

    def test_glory_expires_after_duration(self, paladin: Paladin):
        paladin.change_aura(Aura.PROTECTION)
        paladin.divine_favor.gain(10)
        paladin.activate_glimpse_of_glory()
        # duration_turns = 3
        paladin.tick_glory()
        paladin.tick_glory()
        paladin.tick_glory()
        assert paladin.is_glory_active is False

    def test_glory_expired_stats_return_to_normal(self, paladin: Paladin):
        paladin.change_aura(Aura.PROTECTION)
        paladin.divine_favor.gain(10)
        paladin.activate_glimpse_of_glory()
        for _ in range(3):
            paladin.tick_glory()
        # Volta ao bonus normal da aura (1.15)
        assert paladin.physical_defense == int(110 * 1.15)

    def test_tick_without_glory_is_noop(self, paladin: Paladin):
        paladin.tick_glory()
        assert paladin.is_glory_active is False
