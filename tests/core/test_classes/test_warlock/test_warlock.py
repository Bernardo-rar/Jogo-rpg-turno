import pytest

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_modifiers import ClassModifiers
from src.core.characters.position import Position
from src.core.classes.warlock.familiar import FamiliarType, load_familiar_configs
from src.core.classes.warlock.warlock import Warlock
from src.core.classes.warlock.warlock_config import load_warlock_config

_CONFIG = load_warlock_config()
_FAMILIARS = load_familiar_configs()

WARLOCK_MODS = ClassModifiers(
    hit_dice=8,
    vida_mod=0,
    mod_hp=6,
    mana_multiplier=8,
    mod_atk_physical=4,
    mod_atk_magical=9,
    mod_def_physical=3,
    mod_def_magical=4,
    regen_hp_mod=2,
    regen_mana_mod=4,
)

EMPTY_THRESHOLDS = ThresholdCalculator({})
WARLOCK_CONFIG = CharacterConfig(
    class_modifiers=WARLOCK_MODS,
    threshold_calculator=EMPTY_THRESHOLDS,
    position=Position.BACK,
)


@pytest.fixture
def warlock_attrs() -> Attributes:
    return Attributes({
        AttributeType.STRENGTH: 4,
        AttributeType.DEXTERITY: 5,
        AttributeType.CONSTITUTION: 6,
        AttributeType.INTELLIGENCE: 8,
        AttributeType.WISDOM: 7,
        AttributeType.CHARISMA: 9,
        AttributeType.MIND: 8,
    })


@pytest.fixture
def warlock(warlock_attrs) -> Warlock:
    return Warlock(
        name="Malachar",
        attributes=warlock_attrs,
        config=WARLOCK_CONFIG,
    )


# --- LSP ---


class TestWarlockIsCharacter:
    def test_is_instance_of_character(self, warlock: Warlock):
        assert isinstance(warlock, Character)

    def test_has_name(self, warlock: Warlock):
        assert warlock.name == "Malachar"

    def test_has_hp(self, warlock: Warlock):
        assert warlock.current_hp == warlock.max_hp

    def test_take_damage_works(self, warlock: Warlock):
        warlock.take_damage(10)
        assert warlock.current_hp == warlock.max_hp - 10

    def test_heal_works(self, warlock: Warlock):
        warlock.take_damage(50)
        warlock.heal(20)
        # CON=6, heal(20) -> int(20 * 1.3) = 26
        assert warlock.current_hp == warlock.max_hp - 50 + 26

    def test_is_alive(self, warlock: Warlock):
        assert warlock.is_alive is True

    def test_speed(self, warlock: Warlock):
        # Speed = DEX = 5 (no familiar bonus for IMP)
        assert warlock.speed == 5


# --- Stats ---


class TestWarlockStats:
    def test_max_hp(self, warlock: Warlock):
        # ((8 + 6 + 0) * 2) * 6 = 168
        assert warlock.max_hp == 168

    def test_max_mana(self, warlock: Warlock):
        # 8 * 8 * 5 = 320
        assert warlock.max_mana == 320

    def test_physical_attack(self, warlock: Warlock):
        # (0 + 4 + 5) * 4 = 36
        assert warlock.physical_attack == 36

    def test_magical_attack_base_with_imp(self, warlock: Warlock):
        # base = (0 + 7 + 8) * 9 = 135
        # IMP bonus = 135 * 1.10 = 148 (int)
        assert warlock.magical_attack == int(135 * 1.10)

    def test_physical_defense(self, warlock: Warlock):
        # (5 + 6 + 4) * 3 = 45
        assert warlock.physical_defense == 45

    def test_magical_defense_base(self, warlock: Warlock):
        # (6 + 7 + 8) * 4 = 84
        # No insanity, no familiar bonus for mag_def with IMP
        assert warlock.magical_defense == 84


class TestWarlockPosition:
    def test_default_position_is_back(self, warlock: Warlock):
        assert warlock.position == Position.BACK


# --- Insanity ---


