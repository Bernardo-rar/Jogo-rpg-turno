"""Testes de integracao: level up de Fighter, Mage e Cleric."""

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_modifiers import ClassModifiers
from src.core.classes.cleric.cleric import Cleric
from src.core.classes.cleric.divinity import Divinity
from src.core.classes.fighter.fighter import Fighter
from src.core.classes.mage.mage import Mage
from src.core.progression.attribute_point_config import load_attribute_points
from src.core.progression.level_up_system import LevelUpSystem
from src.core.progression.xp_table import load_xp_table
from tests.core.test_progression.conftest import EMPTY_THRESHOLDS, make_attrs

FIGHTER_MODS = ClassModifiers.from_json("data/classes/fighter.json")
MAGE_MODS = ClassModifiers.from_json("data/classes/mage.json")
CLERIC_MODS = ClassModifiers.from_json("data/classes/cleric.json")


def _make_system() -> LevelUpSystem:
    return LevelUpSystem(load_xp_table(), load_attribute_points())


class TestFighterLevelUpIntegration:
    """Fighter level 1 -> 5: HP cresce, AP limit cresce, regen cresce."""

    def test_fighter_hp_grows_with_level(self) -> None:
        calc = ThresholdCalculator(EMPTY_THRESHOLDS)
        config = CharacterConfig(class_modifiers=FIGHTER_MODS, threshold_calculator=calc)
        fighter = Fighter(name="Roland", attributes=make_attrs(con=6, intelligence=7, mind=5), config=config)
        system = _make_system()
        hp_at_1 = fighter.max_hp
        system.gain_xp(fighter, 280)  # level 5
        assert fighter.level == 5
        assert fighter.max_hp > hp_at_1

    def test_fighter_ap_limit_at_level_5(self) -> None:
        calc = ThresholdCalculator(EMPTY_THRESHOLDS)
        config = CharacterConfig(class_modifiers=FIGHTER_MODS, threshold_calculator=calc)
        fighter = Fighter(name="Roland", attributes=make_attrs(con=6, intelligence=7, mind=5), config=config)
        system = _make_system()
        system.gain_xp(fighter, 280)
        assert fighter.action_points.limit == 10

    def test_fighter_proficiency_bonus_equals_level(self) -> None:
        calc = ThresholdCalculator(EMPTY_THRESHOLDS)
        config = CharacterConfig(class_modifiers=FIGHTER_MODS, threshold_calculator=calc)
        fighter = Fighter(name="Roland", attributes=make_attrs(con=6, intelligence=7, mind=5), config=config)
        system = _make_system()
        system.gain_xp(fighter, 80)  # level 3
        assert fighter.proficiency_bonus == 3

    def test_fighter_regen_grows_with_level(self) -> None:
        calc = ThresholdCalculator(EMPTY_THRESHOLDS)
        config = CharacterConfig(class_modifiers=FIGHTER_MODS, threshold_calculator=calc)
        fighter = Fighter(name="Roland", attributes=make_attrs(con=6, intelligence=7, mind=5), config=config)
        system = _make_system()
        regen_at_1 = fighter.hp_regen
        system.gain_xp(fighter, 30)  # level 2
        assert fighter.hp_regen > regen_at_1


class TestMageLevelUpIntegration:
    """Mage level up: HP e regen crescem, stats escalam."""

    def test_mage_hp_grows_with_level(self) -> None:
        calc = ThresholdCalculator(EMPTY_THRESHOLDS)
        config = CharacterConfig(class_modifiers=MAGE_MODS, threshold_calculator=calc)
        mage = Mage(name="Archmage", attributes=make_attrs(con=6, intelligence=7, mind=5), config=config)
        system = _make_system()
        hp_at_1 = mage.max_hp
        system.gain_xp(mage, 160)  # level 4
        assert mage.level == 4
        assert mage.max_hp > hp_at_1

    def test_mage_proficiency_at_level_10(self) -> None:
        calc = ThresholdCalculator(EMPTY_THRESHOLDS)
        config = CharacterConfig(class_modifiers=MAGE_MODS, threshold_calculator=calc)
        mage = Mage(name="Archmage", attributes=make_attrs(con=6, intelligence=7, mind=5), config=config)
        system = _make_system()
        system.gain_xp(mage, 9999)
        assert mage.level == 10
        assert mage.proficiency_bonus == 10


class TestClericLevelUpIntegration:
    """Cleric level up: HP e regen crescem."""

    def test_cleric_hp_grows_with_level(self) -> None:
        calc = ThresholdCalculator(EMPTY_THRESHOLDS)
        config = CharacterConfig(class_modifiers=CLERIC_MODS, threshold_calculator=calc)
        cleric = Cleric(
            name="Priestess", attributes=make_attrs(con=6, intelligence=7, mind=5), config=config,
            divinity=Divinity.HOLY,
        )
        system = _make_system()
        hp_at_1 = cleric.max_hp
        system.gain_xp(cleric, 80)  # level 3
        assert cleric.level == 3
        assert cleric.max_hp > hp_at_1


class TestDistributePointsIntegration:
    """Distribuir pontos apos level up e verificar stats."""

    def test_str_increase_changes_physical_attack(self) -> None:
        calc = ThresholdCalculator(EMPTY_THRESHOLDS)
        config = CharacterConfig(class_modifiers=FIGHTER_MODS, threshold_calculator=calc)
        fighter = Fighter(name="Roland", attributes=make_attrs(con=6, intelligence=7, mind=5), config=config)
        system = _make_system()
        system.gain_xp(fighter, 30)  # level 2
        atk_before = fighter.physical_attack
        system.distribute_physical_points(
            fighter, {AttributeType.STRENGTH: 2},
        )
        assert fighter.physical_attack > atk_before

    def test_con_increase_changes_max_hp(self) -> None:
        calc = ThresholdCalculator(EMPTY_THRESHOLDS)
        config = CharacterConfig(class_modifiers=FIGHTER_MODS, threshold_calculator=calc)
        fighter = Fighter(name="Roland", attributes=make_attrs(con=6, intelligence=7, mind=5), config=config)
        system = _make_system()
        hp_before = fighter.max_hp
        system.distribute_physical_points(
            fighter, {AttributeType.CONSTITUTION: 2},
        )
        assert fighter.max_hp > hp_before

    def test_mind_increase_changes_mana_regen(self) -> None:
        calc = ThresholdCalculator(EMPTY_THRESHOLDS)
        config = CharacterConfig(class_modifiers=MAGE_MODS, threshold_calculator=calc)
        mage = Mage(name="Archmage", attributes=make_attrs(con=6, intelligence=7, mind=5), config=config)
        system = _make_system()
        regen_before = mage.mana_regen
        system.distribute_mental_points(
            mage, {AttributeType.MIND: 1},
        )
        assert mage.mana_regen > regen_before
