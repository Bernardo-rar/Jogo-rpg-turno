import pytest

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character import Character
from src.core.characters.class_modifiers import ClassModifiers
from src.core.characters.position import Position
from src.core.classes.cleric.cleric import (
    CHANNEL_ATK_MULTIPLIER,
    CHANNEL_DEF_MULTIPLIER,
    CHANNEL_DIVINITY_COST,
    HEAL_MANA_COST,
    HEALING_POWER_MOD,
    Cleric,
)
from src.core.classes.cleric.divinity import Divinity

CLERIC_MODS = ClassModifiers(
    hit_dice=8,
    vida_mod=0,
    mod_hp=8,
    mana_multiplier=8,
    mod_atk_physical=5,
    mod_atk_magical=8,
    mod_def_physical=3,
    mod_def_magical=4,
    regen_hp_mod=3,
    regen_mana_mod=4,
)

EMPTY_THRESHOLDS = ThresholdCalculator({})


@pytest.fixture
def cleric_attrs() -> Attributes:
    return Attributes({
        AttributeType.STRENGTH: 4,
        AttributeType.DEXTERITY: 5,
        AttributeType.CONSTITUTION: 6,
        AttributeType.INTELLIGENCE: 7,
        AttributeType.WISDOM: 9,
        AttributeType.CHARISMA: 8,
        AttributeType.MIND: 7,
    })


@pytest.fixture
def cleric(cleric_attrs) -> Cleric:
    return Cleric(
        name="Aurelia",
        attributes=cleric_attrs,
        class_modifiers=CLERIC_MODS,
        threshold_calculator=EMPTY_THRESHOLDS,
        divinity=Divinity.HOLY,
    )


@pytest.fixture
def wounded_ally(cleric_attrs) -> Character:
    ally = Character(
        name="Ally",
        attributes=cleric_attrs,
        class_modifiers=CLERIC_MODS,
        threshold_calculator=EMPTY_THRESHOLDS,
    )
    ally.take_damage(200)
    return ally


class TestClericIsCharacter:
    def test_is_instance_of_character(self, cleric: Cleric):
        assert isinstance(cleric, Character)

    def test_has_name(self, cleric: Cleric):
        assert cleric.name == "Aurelia"

    def test_has_hp(self, cleric: Cleric):
        assert cleric.current_hp == cleric.max_hp

    def test_take_damage_works(self, cleric: Cleric):
        cleric.take_damage(10)
        assert cleric.current_hp == cleric.max_hp - 10

    def test_heal_works(self, cleric: Cleric):
        cleric.take_damage(50)
        cleric.heal(20)
        assert cleric.current_hp == cleric.max_hp - 30

    def test_is_alive(self, cleric: Cleric):
        assert cleric.is_alive is True

    def test_speed(self, cleric: Cleric):
        # Speed = DEX = 5
        assert cleric.speed == 5


class TestClericStats:
    def test_max_hp_medium(self, cleric: Cleric):
        # ((hit_dice + CON + vida_mod) * 2) * mod_hp
        # ((8 + 6 + 0) * 2) * 8 = 224
        assert cleric.max_hp == 224

    def test_max_mana_medium_high(self, cleric: Cleric):
        # mana_multiplier * MIND * 10 = 8 * 7 * 10 = 560
        assert cleric.max_mana == 560

    def test_physical_attack(self, cleric: Cleric):
        # (0 + STR + DEX) * mod_atk_physical = (0 + 4 + 5) * 5 = 45
        assert cleric.physical_attack == 45

    def test_magical_attack(self, cleric: Cleric):
        # (0 + WIS + INT) * mod_atk_magical = (0 + 9 + 7) * 8 = 128
        assert cleric.magical_attack == 128

    def test_physical_defense(self, cleric: Cleric):
        # (DEX + CON + STR) * mod_def_physical = (5 + 6 + 4) * 3 = 45
        assert cleric.physical_defense == 45

    def test_magical_defense(self, cleric: Cleric):
        # (CON + WIS + INT) * mod_def_magical = (6 + 9 + 7) * 4 = 88
        assert cleric.magical_defense == 88


class TestClericPosition:
    def test_default_position_is_back(self, cleric: Cleric):
        assert cleric.position == Position.BACK

    def test_can_move_to_front(self, cleric: Cleric):
        cleric.change_position(Position.FRONT)
        assert cleric.position == Position.FRONT


class TestClericDivinity:
    def test_has_divinity(self, cleric: Cleric):
        assert cleric.divinity == Divinity.HOLY

    def test_fire_divinity(self, cleric_attrs):
        fire_cleric = Cleric(
            name="Ignis",
            attributes=cleric_attrs,
            class_modifiers=CLERIC_MODS,
            threshold_calculator=EMPTY_THRESHOLDS,
            divinity=Divinity.FIRE,
        )
        assert fire_cleric.divinity == Divinity.FIRE


class TestClericHolyPower:
    def test_has_holy_power(self, cleric: Cleric):
        assert cleric.holy_power is not None

    def test_holy_power_starts_at_zero(self, cleric: Cleric):
        assert cleric.holy_power.current == 0


