import pytest

from src.core.combat.turn_order import TurnOrder, Combatant


class FakeCombatant:
    """Combatant falso para testes, implementa o Protocol."""

    def __init__(self, name: str, speed: int) -> None:
        self._name = name
        self._speed = speed

    @property
    def name(self) -> str:
        return self._name

    @property
    def speed(self) -> int:
        return self._speed

    @property
    def is_alive(self) -> bool:
        return True


class DeadCombatant(FakeCombatant):
    @property
    def is_alive(self) -> bool:
        return False


class TestTurnOrderSorting:
    def test_single_combatant(self):
        a = FakeCombatant("A", speed=10)
        order = TurnOrder([a])
        assert order.get_order() == [a]

    def test_faster_goes_first(self):
        slow = FakeCombatant("Slow", speed=5)
        fast = FakeCombatant("Fast", speed=10)
        order = TurnOrder([slow, fast])
        assert order.get_order() == [fast, slow]

    def test_three_combatants_sorted_by_speed(self):
        a = FakeCombatant("A", speed=3)
        b = FakeCombatant("B", speed=7)
        c = FakeCombatant("C", speed=5)
        order = TurnOrder([a, b, c])
        assert order.get_order() == [b, c, a]

    def test_tie_broken_by_name_alphabetical(self):
        b = FakeCombatant("Bravo", speed=5)
        a = FakeCombatant("Alpha", speed=5)
        order = TurnOrder([b, a])
        result = order.get_order()
        assert result == [a, b]


class TestTurnOrderSkipsDead:
    def test_dead_combatant_excluded_from_order(self):
        alive = FakeCombatant("Alive", speed=5)
        dead = DeadCombatant("Dead", speed=10)
        order = TurnOrder([alive, dead])
        assert order.get_order() == [alive]

    def test_all_dead_returns_empty(self):
        dead1 = DeadCombatant("D1", speed=5)
        dead2 = DeadCombatant("D2", speed=10)
        order = TurnOrder([dead1, dead2])
        assert order.get_order() == []


class TestTurnOrderIteration:
    def test_next_returns_fastest_first(self):
        slow = FakeCombatant("Slow", speed=3)
        fast = FakeCombatant("Fast", speed=10)
        order = TurnOrder([slow, fast])
        assert order.next() == fast

    def test_next_advances_to_second(self):
        slow = FakeCombatant("Slow", speed=3)
        fast = FakeCombatant("Fast", speed=10)
        order = TurnOrder([slow, fast])
        order.next()
        assert order.next() == slow

    def test_next_returns_none_when_exhausted(self):
        a = FakeCombatant("A", speed=5)
        order = TurnOrder([a])
        order.next()
        assert order.next() is None

    def test_reset_restarts_iteration(self):
        a = FakeCombatant("A", speed=5)
        b = FakeCombatant("B", speed=10)
        order = TurnOrder([a, b])
        order.next()
        order.next()
        order.reset()
        assert order.next() == b

    def test_is_round_complete_after_all_acted(self):
        a = FakeCombatant("A", speed=5)
        order = TurnOrder([a])
        order.next()
        assert order.is_round_complete is True

    def test_is_round_complete_false_when_pending(self):
        a = FakeCombatant("A", speed=5)
        b = FakeCombatant("B", speed=10)
        order = TurnOrder([a, b])
        order.next()
        assert order.is_round_complete is False
