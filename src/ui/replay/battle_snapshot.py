"""Dataclasses frozen para snapshots do estado da batalha."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from src.core.characters.position import Position
from src.core.combat.combat_engine import CombatEvent, CombatResult
from src.core.combat.effect_phase import EffectLogEntry

if TYPE_CHECKING:
    from src.core.characters.character import Character


@dataclass(frozen=True)
class CharacterSnapshot:
    """Estado imutavel de um personagem num instante da batalha."""

    name: str
    current_hp: int
    max_hp: int
    current_mana: int
    max_mana: int
    position: Position
    is_alive: bool
    active_effects: tuple[str, ...]
    is_party: bool


@dataclass(frozen=True)
class RoundSnapshot:
    """Estado de todos os personagens ao final de um round."""

    round_number: int
    characters: tuple[CharacterSnapshot, ...]


@dataclass(frozen=True)
class BattleReplay:
    """Replay completo da batalha: snapshots + eventos."""

    snapshots: tuple[RoundSnapshot, ...]
    events: tuple[CombatEvent, ...]
    effect_log: tuple[EffectLogEntry, ...]
    result: CombatResult
    total_rounds: int


def snapshot_character(char: Character, *, is_party: bool) -> CharacterSnapshot:
    """Captura estado atual de um Character como snapshot imutavel."""
    effects = _extract_effect_names(char)
    return CharacterSnapshot(
        name=char.name,
        current_hp=char.current_hp,
        max_hp=char.max_hp,
        current_mana=char.current_mana,
        max_mana=char.max_mana,
        position=char.position,
        is_alive=char.is_alive,
        active_effects=effects,
        is_party=is_party,
    )


def _extract_effect_names(char: Character) -> tuple[str, ...]:
    return tuple(e.name for e in char.effect_manager.active_effects)
