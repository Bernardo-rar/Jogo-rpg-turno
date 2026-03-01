"""Testes para extensao do CombatLog com EventTypes de efeitos."""

from src.core.combat.combat_log import CombatLog, CombatLogEntry, EventType
from src.core.combat.log_formatter import LogFormatter


class TestNewEventTypesExist:

    def test_effect_apply_exists(self) -> None:
        assert isinstance(EventType.EFFECT_APPLY, EventType)

    def test_effect_tick_exists(self) -> None:
        assert isinstance(EventType.EFFECT_TICK, EventType)

    def test_effect_expire_exists(self) -> None:
        assert isinstance(EventType.EFFECT_EXPIRE, EventType)

    def test_elemental_damage_exists(self) -> None:
        assert isinstance(EventType.ELEMENTAL_DAMAGE, EventType)

    def test_skip_turn_exists(self) -> None:
        assert isinstance(EventType.SKIP_TURN, EventType)


class TestFormatterRendersNewEvents:

    def test_renders_effect_apply(self) -> None:
        log = CombatLog()
        log.add(CombatLogEntry(
            round_number=1, event_type=EventType.EFFECT_APPLY,
            actor_name="Goblin", detail="Burn",
        ))
        text = LogFormatter.to_text(log)
        assert "Goblin" in text
        assert "Burn" in text

    def test_renders_effect_tick(self) -> None:
        log = CombatLog()
        log.add(CombatLogEntry(
            round_number=2, event_type=EventType.EFFECT_TICK,
            actor_name="Goblin", value=10, detail="Burn deals 10 fire damage",
        ))
        text = LogFormatter.to_text(log)
        assert "Goblin" in text
        assert "10" in text

    def test_renders_effect_expire(self) -> None:
        log = CombatLog()
        log.add(CombatLogEntry(
            round_number=3, event_type=EventType.EFFECT_EXPIRE,
            actor_name="Goblin", detail="Burn",
        ))
        text = LogFormatter.to_text(log)
        assert "wears off" in text
        assert "Goblin" in text

    def test_renders_elemental_damage(self) -> None:
        log = CombatLog()
        log.add(CombatLogEntry(
            round_number=1, event_type=EventType.ELEMENTAL_DAMAGE,
            actor_name="Mage", target_name="Dragon", value=50, detail="FIRE",
        ))
        text = LogFormatter.to_text(log)
        assert "Mage" in text
        assert "Dragon" in text
        assert "50" in text

    def test_renders_skip_turn(self) -> None:
        log = CombatLog()
        log.add(CombatLogEntry(
            round_number=1, event_type=EventType.SKIP_TURN,
            actor_name="Fighter", detail="Frozen solid",
        ))
        text = LogFormatter.to_text(log)
        assert "Fighter" in text
        assert "cannot act" in text