class TestClericHealing:
    def test_healing_power_formula(self, cleric: Cleric):
        # WIS * HEALING_POWER_MOD * divinity.healing_bonus
        # 9 * 3 * 1.3 = 35.1 -> int = 35
        assert cleric.healing_power == 35

    def test_healing_power_fire_divinity(self, cleric_attrs):
        fire_cleric = Cleric(
            name="Ignis",
            attributes=cleric_attrs,
            class_modifiers=CLERIC_MODS,
            threshold_calculator=EMPTY_THRESHOLDS,
            divinity=Divinity.FIRE,
        )
        # 9 * 3 * 1.0 = 27
        assert fire_cleric.healing_power == 27

    def test_heal_target_heals_ally(self, cleric: Cleric, wounded_ally: Character):
        hp_before = wounded_ally.current_hp
        cleric.heal_target(wounded_ally)
        assert wounded_ally.current_hp == hp_before + cleric.healing_power

    def test_heal_target_spends_mana(self, cleric: Cleric, wounded_ally: Character):
        cleric.heal_target(wounded_ally)
        assert cleric.current_mana == cleric.max_mana - HEAL_MANA_COST

    def test_heal_target_returns_amount_healed(
        self, cleric: Cleric, wounded_ally: Character,
    ):
        healed = cleric.heal_target(wounded_ally)
        assert healed == cleric.healing_power

    def test_heal_target_gains_holy_power(
        self, cleric: Cleric, wounded_ally: Character,
    ):
        cleric.heal_target(wounded_ally)
        assert cleric.holy_power.current == 1

    def test_heal_target_fails_without_mana(
        self, cleric: Cleric, wounded_ally: Character,
    ):
        cleric.spend_mana(cleric.current_mana)
        healed = cleric.heal_target(wounded_ally)
        assert healed == 0

    def test_heal_target_no_holy_power_on_fail(
        self, cleric: Cleric, wounded_ally: Character,
    ):
        cleric.spend_mana(cleric.current_mana)
        cleric.heal_target(wounded_ally)
        assert cleric.holy_power.current == 0


class TestClericChannelDivinity:
    def test_default_not_channeling(self, cleric: Cleric):
        assert cleric.is_channeling is False

    def test_channel_divinity_activates(self, cleric: Cleric, wounded_ally):
        # Build up holy power: heal 3 times
        for _ in range(CHANNEL_DIVINITY_COST):
            cleric.heal_target(wounded_ally)
        result = cleric.channel_divinity()
        assert result is True
        assert cleric.is_channeling is True

    def test_channel_divinity_spends_holy_power(self, cleric: Cleric, wounded_ally):
        for _ in range(CHANNEL_DIVINITY_COST):
            cleric.heal_target(wounded_ally)
        cleric.channel_divinity()
        assert cleric.holy_power.current == 0

    def test_channel_divinity_fails_insufficient_power(self, cleric: Cleric):
        result = cleric.channel_divinity()
        assert result is False
        assert cleric.is_channeling is False

    def test_channel_divinity_double_activate_fails(
        self, cleric: Cleric, wounded_ally,
    ):
        # Build 5 holy power, channel costs 3, leaves 2
        for _ in range(5):
            cleric.heal_target(wounded_ally)
        cleric.channel_divinity()
        result = cleric.channel_divinity()
        assert result is False

    def test_magical_attack_increases_when_channeling(
        self, cleric: Cleric, wounded_ally,
    ):
        base = cleric.magical_attack
        for _ in range(CHANNEL_DIVINITY_COST):
            cleric.heal_target(wounded_ally)
        cleric.channel_divinity()
        assert cleric.magical_attack == int(base * CHANNEL_ATK_MULTIPLIER)

    def test_magical_defense_increases_when_channeling(
        self, cleric: Cleric, wounded_ally,
    ):
        base = cleric.magical_defense
        for _ in range(CHANNEL_DIVINITY_COST):
            cleric.heal_target(wounded_ally)
        cleric.channel_divinity()
        assert cleric.magical_defense == int(base * CHANNEL_DEF_MULTIPLIER)

    def test_physical_attack_unchanged_when_channeling(
        self, cleric: Cleric, wounded_ally,
    ):
        base = cleric.physical_attack
        for _ in range(CHANNEL_DIVINITY_COST):
            cleric.heal_target(wounded_ally)
        cleric.channel_divinity()
        assert cleric.physical_attack == base

    def test_end_channel(self, cleric: Cleric, wounded_ally):
        for _ in range(CHANNEL_DIVINITY_COST):
            cleric.heal_target(wounded_ally)
        cleric.channel_divinity()
        cleric.end_channel()
        assert cleric.is_channeling is False

    def test_stats_normal_after_end_channel(self, cleric: Cleric, wounded_ally):
        base_atk = cleric.magical_attack
        for _ in range(CHANNEL_DIVINITY_COST):
            cleric.heal_target(wounded_ally)
        cleric.channel_divinity()
        cleric.end_channel()
        assert cleric.magical_attack == base_atk
