"""Testes do sistema de subclasses."""

from src.core.progression.subclass_config import load_subclass_registry
from src.core.progression.subclass_applier import apply_subclass
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_modifiers import ClassModifiers
from src.core.classes.fighter.fighter import Fighter
from src.core.classes.mage.mage import Mage
from tests.core.test_progression.conftest import EMPTY_THRESHOLDS, make_attrs


_CALC = ThresholdCalculator(EMPTY_THRESHOLDS)
_FIGHTER_MODS = ClassModifiers.from_json("data/classes/fighter.json")
_MAGE_MODS = ClassModifiers.from_json("data/classes/mage.json")


class TestSubclassRegistry:

    def test_loads_all_13_classes(self) -> None:
        registry = load_subclass_registry()
        assert len(registry) == 13

    def test_each_class_has_two_options(self) -> None:
        registry = load_subclass_registry()
        for class_id, subs in registry.items():
            assert subs.option_a.subclass_id != ""
            assert subs.option_b.subclass_id != ""

    def test_fighter_champion_has_skills(self) -> None:
        registry = load_subclass_registry()
        champion = registry["fighter"].option_a
        assert len(champion.skill_ids) >= 2

    def test_all_options_have_passive_bonus(self) -> None:
        registry = load_subclass_registry()
        for class_id, subs in registry.items():
            assert len(subs.option_a.passive_bonuses) >= 1, f"{class_id} A"
            assert len(subs.option_b.passive_bonuses) >= 1, f"{class_id} B"


class TestApplySubclass:

    def test_champion_boosts_physical_attack(self) -> None:
        config = CharacterConfig(
            class_modifiers=_FIGHTER_MODS, threshold_calculator=_CALC,
        )
        fighter = Fighter("Test", make_attrs(con=6), config)
        atk_before = fighter.physical_attack
        registry = load_subclass_registry()
        apply_subclass(fighter, registry["fighter"].option_a)
        assert fighter.physical_attack > atk_before

    def test_evoker_boosts_magical_attack(self) -> None:
        config = CharacterConfig(
            class_modifiers=_MAGE_MODS, threshold_calculator=_CALC,
        )
        mage = Mage("Test", make_attrs(con=6, intelligence=8, mind=5), config)
        matk_before = mage.magical_attack
        registry = load_subclass_registry()
        apply_subclass(mage, registry["mage"].option_a)
        assert mage.magical_attack > matk_before

    def test_armorer_boosts_defense_and_hp(self) -> None:
        config = CharacterConfig(
            class_modifiers=_FIGHTER_MODS, threshold_calculator=_CALC,
        )
        fighter = Fighter("Test", make_attrs(con=6), config)
        hp_before = fighter.max_hp
        pdef_before = fighter.physical_defense
        registry = load_subclass_registry()
        apply_subclass(fighter, registry["artificer"].option_b)
        assert fighter.max_hp > hp_before
        assert fighter.physical_defense > pdef_before
