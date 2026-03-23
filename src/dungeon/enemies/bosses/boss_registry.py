"""Registra phase handlers dos bosses no BossFactory."""

from __future__ import annotations

from src.dungeon.enemies.bosses.ancient_golem import (
    PHASE1_KEY as GOLEM_P1,
    PHASE2_KEY as GOLEM_P2,
    AncientGolemPhase1,
    AncientGolemPhase2,
)
from src.dungeon.enemies.bosses.boss_factory import register_phase_handler
from src.dungeon.enemies.bosses.goblin_king import (
    PHASE1_KEY as GK_P1,
    PHASE2_KEY as GK_P2,
    GoblinKingPhase1,
    GoblinKingPhase2,
)
from src.dungeon.enemies.bosses.lich_lord import (
    PHASE1_KEY as LICH_P1,
    PHASE2_KEY as LICH_P2,
    LichLordPhase1,
    LichLordPhase2,
)


def register_all_bosses() -> None:
    """Registra todos os phase handlers de boss."""
    register_phase_handler(GK_P1, GoblinKingPhase1)
    register_phase_handler(GK_P2, GoblinKingPhase2)
    register_phase_handler(GOLEM_P1, AncientGolemPhase1)
    register_phase_handler(GOLEM_P2, AncientGolemPhase2)
    register_phase_handler(LICH_P1, LichLordPhase1)
    register_phase_handler(LICH_P2, LichLordPhase2)
