"""Testes do sistema de talentos."""

from random import Random

from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_modifiers import ClassModifiers
from src.core.classes.fighter.fighter import Fighter
from src.core.classes.mage.mage import Mage
from src.core.progression.talent_applier import apply_talent
from src.core.progression.talent_config import TALENT_LEVELS, Talent, load_talents
from src.core.progression.talent_picker import generate_talent_offering
from tests.core.test_progression.conftest import EMPTY_THRESHOLDS, make_attrs

_CALC = ThresholdCalculator(EMPTY_THRESHOLDS)
_FIGHTER_MODS = ClassModifiers.from_json("data/classes/fighter.json")
_MAGE_MODS = ClassModifiers.from_json("data/classes/mage.json")


class TestLoadTalents:

    def test_loads_25_talents(self) -> None:
        talents = load_talents()
        assert len(talents) == 25

    def test_all_have_description(self) -> None:
        for t in load_talents().values():
            assert t.description != ""

    def test_categories_present(self) -> None:
        cats = {t.category for t in load_talents().values()}
        assert "OFFENSIVE" in cats
        assert "DEFENSIVE" in cats
        assert "UTILITY" in cats


class TestTalentPicker:

    def test_generates_3_options(self) -> None:
        talents = load_talents()
        options = generate_talent_offering("fighter", talents, set(), Random(42))
        assert len(options) == 3

    def test_diverse_categories(self) -> None:
        talents = load_talents()
        options = generate_talent_offering("fighter", talents, set(), Random(42))
        cats = {o.category for o in options}
        assert len(cats) >= 2

    def test_excludes_chosen(self) -> None:
        talents = load_talents()
        first = generate_talent_offering("fighter", talents, set(), Random(42))
        chosen = {first[0].talent_id}
        second = generate_talent_offering("fighter", talents, chosen, Random(42))
        second_ids = {o.talent_id for o in second}
        assert first[0].talent_id not in second_ids

    def test_class_restricted_talent_eligible(self) -> None:
        talents = load_talents()
        bv = talents["berserker_vitality"]
        assert bv.is_available_for("barbarian")

    def test_restricted_talent_not_for_wrong_class(self) -> None:
        talents = load_talents()
        for _ in range(20):
            options = generate_talent_offering("mage", talents, set(), Random(_))
            ids = {o.talent_id for o in options}
            assert "berserker_vitality" not in ids


class TestApplyTalent:

    def test_brutal_strikes_boosts_attack(self) -> None:
        config = CharacterConfig(
            class_modifiers=_FIGHTER_MODS, threshold_calculator=_CALC,
        )
        fighter = Fighter("F", make_attrs(con=6), config)
        atk_before = fighter.physical_attack
        talents = load_talents()
        apply_talent(fighter, talents["brutal_strikes"])
        assert fighter.physical_attack > atk_before

    def test_thick_skin_boosts_hp(self) -> None:
        config = CharacterConfig(
            class_modifiers=_FIGHTER_MODS, threshold_calculator=_CALC,
        )
        fighter = Fighter("F", make_attrs(con=6), config)
        hp_before = fighter.max_hp
        talents = load_talents()
        apply_talent(fighter, talents["thick_skin"])
        assert fighter.max_hp > hp_before


class TestTalentLevels:

    def test_talent_levels_are_5_7_9(self) -> None:
        assert TALENT_LEVELS == frozenset({5, 7, 9})
