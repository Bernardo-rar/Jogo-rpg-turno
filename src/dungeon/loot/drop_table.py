"""Drop table — selecao ponderada de loot pos-combate."""

from __future__ import annotations

from dataclasses import dataclass
from random import Random


@dataclass(frozen=True)
class LootDrop:
    """Um item dropado."""

    item_type: str
    item_id: str
    quantity: int = 1


@dataclass(frozen=True)
class DropEntry:
    """Entrada na tabela de drops com peso para selecao."""

    item_type: str
    item_id: str
    weight: int
    quantity: int = 1


@dataclass(frozen=True)
class DropTable:
    """Tabela de drops com entradas ponderadas."""

    drops: tuple[DropEntry, ...]


def _pick_one(table: DropTable, rng: Random) -> LootDrop:
    """Seleciona 1 drop via weighted random."""
    entries = table.drops
    weights = [e.weight for e in entries]
    chosen = rng.choices(entries, weights=weights, k=1)[0]
    return LootDrop(
        item_type=chosen.item_type,
        item_id=chosen.item_id,
        quantity=chosen.quantity,
    )


def resolve_drops(
    table: DropTable, count: int, rng: Random,
) -> list[LootDrop]:
    """Resolve N drops da tabela via selecao ponderada."""
    if count <= 0:
        return []
    return [_pick_one(table, rng) for _ in range(count)]
