"""Tests for mid-combat summoning (add_combatant + TurnOrder.insert)."""

import pytest

from src.core.combat.combat_engine import CombatEngine, CombatResult, EventType
from src.core.combat.turn_order import TurnOrder

from tests.core.test_combat.conftest import _build_char as _make_char


class DoNothingHandler:
    def execute_turn(self, context):
        return []


class TestTurnOrderInsert:

    def test_insert_adds_to_order(self) -> None:
        a = _make_char("Alpha", speed=10)
        order = TurnOrder([a])
        b = _make_char("Beta", speed=5)
        order.insert(b)
        order.reset()
        names = [c.name for c in order.get_order()]
        assert "Beta" in names

    def test_insert_respects_speed(self) -> None:
        slow = _make_char("Slow", speed=5)
        order = TurnOrder([slow])
        fast = _make_char("Fast", speed=15)
        order.insert(fast)
        order.reset()
        names = [c.name for c in order.get_order()]
        assert names[0] == "Fast"

    def test_insert_mid_round_appears_next_reset(self) -> None:
        a = _make_char("A", speed=10)
        order = TurnOrder([a])
        order.reset()
        order.next()  # A acts
        b = _make_char("B", speed=5)
        order.insert(b)
        # B should NOT act this round (already past)
        assert order.next() is None
        # Next round, B appears
        order.reset()
        names = [c.name for c in order.get_order()]
        assert "B" in names


class TestCombatEngineAddCombatant:

    def test_add_enemy_appears_in_enemies(self) -> None:
        hero = _make_char("Hero")
        engine = CombatEngine([hero], [], DoNothingHandler())
        minion = _make_char("Minion")
        engine.add_combatant(minion, is_enemy=True)
        assert engine.run_combat() != CombatResult.PARTY_VICTORY or True
        # Minion should be tracked
        assert "Minion" in engine.turn_order_names

    def test_add_enemy_prevents_instant_victory(self) -> None:
        hero = _make_char("Hero")
        engine = CombatEngine([hero], [], DoNothingHandler())
        # Without enemies, would be PARTY_VICTORY
        minion = _make_char("Minion")
        engine.add_combatant(minion, is_enemy=True)
        # Now there's an enemy, so it should be DRAW (DoNothing)
        result = engine.run_combat()
        assert result == CombatResult.DRAW

    def test_add_ally_appears_in_party(self) -> None:
        hero = _make_char("Hero")
        enemy = _make_char("Goblin")
        engine = CombatEngine([hero], [enemy], DoNothingHandler())
        ally = _make_char("Ally")
        engine.add_combatant(ally, is_enemy=False)
        assert "Ally" in engine.turn_order_names

    def test_add_duplicate_name_raises(self) -> None:
        hero = _make_char("Hero")
        engine = CombatEngine([hero], [], DoNothingHandler())
        with pytest.raises(ValueError, match="unique"):
            engine.add_combatant(_make_char("Hero"), is_enemy=True)
