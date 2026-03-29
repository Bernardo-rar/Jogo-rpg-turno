"""Testes de gain_party_xp — party toda levela junto."""

from src.core.progression.level_up_system import LevelUpSystem
from src.core.progression.xp_table import XpTable
from tests.core.test_progression.conftest import EMPTY_THRESHOLDS, make_attrs
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_modifiers import ClassModifiers
from src.core.classes.fighter.fighter import Fighter
from src.core.classes.mage.mage import Mage

_TABLE = XpTable(thresholds=(0, 30, 80, 160, 280))
_FIGHTER_MODS = ClassModifiers.from_json("data/classes/fighter.json")
_MAGE_MODS = ClassModifiers.from_json("data/classes/mage.json")
from src.core.attributes.threshold_calculator import ThresholdCalculator

_CALC = ThresholdCalculator(EMPTY_THRESHOLDS)


def _make_fighter(name: str = "F") -> Fighter:
    config = CharacterConfig(class_modifiers=_FIGHTER_MODS, threshold_calculator=_CALC)
    return Fighter(name=name, attributes=make_attrs(con=6), config=config)


def _make_mage(name: str = "M") -> Mage:
    config = CharacterConfig(class_modifiers=_MAGE_MODS, threshold_calculator=_CALC)
    return Mage(name=name, attributes=make_attrs(con=6, intelligence=7, mind=5), config=config)


def _system() -> LevelUpSystem:
    return LevelUpSystem(_TABLE, {})


class TestGainPartyXp:

    def test_party_levels_together(self) -> None:
        party = [_make_fighter("F1"), _make_mage("M1")]
        system = _system()
        system.gain_party_xp(party, 30)
        assert party[0].level == 2
        assert party[1].level == 2

    def test_returns_level_up_result(self) -> None:
        party = [_make_fighter()]
        system = _system()
        result = system.gain_party_xp(party, 30)
        assert result is not None
        assert result.new_level == 2

    def test_no_level_up_returns_none(self) -> None:
        party = [_make_fighter()]
        system = _system()
        result = system.gain_party_xp(party, 10)
        assert result is None

    def test_zero_xp_returns_none(self) -> None:
        party = [_make_fighter()]
        system = _system()
        result = system.gain_party_xp(party, 0)
        assert result is None

    def test_multi_level_up(self) -> None:
        party = [_make_fighter()]
        system = _system()
        result = system.gain_party_xp(party, 160)
        assert result is not None
        assert result.new_level == 4

    def test_party_xp_accumulates(self) -> None:
        party = [_make_fighter()]
        system = _system()
        system.gain_party_xp(party, 20)
        system.gain_party_xp(party, 15)
        assert system.party_xp == 35
        assert party[0].level == 2  # 35 >= 30

    def test_four_members_all_same_level(self) -> None:
        party = [_make_fighter(f"F{i}") for i in range(4)]
        system = _system()
        system.gain_party_xp(party, 80)
        for char in party:
            assert char.level == 3
