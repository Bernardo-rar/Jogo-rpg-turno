import pytest

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_modifiers import ClassModifiers
from src.core.characters.position import Position
from src.core.classes.fighter.action_points import ActionPoints
from src.core.classes.fighter.fighter import Fighter
from src.core.classes.fighter.stance import Stance

# Fighter stats: STR=10, DEX=8, CON=5, WIS=4, INT=3, CHA=6, MIND=7
# Modifiers from fighter.json: hit_dice=12, mod_hp_mult=10, mod_atk_physical=10, etc.
# base physical_attack = (0+10+8)*10 = 180
# base physical_defense = (8+5+10)*5 = 115
# base magical_attack = (0+4+3)*6 = 42
# base magical_defense = (5+4+3)*3 = 36

FIGHTER_MODIFIERS = ClassModifiers.from_json("data/classes/fighter.json")
EMPTY_THRESHOLDS = ThresholdCalculator({})
FIGHTER_CONFIG = CharacterConfig(
    class_modifiers=FIGHTER_MODIFIERS,
    threshold_calculator=EMPTY_THRESHOLDS,
)


def _fighter_attrs() -> Attributes:
    attrs = Attributes()
    attrs.set(AttributeType.STRENGTH, 10)
    attrs.set(AttributeType.DEXTERITY, 8)
    attrs.set(AttributeType.CONSTITUTION, 5)
    attrs.set(AttributeType.INTELLIGENCE, 3)
    attrs.set(AttributeType.WISDOM, 4)
    attrs.set(AttributeType.CHARISMA, 6)
    attrs.set(AttributeType.MIND, 7)
    return attrs


@pytest.fixture
def fighter() -> Fighter:
    return Fighter(
        "Warrior",
        _fighter_attrs(),
        FIGHTER_CONFIG,
    )


class TestFighterIsCharacter:
    """LSP: Fighter deve funcionar como Character em qualquer contexto."""

    def test_is_instance_of_character(self, fighter: Fighter):
        assert isinstance(fighter, Character)

    def test_has_name(self, fighter: Fighter):
        assert fighter.name == "Warrior"

    def test_has_hp(self, fighter: Fighter):
        assert fighter.max_hp > 0

    def test_take_damage_works(self, fighter: Fighter):
        original = fighter.current_hp
        fighter.take_damage(10)
        assert fighter.current_hp == original - 10

    def test_heal_works(self, fighter: Fighter):
        fighter.take_damage(20)
        fighter.heal(10)
        # CON=5, heal(10) -> int(10 * 1.25) = 12
        assert fighter.current_hp == fighter.max_hp - 20 + 12

    def test_is_alive(self, fighter: Fighter):
        assert fighter.is_alive is True

    def test_speed(self, fighter: Fighter):
        assert fighter.speed == 8  # DEX


class TestFighterActionPoints:
    def test_has_action_points(self, fighter: Fighter):
        assert isinstance(fighter.action_points, ActionPoints)

    def test_action_points_start_at_zero(self, fighter: Fighter):
        assert fighter.action_points.current == 0

    def test_action_points_limit_by_level(self):
        config_lvl3 = CharacterConfig(
            class_modifiers=FIGHTER_MODIFIERS,
            threshold_calculator=EMPTY_THRESHOLDS,
            level=3,
        )
        f = Fighter("F", _fighter_attrs(), config_lvl3)
        assert f.action_points.limit == 6  # level 3 = limit 6


class TestFighterStance:
    def test_default_stance_is_normal(self, fighter: Fighter):
        assert fighter.stance == Stance.NORMAL

    def test_change_stance(self, fighter: Fighter):
        fighter.change_stance(Stance.OFFENSIVE)
        assert fighter.stance == Stance.OFFENSIVE

    def test_change_to_defensive(self, fighter: Fighter):
        fighter.change_stance(Stance.DEFENSIVE)
        assert fighter.stance == Stance.DEFENSIVE

    def test_change_back_to_normal(self, fighter: Fighter):
        fighter.change_stance(Stance.OFFENSIVE)
        fighter.change_stance(Stance.NORMAL)
        assert fighter.stance == Stance.NORMAL


class TestFighterStanceModifiesAttack:
    def test_normal_stance_no_attack_change(self, fighter: Fighter):
        assert fighter.physical_attack == 180

    def test_offensive_stance_increases_physical_attack(self, fighter: Fighter):
        fighter.change_stance(Stance.OFFENSIVE)
        # 180 * 1.2 = 216
        assert fighter.physical_attack == 216

    def test_defensive_stance_decreases_physical_attack(self, fighter: Fighter):
        fighter.change_stance(Stance.DEFENSIVE)
        # 180 * 0.8 = 144
        assert fighter.physical_attack == 144

    def test_offensive_stance_increases_magical_attack(self, fighter: Fighter):
        fighter.change_stance(Stance.OFFENSIVE)
        # 42 * 1.2 = 50.4 -> 50
        assert fighter.magical_attack == 50


class TestFighterStanceModifiesDefense:
    def test_normal_stance_no_defense_change(self, fighter: Fighter):
        assert fighter.physical_defense == 115

    def test_offensive_stance_decreases_physical_defense(self, fighter: Fighter):
        fighter.change_stance(Stance.OFFENSIVE)
        # 115 * 0.8 = 92
        assert fighter.physical_defense == 92

    def test_defensive_stance_increases_physical_defense(self, fighter: Fighter):
        fighter.change_stance(Stance.DEFENSIVE)
        # 115 * 1.2 = 138
        assert fighter.physical_defense == 138

    def test_defensive_stance_increases_magical_defense(self, fighter: Fighter):
        fighter.change_stance(Stance.DEFENSIVE)
        # 36 * 1.2 = 43.2 -> 43
        assert fighter.magical_defense == 43


class TestFighterPosition:
    def test_default_position_is_front(self, fighter: Fighter):
        assert fighter.position == Position.FRONT

    def test_can_change_position(self, fighter: Fighter):
        fighter.change_position(Position.BACK)
        assert fighter.position == Position.BACK
