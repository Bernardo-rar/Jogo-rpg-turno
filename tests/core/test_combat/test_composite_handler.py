"""Testes para CompositeHandler - encadeia TurnHandlers."""

from __future__ import annotations

from src.core.combat.combat_engine import CombatEvent, EventType, TurnContext
from src.core.combat.composite_handler import CompositeHandler

from tests.core.test_combat.conftest import _build_char


class _FakeHandler:
    """Handler de teste que retorna eventos fixos."""

    def __init__(self, events: list[CombatEvent]) -> None:
        self._events = events
        self.called = False

    def execute_turn(self, context: TurnContext) -> list[CombatEvent]:
        self.called = True
        return self._events


def _dummy_event() -> CombatEvent:
    return CombatEvent(
        round_number=1, actor_name="A", target_name="B",
        event_type=EventType.DAMAGE,
    )


def _make_context():
    hero = _build_char("Hero")
    from src.core.combat.action_economy import ActionEconomy
    return TurnContext(
        combatant=hero, allies=[hero],
        enemies=[_build_char("E")],
        action_economy=ActionEconomy(), round_number=1,
    )


class TestCompositeHandler:
    def test_returns_events_from_first_handler(self) -> None:
        event = _dummy_event()
        h1 = _FakeHandler([event])
        h2 = _FakeHandler([_dummy_event()])
        composite = CompositeHandler((h1, h2))
        result = composite.execute_turn(_make_context())
        assert result == [event]

    def test_skips_handler_returning_empty(self) -> None:
        event = _dummy_event()
        h1 = _FakeHandler([])
        h2 = _FakeHandler([event])
        composite = CompositeHandler((h1, h2))
        result = composite.execute_turn(_make_context())
        assert result == [event]

    def test_all_empty_returns_empty(self) -> None:
        h1 = _FakeHandler([])
        h2 = _FakeHandler([])
        composite = CompositeHandler((h1, h2))
        result = composite.execute_turn(_make_context())
        assert result == []

    def test_stops_after_first_success(self) -> None:
        h1 = _FakeHandler([_dummy_event()])
        h2 = _FakeHandler([_dummy_event()])
        composite = CompositeHandler((h1, h2))
        composite.execute_turn(_make_context())
        assert h1.called
        assert not h2.called
