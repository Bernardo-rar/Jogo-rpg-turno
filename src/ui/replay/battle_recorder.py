"""Grava batalha round-by-round, capturando snapshots entre rounds."""

from __future__ import annotations

from src.core.characters.character import Character
from src.core.combat.combat_engine import CombatEngine
from src.ui.replay.battle_snapshot import (
    BattleReplay,
    RoundSnapshot,
    snapshot_character,
)


class BattleRecorder:
    """Executa batalha via run_round() e captura snapshots."""

    def __init__(
        self,
        engine: CombatEngine,
        party: list[Character],
        enemies: list[Character],
    ) -> None:
        self._engine = engine
        self._party = party
        self._enemies = enemies

    def record(self) -> BattleReplay:
        """Roda batalha completa, retorna replay com snapshots."""
        snapshots = [self._take_snapshot(0)]
        result = None
        while result is None:
            result = self._engine.run_round()
            rnd = self._engine.round_number
            snapshots.append(self._take_snapshot(rnd))
        return BattleReplay(
            snapshots=tuple(snapshots),
            events=tuple(self._engine.events),
            effect_log=tuple(self._engine.effect_log),
            result=result,
            total_rounds=self._engine.round_number,
        )

    def _take_snapshot(self, round_number: int) -> RoundSnapshot:
        party_snaps = _snapshot_team(self._party, is_party=True)
        enemy_snaps = _snapshot_team(self._enemies, is_party=False)
        return RoundSnapshot(
            round_number=round_number,
            characters=party_snaps + enemy_snaps,
        )


def _snapshot_team(
    team: list[Character], *, is_party: bool,
) -> tuple:
    return tuple(
        snapshot_character(c, is_party=is_party) for c in team
    )
