"""Testes para PhaseHandler — transição de fase por HP threshold."""

from __future__ import annotations

from src.core.combat.action_economy import ActionEconomy
from src.core.combat.combat_engine import CombatEvent, TurnContext
from src.dungeon.enemies.bosses.boss_phase import BossPhase
from src.dungeon.enemies.bosses.phase_handler import PhaseHandler
from tests.dungeon.enemies.ai.conftest import make_char

_PHASE1 = BossPhase(phase_number=1, hp_threshold=0.5, handler_key="p1")
_PHASE2 = BossPhase(phase_number=2, hp_threshold=0.0, handler_key="p2")


class _TrackerHandler:
    """Handler de teste que registra qual key foi chamado."""

    def __init__(self, key: str) -> None:
        self.key = key
        self.call_count = 0

    def execute_turn(self, context: TurnContext) -> list[CombatEvent]:
        self.call_count += 1
        return []


def _make_context(boss, hp_pct: float) -> TurnContext:
    """Cria contexto com boss no HP ratio desejado."""
    damage = int(boss.max_hp * (1.0 - hp_pct))
    if damage > 0:
        boss.take_damage(damage)
    return TurnContext(
        combatant=boss,
        allies=[boss],
        enemies=[make_char("Hero")],
        action_economy=ActionEconomy(),
        round_number=1,
    )


class TestPhaseHandler:

    def test_starts_in_phase1_at_full_hp(self) -> None:
        p1 = _TrackerHandler("p1")
        p2 = _TrackerHandler("p2")
        handler = PhaseHandler(
            phases=(_PHASE1, _PHASE2),
            phase_handlers={"p1": p1, "p2": p2},
            default_handler=_TrackerHandler("default"),
        )
        boss = make_char("Boss")
        ctx = _make_context(boss, hp_pct=1.0)
        handler.execute_turn(ctx)
        assert handler.current_phase == 1
        assert p1.call_count == 1
        assert p2.call_count == 0

    def test_transitions_to_phase2_below_threshold(self) -> None:
        p1 = _TrackerHandler("p1")
        p2 = _TrackerHandler("p2")
        handler = PhaseHandler(
            phases=(_PHASE1, _PHASE2),
            phase_handlers={"p1": p1, "p2": p2},
            default_handler=_TrackerHandler("default"),
        )
        boss = make_char("Boss")
        ctx = _make_context(boss, hp_pct=0.3)
        handler.execute_turn(ctx)
        assert handler.current_phase == 2
        assert p2.call_count == 1

    def test_stays_phase1_at_threshold(self) -> None:
        p1 = _TrackerHandler("p1")
        p2 = _TrackerHandler("p2")
        handler = PhaseHandler(
            phases=(_PHASE1, _PHASE2),
            phase_handlers={"p1": p1, "p2": p2},
            default_handler=_TrackerHandler("default"),
        )
        boss = make_char("Boss")
        # Exatamente 51% — acima do threshold de 0.5
        ctx = _make_context(boss, hp_pct=0.51)
        handler.execute_turn(ctx)
        assert handler.current_phase == 1

    def test_phase2_at_exactly_50_pct(self) -> None:
        p1 = _TrackerHandler("p1")
        p2 = _TrackerHandler("p2")
        handler = PhaseHandler(
            phases=(_PHASE1, _PHASE2),
            phase_handlers={"p1": p1, "p2": p2},
            default_handler=_TrackerHandler("default"),
        )
        boss = make_char("Boss")
        # 50% = threshold, NOT > threshold, so phase 2
        ctx = _make_context(boss, hp_pct=0.50)
        handler.execute_turn(ctx)
        assert handler.current_phase == 2

    def test_uses_default_if_key_missing(self) -> None:
        default = _TrackerHandler("default")
        handler = PhaseHandler(
            phases=(_PHASE1, _PHASE2),
            phase_handlers={},
            default_handler=default,
        )
        boss = make_char("Boss")
        ctx = _make_context(boss, hp_pct=1.0)
        handler.execute_turn(ctx)
        assert default.call_count == 1

    def test_phases_sorted_by_threshold(self) -> None:
        """Ordem de input nao importa — phases devem ser ordenadas."""
        p1 = _TrackerHandler("p1")
        p2 = _TrackerHandler("p2")
        # Passando na ordem invertida
        handler = PhaseHandler(
            phases=(_PHASE2, _PHASE1),
            phase_handlers={"p1": p1, "p2": p2},
            default_handler=_TrackerHandler("default"),
        )
        boss = make_char("Boss")
        ctx = _make_context(boss, hp_pct=0.8)
        handler.execute_turn(ctx)
        assert handler.current_phase == 1


class TestBossPhase:

    def test_from_dict(self) -> None:
        data = {
            "phase_number": 1,
            "hp_threshold": 0.5,
            "handler_key": "test_p1",
        }
        phase = BossPhase.from_dict(data)
        assert phase.phase_number == 1
        assert phase.hp_threshold == 0.5
        assert phase.handler_key == "test_p1"

    def test_frozen(self) -> None:
        phase = BossPhase(phase_number=1, hp_threshold=0.5, handler_key="p1")
        try:
            phase.phase_number = 2  # type: ignore[misc]
            assert False, "Should be frozen"
        except AttributeError:
            pass
