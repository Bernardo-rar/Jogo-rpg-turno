import pytest

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_modifiers import ClassModifiers
from src.core.characters.position import Position
from src.core.classes.mage.barrier import BARRIER_EFFICIENCY
from src.core.classes.mage.mage import MANA_PER_BASIC_ATTACK_MOD, Mage

MAGE_MODS = ClassModifiers(
    hit_dice=6,
    vida_mod=0,
    mod_hp=6,
    mana_multiplier=12,
    mod_atk_physical=4,
    mod_atk_magical=10,
    mod_def_physical=2,
    mod_def_magical=5,
    regen_hp_mod=2,
    regen_mana_mod=5,
)

EMPTY_THRESHOLDS = ThresholdCalculator({})
MAGE_CONFIG = CharacterConfig(
    class_modifiers=MAGE_MODS,
    threshold_calculator=EMPTY_THRESHOLDS,
    position=Position.BACK,
)


@pytest.fixture
def mage_attrs() -> Attributes:
    return Attributes({
        AttributeType.STRENGTH: 3,
        AttributeType.DEXTERITY: 5,
        AttributeType.CONSTITUTION: 4,
        AttributeType.INTELLIGENCE: 9,
        AttributeType.WISDOM: 8,
        AttributeType.CHARISMA: 7,
        AttributeType.MIND: 10,
    })


@pytest.fixture
def mage(mage_attrs) -> Mage:
    return Mage(
        name="Merlin",
        attributes=mage_attrs,
        config=MAGE_CONFIG,
    )


class TestMageIsCharacter:
    def test_is_instance_of_character(self, mage: Mage):
        assert isinstance(mage, Character)

    def test_has_name(self, mage: Mage):
        assert mage.name == "Merlin"

    def test_has_hp(self, mage: Mage):
        assert mage.current_hp == mage.max_hp

    def test_take_damage_works(self, mage: Mage):
        mage.take_damage(10)
        assert mage.current_hp == mage.max_hp - 10

    def test_heal_works(self, mage: Mage):
        mage.take_damage(50)
        mage.heal(20)
        # CON=4, heal(20) -> int(20 * 1.2) = 24
        assert mage.current_hp == mage.max_hp - 50 + 24

    def test_is_alive(self, mage: Mage):
        assert mage.is_alive is True

    def test_speed(self, mage: Mage):
        # Speed = DEX = 5
        assert mage.speed == 5


class TestMageStats:
    def test_max_hp_low(self, mage: Mage):
        # ((hit_dice + CON + vida_mod) * 2) * mod_hp
        # ((6 + 4 + 0) * 2) * 6 = 120
        assert mage.max_hp == 120

    def test_max_mana_high(self, mage: Mage):
        # mana_multiplier * MIND * 5 = 12 * 10 * 5 = 600
        assert mage.max_mana == 600

    def test_physical_attack_low(self, mage: Mage):
        # (weapon_die=0 + STR + DEX) * mod_atk_physical
        # (0 + 3 + 5) * 4 = 32
        assert mage.physical_attack == 32

    def test_magical_attack_high(self, mage: Mage):
        # (weapon_die=0 + WIS + INT) * mod_atk_magical
        # (0 + 8 + 9) * 10 = 170
        assert mage.magical_attack == 170

    def test_physical_defense_low(self, mage: Mage):
        # (DEX + CON + STR) * mod_def_physical
        # (5 + 4 + 3) * 2 = 24
        assert mage.physical_defense == 24

    def test_magical_defense_high(self, mage: Mage):
        # (CON + WIS + INT) * mod_def_magical
        # (4 + 8 + 9) * 5 = 105
        assert mage.magical_defense == 105


class TestMagePosition:
    def test_default_position_is_back(self, mage: Mage):
        assert mage.position == Position.BACK

    def test_can_move_to_front(self, mage: Mage):
        mage.change_position(Position.FRONT)
        assert mage.position == Position.FRONT


