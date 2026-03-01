"""Testes para LogFormatter (to_text e to_json)."""

import json

import pytest

from src.core.combat.combat_log import CombatLog, CombatLogEntry, EventType
from src.core.combat.log_formatter import LogFormatter


@pytest.fixture
def sample_log():
    log = CombatLog()
    log.add(CombatLogEntry(
        round_number=1, event_type=EventType.ATTACK,
        actor_name="Gareth", target_name="Goblin_0",
        value=85, detail="physical",
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
        round_number=2, event_type=EventType.MANA_RESTORE,
        actor_name="Merlin", value=30,
    ))
    log.add(CombatLogEntry(
        round_number=2, event_type=EventType.DEATH,
        actor_name="Goblin_0",
    ))
    return log


class TestLogFormatterText:
    def test_attack_line_format(self, sample_log):
        text = LogFormatter.to_text(sample_log)
        assert "[Round 1] Gareth attacks Goblin_0 for 85 damage (physical)" in text

    def test_barrier_line_format(self, sample_log):
        text = LogFormatter.to_text(sample_log)
        assert "[Round 1] Merlin creates barrier (100 shield points)" in text

    def test_heal_line_format(self, sample_log):
        text = LogFormatter.to_text(sample_log)
        assert "[Round 1] Aurelia heals Gareth for 35 HP" in text

    def test_mana_restore_line_format(self, sample_log):
        text = LogFormatter.to_text(sample_log)
        assert "[Round 2] Merlin restores 30 mana" in text

    def test_death_line_format(self, sample_log):
        text = LogFormatter.to_text(sample_log)
        assert "[Round 2] Goblin_0 has fallen" in text

    def test_empty_log_returns_empty_string(self):
        text = LogFormatter.to_text(CombatLog())
        assert text == ""

    def test_overcharge_on_format(self):
        log = CombatLog()
        log.add(CombatLogEntry(
            round_number=1, event_type=EventType.OVERCHARGE_ON,
            actor_name="Merlin",
        ))
        text = LogFormatter.to_text(log)
        assert "[Round 1] Merlin activates overcharge" in text

    def test_channel_divinity_format(self):
        log = CombatLog()
        log.add(CombatLogEntry(
            round_number=3, event_type=EventType.CHANNEL_DIVINITY,
            actor_name="Aurelia",
        ))
        text = LogFormatter.to_text(log)
        assert "[Round 3] Aurelia channels divinity" in text


class TestLogFormatterJson:
    def test_json_is_valid(self, sample_log):
        raw = LogFormatter.to_json(sample_log)
        parsed = json.loads(raw)
        assert isinstance(parsed, list)

    def test_json_entry_count(self, sample_log):
        parsed = json.loads(LogFormatter.to_json(sample_log))
        assert len(parsed) == 5

    def test_json_entry_fields(self, sample_log):
        parsed = json.loads(LogFormatter.to_json(sample_log))
        first = parsed[0]
        assert first["round_number"] == 1
        assert first["event_type"] == "ATTACK"
        assert first["actor_name"] == "Gareth"
        assert first["target_name"] == "Goblin_0"
        assert first["value"] == 85
        assert first["detail"] == "physical"

    def test_empty_log_returns_empty_array(self):
        raw = LogFormatter.to_json(CombatLog())
        assert json.loads(raw) == []
