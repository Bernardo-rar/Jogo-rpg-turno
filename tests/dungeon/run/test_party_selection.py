"""Testes para PartySelection."""

from src.core.classes.class_id import ClassId
from src.dungeon.run.party_selection import PartySelection


def _all_classes() -> tuple[ClassId, ...]:
    return tuple(ClassId)


class TestPartySelection:

    def test_select_adds_class(self) -> None:
        ps = PartySelection(_all_classes())
        assert ps.select(ClassId.FIGHTER) is True
        assert ClassId.FIGHTER in ps.selected

    def test_select_duplicate_returns_false(self) -> None:
        ps = PartySelection(_all_classes())
        ps.select(ClassId.FIGHTER)
        assert ps.select(ClassId.FIGHTER) is False

    def test_select_fifth_returns_false(self) -> None:
        ps = PartySelection(_all_classes())
        ps.select(ClassId.FIGHTER)
        ps.select(ClassId.MAGE)
        ps.select(ClassId.CLERIC)
        ps.select(ClassId.ROGUE)
        assert ps.select(ClassId.RANGER) is False

    def test_select_unavailable_returns_false(self) -> None:
        ps = PartySelection((ClassId.FIGHTER, ClassId.MAGE))
        assert ps.select(ClassId.CLERIC) is False

    def test_deselect_removes_class(self) -> None:
        ps = PartySelection(_all_classes())
        ps.select(ClassId.FIGHTER)
        assert ps.deselect(ClassId.FIGHTER) is True
        assert ClassId.FIGHTER not in ps.selected

    def test_deselect_absent_returns_false(self) -> None:
        ps = PartySelection(_all_classes())
        assert ps.deselect(ClassId.FIGHTER) is False

    def test_is_valid_four_with_frontliner(self) -> None:
        ps = PartySelection(_all_classes())
        ps.select(ClassId.FIGHTER)
        ps.select(ClassId.MAGE)
        ps.select(ClassId.CLERIC)
        ps.select(ClassId.ROGUE)
        assert ps.is_valid() is True

    def test_is_valid_three_selected(self) -> None:
        ps = PartySelection(_all_classes())
        ps.select(ClassId.FIGHTER)
        ps.select(ClassId.MAGE)
        ps.select(ClassId.CLERIC)
        assert ps.is_valid() is False

    def test_is_valid_no_frontliner(self) -> None:
        ps = PartySelection(_all_classes())
        ps.select(ClassId.MAGE)
        ps.select(ClassId.CLERIC)
        ps.select(ClassId.ROGUE)
        ps.select(ClassId.RANGER)
        assert ps.is_valid() is False
