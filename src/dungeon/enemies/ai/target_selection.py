"""Funcoes puras de selecao de alvo para IA de inimigos."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.core.characters.position import Position

if TYPE_CHECKING:
    from src.core.characters.character import Character


def pick_lowest_hp_ratio(targets: list[Character]) -> Character | None:
    """Retorna alvo vivo com menor ratio HP atual / HP maximo."""
    alive = [t for t in targets if t.is_alive]
    if not alive:
        return None
    return min(alive, key=_hp_ratio)


def pick_backline_targets(targets: list[Character]) -> list[Character]:
    """Filtra alvos vivos na posicao BACK."""
    return [t for t in targets if t.is_alive and t.position == Position.BACK]


def pick_highest_threat(targets: list[Character]) -> Character | None:
    """Retorna alvo vivo com maior attack_power."""
    alive = [t for t in targets if t.is_alive]
    if not alive:
        return None
    return max(alive, key=lambda c: c.attack_power)


def _hp_ratio(char: Character) -> float:
    if char.max_hp == 0:
        return 1.0
    return char.current_hp / char.max_hp
