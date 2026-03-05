import pytest

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_modifiers import ClassModifiers
from src.core.characters.position import Position
from src.core.classes.monk.equilibrium_bar import EquilibriumState
from src.core.classes.monk.monk import Monk

# Monk stats: STR=10, DEX=10, CON=8, INT=5, WIS=10, CHA=4, MIND=6
# Modifiers from monk.json: hit_dice=10, vida_mod=0, mod_hp=8,
#   mod_atk_physical=6, mod_atk_magical=5, mod_def_physical=4, mod_def_magical=4
# base HP = (10 + 8 + 0) * 2 * 8 = 288
# base physical_attack = (0 + 10 + 10) * 6 = 120
# base magical_attack = (0 + 10 + 5) * 5 = 75
# base physical_defense = (10 + 8 + 10) * 4 = 112
# base magical_defense = (8 + 10 + 5) * 4 = 92

MONK_MODIFIERS = ClassModifiers.from_json("data/classes/monk.json")
EMPTY_THRESHOLDS = ThresholdCalculator({})
MONK_CONFIG = CharacterConfig(
    class_modifiers=MONK_MODIFIERS,
    threshold_calculator=EMPTY_THRESHOLDS,
)


def _monk_attrs() -> Attributes:
    attrs = Attributes()
    attrs.set(AttributeType.STRENGTH, 10)
    attrs.set(AttributeType.DEXTERITY, 10)
    attrs.set(AttributeType.CONSTITUTION, 8)
    attrs.set(AttributeType.INTELLIGENCE, 5)
    attrs.set(AttributeType.WISDOM, 10)
    attrs.set(AttributeType.CHARISMA, 4)
    attrs.set(AttributeType.MIND, 6)
    return attrs


@pytest.fixture
def monk() -> Monk:
    return Monk("Lee", _monk_attrs(), MONK_CONFIG)


# --- LSP: Monk e substituivel por Character ---


class TestMonkLSP:
    def test_is_character(self, monk: Monk):
        assert isinstance(monk, Character)

    def test_has_name(self, monk: Monk):
        assert monk.name == "Lee"

    def test_is_alive(self, monk: Monk):
        assert monk.is_alive

    def test_default_position_is_front(self, monk: Monk):
        assert monk.position == Position.FRONT

    def test_take_damage(self, monk: Monk):
        initial_hp = monk.current_hp
        actual = monk.take_damage(10)
        assert actual == 10
        assert monk.current_hp == initial_hp - 10

    def test_heal(self, monk: Monk):
        monk.take_damage(20)
        healed = monk.heal(10)
        assert healed == 10


# --- Stats basicos ---


class TestMonkStats:
    def test_max_hp(self, monk: Monk):
        # (10 + 8 + 0) * 2 * 8 = 288
        assert monk.max_hp == 288

    def test_base_physical_attack(self, monk: Monk):
        # (0 + 10 + 10) * 6 = 120, +8% balanced bonus = 129
        assert monk.physical_attack == int(120 * 1.08)

    def test_base_magical_attack(self, monk: Monk):
        # (0 + 10 + 5) * 5 = 75
        assert monk.magical_attack == 75

    def test_base_physical_defense(self, monk: Monk):
        # (10 + 8 + 10) * 4 = 112, +8% balanced bonus = 120
        assert monk.physical_defense == int(112 * 1.08)

    def test_base_magical_defense(self, monk: Monk):
        # (8 + 10 + 5) * 4 = 92
        assert monk.magical_defense == 92


# --- Equilibrium integration ---


class TestMonkEquilibrium:
    def test_has_equilibrium(self, monk: Monk):
        assert monk.equilibrium is not None

    def test_starts_in_balanced(self, monk: Monk):
        assert monk.equilibrium.state == EquilibriumState.BALANCED

    def test_attack_action_shifts_to_destruction(self, monk: Monk):
        shifted = monk.attack_action()
        assert shifted == 10
        assert monk.equilibrium.value == 60

    def test_defensive_action_shifts_to_vitality(self, monk: Monk):
        shifted = monk.defensive_action()
        assert shifted == 10
        assert monk.equilibrium.value == 40

    def test_end_of_turn_decay(self, monk: Monk):
        monk.attack_action()  # value=60
        decayed = monk.end_of_turn_decay()
        assert decayed == 5
        assert monk.equilibrium.value == 55

    def test_multiple_attacks_push_to_destruction(self, monk: Monk):
        for _ in range(3):
            monk.attack_action()
        # 50 + 30 = 80
        assert monk.equilibrium.state == EquilibriumState.DESTRUCTION

    def test_multiple_defends_push_to_vitality(self, monk: Monk):
        for _ in range(3):
            monk.defensive_action()
        # 50 - 30 = 20
        assert monk.equilibrium.state == EquilibriumState.VITALITY


