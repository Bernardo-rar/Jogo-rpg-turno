"""Testes para CombatLogEntry e CombatLog."""

import pytest

from src.core.combat.combat_engine import CombatEvent
from src.core.combat.combat_log import CombatLog, CombatLogEntry, EventType
from src.core.combat.damage import DamageResult


# --- CombatLogEntry ---


class TestCombatLogEntryImmutable:
    def test_entry_is_frozen(self):
        entry = CombatLogEntry(
            round_number=1, event_type=EventType.ATTACK, actor_name="A",
        )
        with pytest.raises(AttributeError):
            entry.round_number = 2

    def test_entry_defaults(self):
        entry = CombatLogEntry(
            round_number=1, event_type=EventType.ATTACK, actor_name="A",
        )
        assert entry.target_name == ""
        assert entry.value == 0
        assert entry.detail == ""

    def test_entry_with_all_fields(self):
        entry = CombatLogEntry(
            round_number=3, event_type=EventType.HEAL,
            actor_name="Cleric", target_name="Fighter",
            value=35, detail="holy",
        )
        assert entry.round_number == 3
        assert entry.event_type == EventType.HEAL
        assert entry.actor_name == "Cleric"
        assert entry.target_name == "Fighter"
        assert entry.value == 35
        assert entry.detail == "holy"


# --- CombatLog add/entries ---


class TestCombatLogAdd:
    def test_starts_empty(self):
        log = CombatLog()
        assert len(log.entries) == 0

    def test_add_single_entry(self):
        log = CombatLog()
        entry = CombatLogEntry(
            round_number=1, event_type=EventType.ATTACK, actor_name="A",
        )
        log.add(entry)
        assert len(log.entries) == 1
        assert log.entries[0] is entry

    def test_add_multiple_entries(self):
        log = CombatLog()
        for i in range(5):
            log.add(CombatLogEntry(
                round_number=i, event_type=EventType.ATTACK, actor_name="A",
            ))
        assert len(log.entries) == 5

    def test_entries_returns_copy(self):
        log = CombatLog()
        log.add(CombatLogEntry(
            round_number=1, event_type=EventType.ATTACK, actor_name="A",
        ))
        copy = log.entries
        copy.clear()
        assert len(log.entries) == 1


# --- add_from_combat_event ---


class TestAddFromCombatEvent:
    def test_converts_attack_event(self):
        log = CombatLog()
        damage = DamageResult(
            raw_damage=50, defense_value=10, is_critical=False, final_damage=40,
        )
        event = CombatEvent(
            round_number=2, actor_name="Gareth",
            target_name="Goblin_0", damage=damage,
        )
        log.add_from_combat_event(event)
        assert len(log.entries) == 1
        entry = log.entries[0]
        assert entry.event_type == EventType.ATTACK
        assert entry.round_number == 2
        assert entry.actor_name == "Gareth"
        assert entry.target_name == "Goblin_0"
        assert entry.value == 40

    def test_critical_noted_in_detail(self):
        log = CombatLog()
        damage = DamageResult(
            raw_damage=50, defense_value=10, is_critical=True, final_damage=90,
        )
        event = CombatEvent(
            round_number=1, actor_name="A", target_name="B", damage=damage,
        )
        log.add_from_combat_event(event)
        assert "critical" in log.entries[0].detail


# --- Filtros ---


class TestCombatLogFilters:
    @pytest.fixture
    def populated_log(self):
        log = CombatLog()
        log.add(CombatLogEntry(
            round_number=1, event_type=EventType.ATTACK,
            actor_name="Gareth", target_name="Goblin_0", value=40,
        ))
        log.add(CombatLogEntry(
            round_number=1, event_type=EventType.BARRIER_CREATE,
            actor_name="Merlin", value=100,
        ))
        log.add(CombatLogEntry(
            round_number=1, event_type=EventType.HEAL,
            actor_name="Aurelia", target_name="Gareth", value=35,
        ))
        log.add(CombatLogEntry(
            round_number=2, event_type=EventType.ATTACK,
            actor_name="Gareth", target_name="Goblin_1", value=55,
        ))
        log.add(CombatLogEntry(
            round_number=2, event_type=EventType.DEATH,
            actor_name="Goblin_1",
        ))
        return log

    def test_get_by_round_returns_correct_entries(self, populated_log):
        r1 = populated_log.get_by_round(1)
        assert len(r1) == 3
        assert all(e.round_number == 1 for e in r1)

    def test_get_by_round_empty_for_missing_round(self, populated_log):
        assert len(populated_log.get_by_round(99)) == 0

    def test_get_by_actor_returns_correct_entries(self, populated_log):
        gareth = populated_log.get_by_actor("Gareth")
        assert len(gareth) == 2
        assert all(e.actor_name == "Gareth" for e in gareth)

    def test_get_by_actor_empty_for_missing_name(self, populated_log):
        assert len(populated_log.get_by_actor("Nobody")) == 0

    def test_get_by_type_returns_correct_entries(self, populated_log):
        attacks = populated_log.get_by_type(EventType.ATTACK)
        assert len(attacks) == 2
        assert all(e.event_type == EventType.ATTACK for e in attacks)

    def test_get_by_type_single_match(self, populated_log):
        deaths = populated_log.get_by_type(EventType.DEATH)
        assert len(deaths) == 1
        assert deaths[0].actor_name == "Goblin_1"

    def test_get_by_type_no_match(self, populated_log):
        assert len(populated_log.get_by_type(EventType.OVERCHARGE_ON)) == 0
