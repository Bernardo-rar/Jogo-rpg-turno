import pytest

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_modifiers import ClassModifiers
from src.core.characters.position import Position
from src.core.classes.ranger.ranger import Ranger

# Ranger stats: STR=8, DEX=12, CON=6, INT=5, WIS=10, CHA=4, MIND=7
# Modifiers from ranger.json: hit_dice=10, mod_hp_flat=0, mod_hp_mult=8,
#   mod_atk_physical=8, mod_atk_magical=8, mod_def_physical=3, mod_def_magical=3
# base physical_attack = (0 + 8 + 12) * 8 = 160 (weapon_die=0, STR=8, DEX=12)
# base physical_defense = (12 + 6 + 8) * 3 = 78
# base magical_attack = (0 + 10 + 5) * 8 = 120
# base magical_defense = (6 + 10 + 5) * 3 = 63

RANGER_MODIFIERS = ClassModifiers.from_json("data/classes/ranger.json")
EMPTY_THRESHOLDS = ThresholdCalculator({})
RANGER_CONFIG = CharacterConfig(
    class_modifiers=RANGER_MODIFIERS,
    threshold_calculator=EMPTY_THRESHOLDS,
)


def _ranger_attrs() -> Attributes:
    attrs = Attributes()
    attrs.set(AttributeType.STRENGTH, 8)
    attrs.set(AttributeType.DEXTERITY, 12)
    attrs.set(AttributeType.CONSTITUTION, 6)
    attrs.set(AttributeType.INTELLIGENCE, 5)
    attrs.set(AttributeType.WISDOM, 10)
    attrs.set(AttributeType.CHARISMA, 4)
    attrs.set(AttributeType.MIND, 7)
    return attrs


@pytest.fixture
def ranger() -> Ranger:
    return Ranger("Legolas", _ranger_attrs(), RANGER_CONFIG)


# --- LSP: Ranger e substituivel por Character ---

class TestRangerLSP:
    def test_is_character(self, ranger: Ranger):
        assert isinstance(ranger, Character)

    def test_has_name(self, ranger: Ranger):
        assert ranger.name == "Legolas"

    def test_is_alive(self, ranger: Ranger):
        assert ranger.is_alive

    def test_default_position_is_front(self, ranger: Ranger):
        assert ranger.position == Position.FRONT

    def test_take_damage(self, ranger: Ranger):
        initial_hp = ranger.current_hp
        actual = ranger.take_damage(10)
        assert actual == 10
        assert ranger.current_hp == initial_hp - 10

    def test_heal(self, ranger: Ranger):
        ranger.take_damage(20)
        healed = ranger.heal(10)
        # CON=6, heal(10) -> int(10 * 1.3) = 13
        assert healed == 13


# --- Stats basicos ---

class TestRangerStats:
    def test_max_hp(self, ranger: Ranger):
        # (hit_dice + CON + mod_hp_flat) * 2 * mod_hp_mult = (10 + 6 + 0) * 2 * 8 = 256
        assert ranger.max_hp == 256

    def test_base_physical_attack(self, ranger: Ranger):
        # (0 + STR + DEX) * mod = (0 + 8 + 12) * 8 = 160
        assert ranger.physical_attack == 160

    def test_base_magical_attack(self, ranger: Ranger):
        # (0 + WIS + INT) * mod = (0 + 10 + 5) * 8 = 120
        assert ranger.magical_attack == 120

    def test_base_physical_defense(self, ranger: Ranger):
        # (DEX + CON + STR) * mod = (12 + 6 + 8) * 3 = 78
        assert ranger.physical_defense == 78

    def test_base_magical_defense(self, ranger: Ranger):
        # (CON + WIS + INT) * mod = (6 + 10 + 5) * 3 = 63
        assert ranger.magical_defense == 63


# --- Predatory Focus integration ---

