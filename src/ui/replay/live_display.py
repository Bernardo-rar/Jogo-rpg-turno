"""Cria RoundSnapshot a partir de Characters vivos (sem replay)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.ui.replay.battle_snapshot import RoundSnapshot, snapshot_character

if TYPE_CHECKING:
    from src.core.characters.character import Character


def create_live_snapshot(
    party: list[Character],
    enemies: list[Character],
    round_number: int,
) -> RoundSnapshot:
    """Cria snapshot imutavel do estado atual dos personagens."""
    chars = tuple(
        snapshot_character(c, is_party=True) for c in party
    ) + tuple(
        snapshot_character(c, is_party=False) for c in enemies
    )
    return RoundSnapshot(round_number=round_number, characters=chars)