# --- Physical attack bonus por zona ---


class TestMonkAttackBonus:
    def test_no_bonus_at_balanced_start(self, monk: Monk):
        # Balanced zone: +8% atk bonus
        base = 120
        expected = int(base * (1.0 + 0.08))
        assert monk.physical_attack == expected

    def test_destruction_zone_atk_bonus(self, monk: Monk):
        # Push deep into destruction: 3 attacks -> value=80
        for _ in range(3):
            monk.attack_action()
        # destruction_intensity = (80 - 67) / (100 - 67) = 13/33
        intensity = 13 / 33
        base = 120
        expected = int(base * (1.0 + intensity * 0.25))
        assert monk.physical_attack == expected

    def test_vitality_zone_no_atk_bonus(self, monk: Monk):
        # Push into vitality: 3 defends -> value=20
        for _ in range(3):
            monk.defensive_action()
        # vitality zone: no atk bonus, only defense
        assert monk.physical_attack == 120

    def test_max_destruction_atk_bonus(self, monk: Monk):
        for _ in range(5):
            monk.attack_action()  # 50 + 50 = 100 (capped)
        # destruction_intensity = 1.0, bonus = 25%
        base = 120
        expected = int(base * 1.25)
        assert monk.physical_attack == expected


# --- Physical defense bonus por zona ---


class TestMonkDefenseBonus:
    def test_balanced_zone_def_bonus(self, monk: Monk):
        # Balanced: +8% def
        base = 112
        expected = int(base * (1.0 + 0.08))
        assert monk.physical_defense == expected

    def test_vitality_zone_def_bonus(self, monk: Monk):
        # Push into vitality: 3 defends -> value=20
        for _ in range(3):
            monk.defensive_action()
        # vitality_intensity = (33 - 20) / 33 = 13/33
        intensity = 13 / 33
        base = 112
        expected = int(base * (1.0 + intensity * 0.20))
        assert monk.physical_defense == expected

    def test_destruction_zone_no_def_bonus(self, monk: Monk):
        # Push into destruction
        for _ in range(3):
            monk.attack_action()
        # destruction zone: no def bonus
        assert monk.physical_defense == 112

    def test_max_vitality_def_bonus(self, monk: Monk):
        for _ in range(5):
            monk.defensive_action()  # 50 - 50 = 0 (capped)
        # vitality_intensity = 1.0, bonus = 20%
        base = 112
        expected = int(base * 1.20)
        assert monk.physical_defense == expected


# --- Multi-hit ---


class TestMonkMultiHit:
    def test_base_hit_count(self, monk: Monk):
        assert monk.hit_count == 2

    def test_hit_count_in_destruction(self, monk: Monk):
        for _ in range(3):
            monk.attack_action()  # push to destruction
        assert monk.hit_count == 3

    def test_hit_count_in_vitality(self, monk: Monk):
        for _ in range(3):
            monk.defensive_action()
        assert monk.hit_count == 2

    def test_hit_count_in_balanced(self, monk: Monk):
        assert monk.hit_count == 2


# --- Crit bonus ---


class TestMonkCritBonus:
    def test_crit_chance_zero_in_balanced(self, monk: Monk):
        assert monk.crit_chance_bonus == 0.0

    def test_crit_chance_scales_in_destruction(self, monk: Monk):
        for _ in range(3):
            monk.attack_action()  # value=80
        # intensity = 13/33, crit bonus = 13/33 * 0.15
        expected = (13 / 33) * 0.15
        assert monk.crit_chance_bonus == pytest.approx(expected)

    def test_crit_chance_max_in_full_destruction(self, monk: Monk):
        for _ in range(5):
            monk.attack_action()
        assert monk.crit_chance_bonus == pytest.approx(0.15)

    def test_crit_chance_zero_in_vitality(self, monk: Monk):
        for _ in range(3):
            monk.defensive_action()
        assert monk.crit_chance_bonus == 0.0


# --- Debuff chance ---


class TestMonkDebuffChance:
    def test_debuff_chance_zero_in_balanced(self, monk: Monk):
        assert monk.debuff_chance_bonus == 0.0

    def test_debuff_chance_scales_in_destruction(self, monk: Monk):
        for _ in range(3):
            monk.attack_action()  # value=80
        expected = (13 / 33) * 0.30
        assert monk.debuff_chance_bonus == pytest.approx(expected)

    def test_debuff_chance_max_in_full_destruction(self, monk: Monk):
        for _ in range(5):
            monk.attack_action()
        assert monk.debuff_chance_bonus == pytest.approx(0.30)

    def test_debuff_chance_zero_in_vitality(self, monk: Monk):
        for _ in range(3):
            monk.defensive_action()
        assert monk.debuff_chance_bonus == 0.0