class TestRangerPredatoryFocus:
    def test_has_predatory_focus(self, ranger: Ranger):
        assert ranger.predatory_focus is not None
        assert ranger.predatory_focus.current == 0

    def test_predatory_focus_max_stacks(self, ranger: Ranger):
        assert ranger.predatory_focus.max_stacks == 20

    def test_register_hit_gains_stacks(self, ranger: Ranger):
        gained = ranger.register_hit()
        assert gained == 2
        assert ranger.predatory_focus.current == 2

    def test_register_miss_loses_stacks(self, ranger: Ranger):
        ranger.register_hit()  # +2
        ranger.register_hit()  # +2 = 4
        lost = ranger.register_miss()
        assert lost == 4  # stacks_per_hit * miss_loss_multiplier = 2 * 2.0 = 4
        assert ranger.predatory_focus.current == 0

    def test_register_miss_loss_clamped(self, ranger: Ranger):
        ranger.register_hit()  # +2
        lost = ranger.register_miss()
        assert lost == 2  # only had 2, can't lose 4
        assert ranger.predatory_focus.current == 0

    def test_decay_focus(self, ranger: Ranger):
        ranger.register_hit()
        ranger.register_hit()  # 4 stacks
        decayed = ranger.decay_focus()
        assert decayed == 1  # decay_per_turn = 1
        assert ranger.predatory_focus.current == 3

    def test_multiple_hits_accumulate(self, ranger: Ranger):
        for _ in range(5):
            ranger.register_hit()
        assert ranger.predatory_focus.current == 10


# --- Crit bonuses ---

class TestRangerCritBonus:
    def test_crit_chance_bonus_zero_at_start(self, ranger: Ranger):
        assert ranger.crit_chance_bonus == 0.0

    def test_crit_chance_bonus_scales_with_stacks(self, ranger: Ranger):
        for _ in range(5):
            ranger.register_hit()  # 10 stacks
        # 10 * 0.02 = 0.20
        assert ranger.crit_chance_bonus == pytest.approx(0.20)

    def test_crit_chance_bonus_at_max(self, ranger: Ranger):
        for _ in range(10):
            ranger.register_hit()  # 20 stacks
        # 20 * 0.02 = 0.40
        assert ranger.crit_chance_bonus == pytest.approx(0.40)

    def test_crit_damage_multiplier_at_start(self, ranger: Ranger):
        # Base multiplier = 1.0 (no bonus)
        assert ranger.crit_damage_multiplier == 1.0

    def test_crit_damage_multiplier_scales_with_stacks(self, ranger: Ranger):
        for _ in range(5):
            ranger.register_hit()  # 10 stacks
        # 1.0 + 10 * 0.05 = 1.50
        assert ranger.crit_damage_multiplier == pytest.approx(1.50)

    def test_crit_damage_multiplier_at_max(self, ranger: Ranger):
        for _ in range(10):
            ranger.register_hit()  # 20 stacks
        # 1.0 + 20 * 0.05 = 2.0
        assert ranger.crit_damage_multiplier == pytest.approx(2.0)


# --- Physical attack focus bonus ---

class TestRangerFocusAttackBonus:
    def test_physical_attack_with_focus_stacks(self, ranger: Ranger):
        base_atk = ranger.physical_attack
        for _ in range(10):
            ranger.register_hit()  # 20 stacks = max
        boosted_atk = ranger.physical_attack
        # 20 * 0.005 = 0.10 -> 10% bonus
        expected = int(base_atk * (1.0 + 20 * 0.005))
        assert boosted_atk == expected
        assert boosted_atk > base_atk

    def test_physical_attack_no_bonus_at_zero(self, ranger: Ranger):
        assert ranger.physical_attack == 160


# --- Hunter's Mark integration ---

class TestRangerHuntersMark:
    def test_has_hunters_mark(self, ranger: Ranger):
        assert ranger.hunters_mark is not None
        assert not ranger.hunters_mark.is_active

    def test_mark_target(self, ranger: Ranger):
        ranger.mark_target("Goblin")
        assert ranger.hunters_mark.is_active
        assert ranger.hunters_mark.target_name == "Goblin"

    def test_clear_mark(self, ranger: Ranger):
        ranger.mark_target("Goblin")
        ranger.clear_mark()
        assert not ranger.hunters_mark.is_active

    def test_get_armor_penetration_marked_target(self, ranger: Ranger):
        ranger.mark_target("Goblin")
        pen = ranger.get_armor_penetration("Goblin")
        assert pen == pytest.approx(0.20)

    def test_get_armor_penetration_unmarked_target(self, ranger: Ranger):
        ranger.mark_target("Goblin")
        pen = ranger.get_armor_penetration("Orc")
        assert pen == 0.0

    def test_get_armor_penetration_no_mark(self, ranger: Ranger):
        pen = ranger.get_armor_penetration("Goblin")
        assert pen == 0.0