class TestWarlockInsanity:
    def test_has_insanity_bar(self, warlock: Warlock):
        assert warlock.insanity is not None

    def test_insanity_starts_empty(self, warlock: Warlock):
        assert warlock.insanity.current == 0

    def test_take_damage_gains_insanity(self, warlock: Warlock):
        warlock.take_damage(100)
        # 100 * 0.05 = 5 insanity
        assert warlock.insanity.current == 5

    def test_generate_insanity_from_cast(self, warlock: Warlock):
        warlock.generate_insanity_from_cast()
        assert warlock.insanity.current == 10

    def test_decay_insanity(self, warlock: Warlock):
        warlock.insanity.gain(50)
        warlock.decay_insanity()
        assert warlock.insanity.current == 47

    def test_magical_attack_increases_with_insanity(self, warlock: Warlock):
        base = warlock.magical_attack
        warlock.insanity.gain(100)  # max insanity
        boosted = warlock.magical_attack
        # At max: base * 1.40 * 1.0 (no thirst) * 1.10 (IMP)
        assert boosted > base

    def test_magical_defense_decreases_with_insanity(self, warlock: Warlock):
        base = warlock.magical_defense
        warlock.insanity.gain(100)  # max insanity
        penalized = warlock.magical_defense
        # At max: base * 0.75
        assert penalized < base

    def test_insanity_atk_at_max(self, warlock: Warlock):
        warlock.insanity.gain(100)
        # base=135, insanity=1.40, thirst=1.0, imp=1.10
        expected = int(135 * 1.40 * 1.0 * 1.10)
        assert warlock.magical_attack == expected

    def test_insanity_def_at_max(self, warlock: Warlock):
        warlock.insanity.gain(100)
        # base=84, penalty=0.75, no familiar for mag_def (IMP)
        expected = int(84 * 0.75 * 1.0)
        assert warlock.magical_defense == expected


# --- Insatiable Thirst ---


