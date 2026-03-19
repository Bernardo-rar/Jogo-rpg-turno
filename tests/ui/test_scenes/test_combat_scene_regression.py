"""Testes de regressao — CombatScene (replay) e CombatLogPanel compacto."""

from __future__ import annotations

from src.core.combat.basic_attack_handler import BasicAttackHandler
from src.core.combat.combat_engine import CombatEngine, CombatResult
from src.ui.components.combat_log_panel import CombatLogPanel
from src.ui.replay.battle_recorder import BattleRecorder

from tests.core.test_combat.conftest import _build_char


class TestCombatSceneReplayRegression:
    def test_battle_recorder_produces_valid_replay(self) -> None:
        party = [_build_char("Hero")]
        enemies = [_build_char("Goblin")]
        engine = CombatEngine(party, enemies, BasicAttackHandler())
        recorder = BattleRecorder(engine, party, enemies)
        replay = recorder.record()
        assert replay.result in (
            CombatResult.PARTY_VICTORY,
            CombatResult.PARTY_DEFEAT,
        )
        assert len(replay.snapshots) >= 2
        assert len(replay.events) > 0

    def test_replay_snapshots_have_all_characters(self) -> None:
        party = [_build_char("A"), _build_char("B")]
        enemies = [_build_char("X")]
        engine = CombatEngine(party, enemies, BasicAttackHandler())
        recorder = BattleRecorder(engine, party, enemies)
        replay = recorder.record()
        first_snap = replay.snapshots[0]
        assert len(first_snap.characters) == 3


class TestCombatLogPanelCompact:
    def test_max_visible_default(self) -> None:
        panel = CombatLogPanel()
        assert panel.max_visible == 9

    def test_custom_max_visible(self) -> None:
        panel = CombatLogPanel(max_visible=4)
        assert panel.max_visible == 4

    def test_line_count_reflects_additions(self) -> None:
        panel = CombatLogPanel()
        panel.add_line("Line 1")
        panel.add_line("Line 2")
        assert panel.line_count == 2
