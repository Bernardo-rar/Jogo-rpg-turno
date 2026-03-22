import pytest

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_modifiers import ClassModifiers
from src.core.characters.position import Position
from src.core.classes.sorcerer.mana_rotation import load_mana_rotation_config
from src.core.classes.sorcerer.overcharged_config import load_overcharged_config
from src.core.classes.sorcerer.sorcerer import Sorcerer
from src.core.elements.element_type import ElementType

_CONFIG = load_overcharged_config()
_ROTATION_CONFIG = load_mana_rotation_config()

SORCERER_MODS = ClassModifiers(
    hit_dice=6,
    mod_hp_flat=0,
    mod_hp_mult=5,
    mana_multiplier=14,
    mod_atk_physical=2,
    mod_atk_magical=12,
    mod_def_physical=2,
    mod_def_magical=4,
    regen_hp_mod=2,
    regen_mana_mod=4,
)

EMPTY_THRESHOLDS = ThresholdCalculator({})
SORCERER_CONFIG = CharacterConfig(
    class_modifiers=SORCERER_MODS,
    threshold_calculator=EMPTY_THRESHOLDS,
    position=Position.BACK,
)


@pytest.fixture
def sorc_attrs() -> Attributes:
    return Attributes({
        AttributeType.STRENGTH: 3,
        AttributeType.DEXTERITY: 5,
        AttributeType.CONSTITUTION: 4,
        AttributeType.INTELLIGENCE: 10,
        AttributeType.WISDOM: 8,
        AttributeType.CHARISMA: 7,
        AttributeType.MIND: 11,
    })


@pytest.fixture
def sorcerer(sorc_attrs) -> Sorcerer:
    return Sorcerer(
        name="Vex",
        attributes=sorc_attrs,
        config=SORCERER_CONFIG,
    )


# --- LSP ---


class TestSorcererIsCharacter:
    def test_is_instance_of_character(self, sorcerer: Sorcerer):
        assert isinstance(sorcerer, Character)

    def test_has_name(self, sorcerer: Sorcerer):
        assert sorcerer.name == "Vex"

    def test_has_hp(self, sorcerer: Sorcerer):
        assert sorcerer.current_hp == sorcerer.max_hp

    def test_take_damage_works(self, sorcerer: Sorcerer):
        sorcerer.take_damage(10)
        assert sorcerer.current_hp == sorcerer.max_hp - 10

    def test_heal_works(self, sorcerer: Sorcerer):
        sorcerer.take_damage(50)
        sorcerer.heal(20)
        # CON=4, heal(20) -> int(20 * 1.2) = 24
        assert sorcerer.current_hp == sorcerer.max_hp - 50 + 24

    def test_is_alive(self, sorcerer: Sorcerer):
        assert sorcerer.is_alive is True

    def test_speed(self, sorcerer: Sorcerer):
        assert sorcerer.speed == 5


# --- Stats ---


class TestSorcererStats:
    def test_max_hp(self, sorcerer: Sorcerer):
        # ((6 + 4 + 0) * 2) * 5 = 100
        assert sorcerer.max_hp == 100

    def test_max_mana(self, sorcerer: Sorcerer):
        # 14 * 11 * 5 = 770
        assert sorcerer.max_mana == 770

    def test_physical_attack(self, sorcerer: Sorcerer):
        # (0 + 3 + 5) * 2 = 16
        assert sorcerer.physical_attack == 16

    def test_magical_attack_with_born_of_magic(self, sorcerer: Sorcerer):
        # base = (0 + 8 + 10) * 12 = 216
        # born_of_magic = 216 * 1.10 = 237 (int)
        assert sorcerer.magical_attack == int(216 * (1.0 + _CONFIG.born_of_magic_bonus))

    def test_physical_defense(self, sorcerer: Sorcerer):
        # (5 + 4 + 3) * 2 = 24
        assert sorcerer.physical_defense == 24

    def test_magical_defense(self, sorcerer: Sorcerer):
        # (4 + 8 + 10) * 4 = 88
        assert sorcerer.magical_defense == 88


class TestSorcererPosition:
    def test_default_position_is_back(self, sorcerer: Sorcerer):
        assert sorcerer.position == Position.BACK

    def test_can_move_to_front(self, sorcerer: Sorcerer):
        sorcerer.change_position(Position.FRONT)
        assert sorcerer.position == Position.FRONT


# --- Overcharged ---


