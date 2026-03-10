"""Testes para BattleRecorder - grava batalha round-by-round."""

from __future__ import annotations

from src.core.combat.basic_attack_handler import BasicAttackHandler
from src.core.combat.combat_engine import CombatEngine, CombatResult
from src.ui.replay.battle_recorder import BattleRecorder

from tests.core.test_combat.conftest import _build_char


def _run_simple_battle():
    party = [_build_char("Hero", speed=15)]
    enemies = [_build_char("Goblin", speed=5)]
    handler = BasicAttackHandler()
    engine = CombatEngine(party, enemies, handler)
    recorder = BattleRecorder(engine, party, enemies)
    return recorder.record()


class TestBattleRecorder:
    def test_replay_has_result(self) -> None:
        replay = _run_simple_battle()
        assert replay.result in (
            CombatResult.PARTY_VICTORY,
            CombatResult.PARTY_DEFEAT,
        )

    def test_snapshots_include_round_zero(self) -> None:
        replay = _run_simple_battle()
        assert replay.snapshots[0].round_number == 0

    def test_snapshot_count_matches_rounds(self) -> None:
        replay = _run_simple_battle()
        assert len(replay.snapshots) == replay.total_rounds + 1

    def test_events_match_engine(self) -> None:
        party = [_build_char("Hero", speed=15)]
        enemies = [_build_char("Goblin", speed=5)]
        handler = BasicAttackHandler()
        engine = CombatEngine(party, enemies, handler)
        recorder = BattleRecorder(engine, party, enemies)
        replay = recorder.record()
        assert len(replay.events) == len(engine.events)

    def test_initial_snapshot_has_full_hp(self) -> None:
        replay = _run_simple_battle()
        round_0 = replay.snapshots[0]
        for snap in round_0.characters:
            assert snap.current_hp == snap.max_hp

    def test_characters_have_party_flag(self) -> None:
        replay = _run_simple_battle()
        round_0 = replay.snapshots[0]
        names = {s.name: s.is_party for s in round_0.characters}
        assert names["Hero"] is True
        assert names["Goblin"] is False