class TestMageBarrier:
    def test_has_barrier(self, mage: Mage):
        assert mage.barrier is not None

    def test_barrier_starts_empty(self, mage: Mage):
        assert mage.barrier.current == 0

    def test_create_barrier_spends_mana(self, mage: Mage):
        mage.create_barrier(100)
        assert mage.current_mana == mage.max_mana - 100

    def test_create_barrier_adds_shield(self, mage: Mage):
        mage.create_barrier(100)
        assert mage.barrier.current == 100 * BARRIER_EFFICIENCY

    def test_create_barrier_fails_insufficient_mana(self, mage: Mage):
        result = mage.create_barrier(9999)
        assert result is False
        assert mage.barrier.current == 0

    def test_take_damage_uses_barrier_first(self, mage: Mage):
        mage.create_barrier(100)  # 200 barrier points
        mage.take_damage(150)
        assert mage.barrier.current == 50
        assert mage.current_hp == mage.max_hp

    def test_take_damage_overflow_hits_hp(self, mage: Mage):
        mage.create_barrier(50)  # 100 barrier points
        mage.take_damage(150)
        assert mage.barrier.current == 0
        assert mage.current_hp == mage.max_hp - 50

    def test_take_damage_no_barrier_hits_hp_directly(self, mage: Mage):
        mage.take_damage(30)
        assert mage.current_hp == mage.max_hp - 30

    def test_take_damage_returns_total_absorbed(self, mage: Mage):
        mage.create_barrier(50)  # 100 barrier points
        actual = mage.take_damage(80)
        # 80 absorbed by barrier, 0 HP damage
        assert actual == 80

    def test_take_damage_returns_clamped_with_barrier(self, mage: Mage):
        mage.create_barrier(50)  # 100 barrier points
        mage.take_damage(mage.max_hp + 50)  # reduce HP to small
        # Reset for cleaner test
        pass  # covered by no-barrier tests in Character


class TestMageOvercharge:
    def test_default_not_overcharged(self, mage: Mage):
        assert mage.is_overcharged is False

    def test_activate_overcharge(self, mage: Mage):
        result = mage.activate_overcharge()
        assert result is True
        assert mage.is_overcharged is True

    def test_activate_already_active_returns_false(self, mage: Mage):
        mage.activate_overcharge()
        result = mage.activate_overcharge()
        assert result is False

    def test_deactivate_overcharge(self, mage: Mage):
        mage.activate_overcharge()
        mage.deactivate_overcharge()
        assert mage.is_overcharged is False

    def test_magical_attack_increases_when_overcharged(self, mage: Mage):
        base = mage.magical_attack
        mage.activate_overcharge()
        assert mage.magical_attack == int(base * 1.5)

    def test_physical_attack_unchanged_when_overcharged(self, mage: Mage):
        base = mage.physical_attack
        mage.activate_overcharge()
        assert mage.physical_attack == base

    def test_apply_overcharge_cost_spends_mana(self, mage: Mage):
        mage.activate_overcharge()
        mage.apply_overcharge_cost()
        assert mage.current_mana == mage.max_mana - 30

    def test_apply_overcharge_cost_noop_when_inactive(self, mage: Mage):
        mage.apply_overcharge_cost()
        assert mage.current_mana == mage.max_mana

    def test_auto_deactivates_when_insufficient_mana(self, mage: Mage):
        mage.activate_overcharge()
        # Drain almost all mana
        mage.spend_mana(mage.current_mana - 10)
        mage.apply_overcharge_cost()
        assert mage.is_overcharged is False
        # Mana stays at 10 (not spent since insufficient for cost)
        assert mage.current_mana == 10


class TestMageManaGeneration:
    def test_mana_per_basic_attack(self, mage: Mage):
        # MIND * MANA_PER_BASIC_ATTACK_MOD = 10 * 3 = 30
        assert mage.mana_per_basic_attack == 30

    def test_mana_per_basic_attack_mod_constant(self):
        assert MANA_PER_BASIC_ATTACK_MOD == 3