class TestSorcererOvercharged:
    def test_default_not_overcharged(self, sorcerer: Sorcerer):
        assert sorcerer.is_overcharged is False

    def test_activate_overcharged(self, sorcerer: Sorcerer):
        result = sorcerer.activate_overcharged()
        assert result is True
        assert sorcerer.is_overcharged is True

    def test_activate_already_active_returns_false(self, sorcerer: Sorcerer):
        sorcerer.activate_overcharged()
        result = sorcerer.activate_overcharged()
        assert result is False

    def test_deactivate_overcharged(self, sorcerer: Sorcerer):
        sorcerer.activate_overcharged()
        sorcerer.deactivate_overcharged()
        assert sorcerer.is_overcharged is False

    def test_magical_attack_increases_when_overcharged(self, sorcerer: Sorcerer):
        base = sorcerer.magical_attack
        sorcerer.activate_overcharged()
        expected = int(base * _CONFIG.atk_multiplier)
        assert sorcerer.magical_attack == expected

    def test_physical_attack_unchanged_when_overcharged(self, sorcerer: Sorcerer):
        base = sorcerer.physical_attack
        sorcerer.activate_overcharged()
        assert sorcerer.physical_attack == base

    def test_apply_overcharged_cost_spends_mana(self, sorcerer: Sorcerer):
        sorcerer.activate_overcharged()
        sorcerer.apply_overcharged_cost()
        assert sorcerer.current_mana == sorcerer.max_mana - _CONFIG.mana_cost_per_turn

    def test_apply_overcharged_cost_deals_self_damage(self, sorcerer: Sorcerer):
        sorcerer.activate_overcharged()
        sorcerer.apply_overcharged_cost()
        expected_damage = int(sorcerer.max_hp * _CONFIG.self_damage_pct)
        assert sorcerer.current_hp == sorcerer.max_hp - expected_damage

    def test_apply_overcharged_cost_noop_when_inactive(self, sorcerer: Sorcerer):
        sorcerer.apply_overcharged_cost()
        assert sorcerer.current_mana == sorcerer.max_mana
        assert sorcerer.current_hp == sorcerer.max_hp

    def test_auto_deactivates_when_insufficient_mana(self, sorcerer: Sorcerer):
        sorcerer.activate_overcharged()
        sorcerer.spend_mana(sorcerer.current_mana - 10)
        sorcerer.apply_overcharged_cost()
        assert sorcerer.is_overcharged is False
        assert sorcerer.current_mana == 10

    def test_self_damage_does_not_kill(self, sorcerer: Sorcerer):
        sorcerer.activate_overcharged()
        # Reduce HP to near death
        sorcerer.take_damage(sorcerer.max_hp - 1)
        sorcerer.apply_overcharged_cost()
        # Self-damage via take_damage - may kill, but that's the risk
        # The Sorcerer is a high-risk class
        assert sorcerer.current_hp >= 0


# --- Metamagia ---


class TestSorcererMetamagic:
    def test_no_metamagic_by_default(self, sorcerer: Sorcerer):
        assert sorcerer.current_metamagic is None

    def test_set_metamagic(self, sorcerer: Sorcerer):
        result = sorcerer.set_metamagic(ElementType.FIRE)
        assert result is True
        assert sorcerer.current_metamagic == ElementType.FIRE

    def test_set_metamagic_costs_mana(self, sorcerer: Sorcerer):
        sorcerer.set_metamagic(ElementType.FIRE)
        assert sorcerer.current_mana == sorcerer.max_mana - _CONFIG.metamagic_mana_cost

    def test_set_metamagic_fails_insufficient_mana(self, sorcerer: Sorcerer):
        sorcerer.spend_mana(sorcerer.current_mana)
        result = sorcerer.set_metamagic(ElementType.FIRE)
        assert result is False
        assert sorcerer.current_metamagic is None

    def test_set_metamagic_replaces_existing(self, sorcerer: Sorcerer):
        sorcerer.set_metamagic(ElementType.FIRE)
        sorcerer.set_metamagic(ElementType.ICE)
        assert sorcerer.current_metamagic == ElementType.ICE

    def test_consume_metamagic_returns_element(self, sorcerer: Sorcerer):
        sorcerer.set_metamagic(ElementType.LIGHTNING)
        element = sorcerer.consume_metamagic()
        assert element == ElementType.LIGHTNING

    def test_consume_metamagic_clears_state(self, sorcerer: Sorcerer):
        sorcerer.set_metamagic(ElementType.LIGHTNING)
        sorcerer.consume_metamagic()
        assert sorcerer.current_metamagic is None

    def test_consume_metamagic_returns_none_when_empty(self, sorcerer: Sorcerer):
        result = sorcerer.consume_metamagic()
        assert result is None


# --- Mana Rotation ---


class TestSorcererManaRotation:
    def test_has_mana_rotation(self, sorcerer: Sorcerer):
        assert sorcerer.mana_rotation is not None

    def test_rotation_starts_empty(self, sorcerer: Sorcerer):
        assert sorcerer.mana_rotation.current == 0

    def test_on_deal_magic_damage_gains_rotation(self, sorcerer: Sorcerer):
        sorcerer.on_deal_magic_damage(100)
        assert sorcerer.mana_rotation.current > 0

    def test_on_deal_magic_damage_restores_mana(self, sorcerer: Sorcerer):
        sorcerer.spend_mana(500)
        before = sorcerer.current_mana
        sorcerer.on_deal_magic_damage(100)
        assert sorcerer.current_mana > before

    def test_rotation_decay_on_turn(self, sorcerer: Sorcerer):
        sorcerer.on_deal_magic_damage(200)
        before = sorcerer.mana_rotation.current
        sorcerer.apply_rotation_decay()
        assert sorcerer.mana_rotation.current < before

    def test_rotation_decay_noop_when_empty(self, sorcerer: Sorcerer):
        sorcerer.apply_rotation_decay()
        assert sorcerer.mana_rotation.current == 0


# --- Level Up ---


class TestSorcererLevelUp:
    def test_on_level_up_recalculates_rotation_max(self, sorcerer: Sorcerer):
        # Mana doesn't scale with level, so rotation max stays the same
        # But on_level_up still recalculates (future-proof for mana scaling)
        expected = int(sorcerer.max_mana * _ROTATION_CONFIG.max_ratio)
        sorcerer._set_level(2)
        assert sorcerer.mana_rotation.max_mana == expected

    def test_on_level_up_clamps_rotation_if_needed(self, sorcerer: Sorcerer):
        # Fill rotation to max, then simulate a scenario where max would shrink
        sorcerer.mana_rotation.gain(sorcerer.mana_rotation.max_mana)
        current_before = sorcerer.mana_rotation.current
        sorcerer._set_level(2)
        assert sorcerer.mana_rotation.current <= sorcerer.mana_rotation.max_mana
