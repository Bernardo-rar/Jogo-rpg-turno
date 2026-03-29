"""Testes de auto-distribuicao de pontos."""

from src.core.attributes.attribute_types import AttributeType
from src.core.progression.recommended_distribution import (
    auto_distribute,
    load_recommended,
)


class TestAutoDistribute:

    def test_two_points_go_to_first_two_priorities(self) -> None:
        priority = [
            AttributeType.STRENGTH,
            AttributeType.DEXTERITY,
            AttributeType.CONSTITUTION,
        ]
        dist = auto_distribute(2, priority)
        assert dist[AttributeType.STRENGTH] == 1
        assert dist[AttributeType.DEXTERITY] == 1
        assert dist[AttributeType.CONSTITUTION] == 0

    def test_three_points_spread_evenly(self) -> None:
        priority = [
            AttributeType.STRENGTH,
            AttributeType.DEXTERITY,
            AttributeType.CONSTITUTION,
        ]
        dist = auto_distribute(3, priority)
        assert dist[AttributeType.STRENGTH] == 1
        assert dist[AttributeType.DEXTERITY] == 1
        assert dist[AttributeType.CONSTITUTION] == 1

    def test_four_points_wraps_to_first(self) -> None:
        priority = [
            AttributeType.STRENGTH,
            AttributeType.DEXTERITY,
            AttributeType.CONSTITUTION,
        ]
        dist = auto_distribute(4, priority)
        assert dist[AttributeType.STRENGTH] == 2
        assert dist[AttributeType.DEXTERITY] == 1
        assert dist[AttributeType.CONSTITUTION] == 1

    def test_zero_points_returns_zeros(self) -> None:
        priority = [AttributeType.STRENGTH, AttributeType.DEXTERITY]
        dist = auto_distribute(0, priority)
        assert all(v == 0 for v in dist.values())

    def test_total_matches_input(self) -> None:
        priority = [
            AttributeType.INTELLIGENCE,
            AttributeType.WISDOM,
            AttributeType.CHARISMA,
            AttributeType.MIND,
        ]
        dist = auto_distribute(7, priority)
        assert sum(dist.values()) == 7


class TestLoadRecommended:

    def test_loads_all_classes(self) -> None:
        configs = load_recommended()
        assert len(configs) == 13

    def test_fighter_physical_priority(self) -> None:
        configs = load_recommended()
        fighter = configs["fighter"]
        assert fighter.physical[0] == AttributeType.STRENGTH

    def test_mage_mental_priority(self) -> None:
        configs = load_recommended()
        mage = configs["mage"]
        assert mage.mental[0] == AttributeType.INTELLIGENCE
