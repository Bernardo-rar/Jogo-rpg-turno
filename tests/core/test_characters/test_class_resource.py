"""Testes para os Protocols GainableResource e SpendableResource."""

from __future__ import annotations

from src.core.characters.class_resource import GainableResource, SpendableResource
from src.core.classes.barbarian.fury_bar import FuryBar
from src.core.classes.cleric.holy_power import HolyPower
from src.core.classes.fighter.action_points import ActionPoints


class TestSpendableResourceProtocol:
    def test_action_points_satisfies_spendable_protocol(self) -> None:
        ap = ActionPoints(level=1)
        assert isinstance(ap, SpendableResource)

    def test_fury_bar_satisfies_spendable_protocol(self) -> None:
        fury = FuryBar(max_fury=100)
        assert isinstance(fury, SpendableResource)

    def test_holy_power_satisfies_spendable_protocol(self) -> None:
        hp = HolyPower()
        assert isinstance(hp, SpendableResource)


class TestGainableResourceProtocol:
    def test_action_points_satisfies_gainable_protocol(self) -> None:
        ap = ActionPoints(level=1)
        assert isinstance(ap, GainableResource)

    def test_fury_bar_satisfies_gainable_protocol(self) -> None:
        fury = FuryBar(max_fury=100)
        assert isinstance(fury, GainableResource)

    def test_holy_power_satisfies_gainable_protocol(self) -> None:
        hp = HolyPower()
        assert isinstance(hp, GainableResource)
