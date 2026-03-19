"""Testes para action_economy_bar — labels e mapeamento de ActionType."""

from src.core.combat.action_economy import ActionType
from src.ui.components.action_economy_bar import get_economy_labels


class TestEconomyBarLabels:
    def test_has_three_slots(self) -> None:
        labels = get_economy_labels()
        assert len(labels) == 3

    def test_action_is_first(self) -> None:
        labels = get_economy_labels()
        assert labels[0] == (ActionType.ACTION, "A")

    def test_bonus_action_is_second(self) -> None:
        labels = get_economy_labels()
        assert labels[1] == (ActionType.BONUS_ACTION, "B")

    def test_reaction_is_third(self) -> None:
        labels = get_economy_labels()
        assert labels[2] == (ActionType.REACTION, "R")
