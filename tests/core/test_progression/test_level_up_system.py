"""Testes para LevelUpSystem: orquestrador de level up."""

import pytest

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.progression.attribute_point_config import (
    LevelAttributePoints,
    load_attribute_points,
)
from src.core.progression.level_up_system import LevelUpSystem
from src.core.progression.xp_table import XpTable, load_xp_table
from tests.core.test_progression.conftest import (
    EMPTY_THRESHOLDS,
    SIMPLE_MODS,
    make_attrs,
)

SMALL_TABLE = XpTable(thresholds=(0, 100, 300, 600))

SMALL_ATTR_CONFIG = {
    2: LevelAttributePoints(physical=2, mental=1),
    3: LevelAttributePoints(physical=0, mental=0),
    4: LevelAttributePoints(physical=3, mental=2),
}


def _make_char(name: str = "Test") -> Character:
    calc = ThresholdCalculator(EMPTY_THRESHOLDS)
    config = CharacterConfig(class_modifiers=SIMPLE_MODS, threshold_calculator=calc)
    return Character(name=name, attributes=make_attrs(), config=config)


class TestGainXp:
    """Testes de ganho de XP e level up."""

    @pytest.fixture()
    def system(self) -> LevelUpSystem:
        return LevelUpSystem(SMALL_TABLE, SMALL_ATTR_CONFIG)

    def test_gain_xp_no_level_up(self, system: LevelUpSystem) -> None:
        char = _make_char()
        result = system.gain_xp(char, 50)
        assert result is None
        assert char.level == 1
        assert system.get_xp(char) == 50

    def test_gain_xp_triggers_level_up(self, system: LevelUpSystem) -> None:
        char = _make_char()
        result = system.gain_xp(char, 100)
        assert result is not None
        assert result.new_level == 2
        assert char.level == 2

    def test_gain_xp_returns_attribute_points(self, system: LevelUpSystem) -> None:
        char = _make_char()
        result = system.gain_xp(char, 100)
        assert result is not None
        assert result.physical_points == 2
        assert result.mental_points == 1

    def test_gain_xp_accumulates(self, system: LevelUpSystem) -> None:
        char = _make_char()
        system.gain_xp(char, 50)
        result = system.gain_xp(char, 60)  # total 110
        assert result is not None
        assert char.level == 2
        assert system.get_xp(char) == 110

    def test_gain_xp_multi_level(self, system: LevelUpSystem) -> None:
        char = _make_char()
        result = system.gain_xp(char, 600)
        assert result is not None
        assert char.level == 4
        assert result.new_level == 4

    def test_gain_xp_caps_at_max_level(self, system: LevelUpSystem) -> None:
        char = _make_char()
        system.gain_xp(char, 9999)
        assert char.level == SMALL_TABLE.max_level
        result = system.gain_xp(char, 100)
        assert result is None

    def test_gain_xp_zero_is_noop(self, system: LevelUpSystem) -> None:
        char = _make_char()
        result = system.gain_xp(char, 0)
        assert result is None
        assert system.get_xp(char) == 0

    def test_hp_increases_on_level_up(self, system: LevelUpSystem) -> None:
        char = _make_char()
        hp_at_1 = char.max_hp
        system.gain_xp(char, 100)
        assert char.max_hp > hp_at_1

    def test_regen_increases_on_level_up(self, system: LevelUpSystem) -> None:
        char = _make_char()
        regen_at_1 = char.hp_regen
        system.gain_xp(char, 100)
        assert char.hp_regen > regen_at_1


class TestDistributePoints:
    """Testes de distribuicao de pontos de atributo."""

    @pytest.fixture()
    def system(self) -> LevelUpSystem:
        return LevelUpSystem(SMALL_TABLE, SMALL_ATTR_CONFIG)

    def test_distribute_physical_points(self, system: LevelUpSystem) -> None:
        char = _make_char()
        old_str = char._attributes.get(AttributeType.STRENGTH)
        distribution = {AttributeType.STRENGTH: 1, AttributeType.DEXTERITY: 1}
        system.distribute_physical_points(char, distribution)
        assert char._attributes.get(AttributeType.STRENGTH) == old_str + 1

    def test_distribute_mental_points(self, system: LevelUpSystem) -> None:
        char = _make_char()
        old_wis = char._attributes.get(AttributeType.WISDOM)
        distribution = {AttributeType.WISDOM: 1}
        system.distribute_mental_points(char, distribution)
        assert char._attributes.get(AttributeType.WISDOM) == old_wis + 1

    def test_distribute_rejects_wrong_category(self, system: LevelUpSystem) -> None:
        char = _make_char()
        distribution = {AttributeType.STRENGTH: 1}  # STR is physical, not mental
        with pytest.raises(ValueError):
            system.distribute_mental_points(char, distribution)

    def test_distribute_physical_rejects_mental_attr(
        self, system: LevelUpSystem,
    ) -> None:
        char = _make_char()
        distribution = {AttributeType.WISDOM: 1}  # WIS is mental, not physical
        with pytest.raises(ValueError):
            system.distribute_physical_points(char, distribution)

    def test_distribute_invalidates_threshold_cache(
        self, system: LevelUpSystem,
    ) -> None:
        char = _make_char()
        _ = char.max_hp  # populates threshold cache
        distribution = {AttributeType.CONSTITUTION: 2}
        system.distribute_physical_points(char, distribution)
        assert char._threshold_cache is None


class TestWithRealData:
    """Testes com dados reais dos JSONs."""

    def test_level_1_to_10_with_real_xp_table(self) -> None:
        xp_table = load_xp_table()
        attr_config = load_attribute_points()
        system = LevelUpSystem(xp_table, attr_config)
        char = _make_char()
        system.gain_xp(char, 9999)
        assert char.level == 10
