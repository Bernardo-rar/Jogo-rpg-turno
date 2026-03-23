"""Aplica ganho de recurso de classe ao realizar ataque básico.

Dispatch table data-driven: cada classe tem um recurso com .gain().
Duck typing via getattr — se o personagem não tiver o recurso, ignora.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.characters.character import Character

_RESOURCE_GAINS: tuple[tuple[str, int], ...] = (
    ("action_points", 1),
    ("fury_bar", 10),
    ("holy_power", 1),
    ("divine_favor", 1),
    ("predatory_focus", 1),
    ("mana_rotation", 1),
    ("insanity", 5),
    ("groove", 1),
)


def on_basic_attack(combatant: Character) -> None:
    """Concede recurso de classe após ataque básico."""
    for attr_name, amount in _RESOURCE_GAINS:
        resource = getattr(combatant, attr_name, None)
        if resource is None:
            continue
        gain_fn = getattr(resource, "gain", None)
        if gain_fn is not None:
            _safe_gain(gain_fn, amount)
            return


def _safe_gain(gain_fn: object, amount: int) -> None:
    """Chama gain(amount) ou gain() se não aceitar argumento."""
    try:
        gain_fn(amount)
    except TypeError:
        gain_fn()
