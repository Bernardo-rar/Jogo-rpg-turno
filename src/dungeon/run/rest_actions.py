"""Rest actions — ações disponíveis em rest rooms."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.characters.character import Character

REST_HEAL_PERCENT = 0.30
REST_MANA_PERCENT = 0.40


def apply_rest_heal(party: list[Character]) -> dict[str, int]:
    """Cura 30% do HP máximo de cada membro vivo."""
    results: dict[str, int] = {}
    for c in party:
        if c.is_alive:
            amount = int(c.max_hp * REST_HEAL_PERCENT)
            healed = c.heal(amount)
            results[c.name] = healed
    return results


def apply_rest_meditate(party: list[Character]) -> dict[str, int]:
    """Restaura 40% da mana máxima de cada membro vivo."""
    results: dict[str, int] = {}
    for c in party:
        if c.is_alive:
            amount = int(c.max_mana * REST_MANA_PERCENT)
            restored = c.restore_mana(amount)
            results[c.name] = restored
    return results
