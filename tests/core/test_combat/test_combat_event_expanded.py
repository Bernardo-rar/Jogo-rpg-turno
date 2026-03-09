"""Testes para CombatEvent expandido e EventType enum."""

from __future__ import annotations

from src.core.combat.combat_engine import CombatEvent, EventType
from src.core.combat.damage import DamageResult


class TestEventType:
    def test_has_damage(self) -> None:
        assert EventType.DAMAGE is not None

    def test_has_heal(self) -> None:
        assert EventType.HEAL is not None

    def test_has_buff(self) -> None:
        assert EventType.BUFF is not None

    def test_has_cleanse(self) -> None:
        assert EventType.CLEANSE is not None

    def test_has_flee(self) -> None:
        assert EventType.FLEE is not None

    def test_has_ten_members(self) -> None:
        assert len(EventType) == 10


class TestCombatEventExpanded:
    def test_backward_compat_with_damage(self) -> None:
        result = DamageResult(
            raw_damage=20, defense_value=5,
            is_critical=False, final_damage=15,
        )
        event = CombatEvent(
            round_number=1, actor_name="A",
            target_name="B", damage=result,
        )
        assert event.damage is result
        assert event.event_type == EventType.DAMAGE

    def test_heal_event_no_damage(self) -> None:
        event = CombatEvent(
            round_number=1, actor_name="Healer",
            target_name="Ally",
            event_type=EventType.HEAL, value=50,
            description="Minor Heal",
        )
        assert event.damage is None
        assert event.event_type == EventType.HEAL
        assert event.value == 50

    def test_buff_event(self) -> None:
        event = CombatEvent(
            round_number=2, actor_name="Buffer",
            target_name="Ally",
            event_type=EventType.BUFF, value=10,
            description="Defense Buff",
        )
        assert event.event_type == EventType.BUFF

    def test_defaults(self) -> None:
        event = CombatEvent(
            round_number=1, actor_name="A", target_name="B",
        )
        assert event.damage is None
        assert event.event_type == EventType.DAMAGE
        assert event.value == 0
        assert event.description == ""

    def test_flee_event(self) -> None:
        event = CombatEvent(
            round_number=3, actor_name="Runner",
            target_name="",
            event_type=EventType.FLEE,
            description="Smoke Bomb",
        )
        assert event.event_type == EventType.FLEE