class TestWarlockThirst:
    def test_has_thirst(self, warlock: Warlock):
        assert warlock.thirst is not None

    def test_thirst_starts_inactive(self, warlock: Warlock):
        assert warlock.thirst.is_active is False

    def test_check_thirst_no_stack_when_healthy(self, warlock: Warlock):
        warlock.check_thirst()
        assert warlock.thirst.stacks == 0

    def test_check_thirst_gains_stack_when_low(self, warlock: Warlock):
        warlock.take_damage(warlock.max_hp // 2 + 1)
        warlock.check_thirst()
        assert warlock.thirst.stacks == 1

    def test_check_thirst_triggers_at_5_stacks(self, warlock: Warlock):
        warlock.take_damage(warlock.max_hp // 2 + 1)
        for _ in range(4):
            warlock.check_thirst()
        result = warlock.check_thirst()
        assert result is True
        assert warlock.thirst.is_active is True

    def test_thirst_duration_equals_con(self, warlock: Warlock):
        warlock.take_damage(warlock.max_hp // 2 + 1)
        for _ in range(5):
            warlock.check_thirst()
        # CON = 6
        assert warlock.thirst.remaining_turns == 6

    def test_thirst_boosts_magical_attack(self, warlock: Warlock):
        base = warlock.magical_attack
        warlock.take_damage(warlock.max_hp // 2 + 1)
        for _ in range(5):
            warlock.check_thirst()
        assert warlock.magical_attack > base

    def test_thirst_boosts_hp_regen(self, warlock: Warlock):
        base = warlock.hp_regen
        warlock.take_damage(warlock.max_hp // 2 + 1)
        for _ in range(5):
            warlock.check_thirst()
        assert warlock.hp_regen > base

    def test_thirst_boosts_physical_defense(self, warlock: Warlock):
        base = warlock.physical_defense
        warlock.take_damage(warlock.max_hp // 2 + 1)
        for _ in range(5):
            warlock.check_thirst()
        assert warlock.physical_defense > base

    def test_tick_thirst_decrements(self, warlock: Warlock):
        warlock.take_damage(warlock.max_hp // 2 + 1)
        for _ in range(5):
            warlock.check_thirst()
        warlock.tick_thirst()
        assert warlock.thirst.remaining_turns == 5

    def test_thirst_deactivates_after_duration(self, warlock: Warlock):
        warlock.take_damage(warlock.max_hp // 2 + 1)
        for _ in range(5):
            warlock.check_thirst()
        for _ in range(6):  # CON = 6
            warlock.tick_thirst()
        assert warlock.thirst.is_active is False


# --- Familiar ---


class TestWarlockFamiliar:
    def test_default_familiar_is_imp(self, warlock: Warlock):
        assert warlock.familiar == FamiliarType.IMP

    def test_set_familiar(self, warlock: Warlock):
        warlock.set_familiar(FamiliarType.RAVEN)
        assert warlock.familiar == FamiliarType.RAVEN

    def test_raven_boosts_speed(self, warlock_attrs):
        w = Warlock(
            name="Test",
            attributes=warlock_attrs,
            config=WARLOCK_CONFIG,
            familiar=FamiliarType.RAVEN,
        )
        # Speed = DEX = 5, RAVEN +15% = 5 * 1.15 = 5 (int)
        assert w.speed == int(5 * 1.15)

    def test_shadow_cat_boosts_mag_def(self, warlock_attrs):
        w = Warlock(
            name="Test",
            attributes=warlock_attrs,
            config=WARLOCK_CONFIG,
            familiar=FamiliarType.SHADOW_CAT,
        )
        # base mag_def = 84, +10% = 92
        assert w.magical_defense == int(84 * 1.10)

    def test_imp_does_not_boost_speed(self, warlock: Warlock):
        assert warlock.speed == 5  # DEX raw, no bonus

    def test_custom_familiar_in_constructor(self, warlock_attrs):
        w = Warlock(
            name="Test",
            attributes=warlock_attrs,
            config=WARLOCK_CONFIG,
            familiar=FamiliarType.SPIDER,
        )
        assert w.familiar == FamiliarType.SPIDER


# --- Life Drain ---


class TestWarlockLifeDrain:
    def test_on_inflict_bleed_heals(self, warlock: Warlock):
        warlock.take_damage(50)
        before = warlock.current_hp
        warlock.on_inflict_bleed(100)
        # 100 * 0.15 = 15 -> heal(15) with CON=6 -> int(15 * 1.3) = 19
        assert warlock.current_hp == before + 19

    def test_on_inflict_bleed_returns_healed(self, warlock: Warlock):
        warlock.take_damage(50)
        healed = warlock.on_inflict_bleed(100)
        # 100 * 0.15 = 15 -> heal(15) with CON=6 -> int(15 * 1.3) = 19
        assert healed == 19

    def test_on_inflict_bleed_capped_at_max_hp(self, warlock: Warlock):
        healed = warlock.on_inflict_bleed(100)
        assert healed == 0  # already at max HP


# --- Spell Ramping ---


class TestWarlockSpellRamping:
    def test_no_ramp_by_default(self, warlock: Warlock):
        assert warlock.spell_damage_bonus == 0.0

    def test_register_cast_activates_ramp(self, warlock: Warlock):
        warlock.register_cast()
        assert warlock.spell_damage_bonus > 0.0

    def test_register_cast_also_generates_insanity(self, warlock: Warlock):
        warlock.register_cast()
        assert warlock.insanity.current == 10

    def test_spell_ramp_scales_with_cha(self, warlock: Warlock):
        warlock.register_cast()
        # 0.15 + (9 * 0.005) = 0.15 + 0.045 = 0.195
        assert warlock.spell_damage_bonus == pytest.approx(0.195)

    def test_consume_spell_ramp_returns_bonus(self, warlock: Warlock):
        warlock.register_cast()
        bonus = warlock.consume_spell_ramp()
        assert bonus == pytest.approx(0.195)

    def test_consume_spell_ramp_resets(self, warlock: Warlock):
        warlock.register_cast()
        warlock.consume_spell_ramp()
        assert warlock.spell_damage_bonus == 0.0
