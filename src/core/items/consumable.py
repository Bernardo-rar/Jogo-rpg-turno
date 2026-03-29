"""Consumable frozen dataclass - descreve um item consumivel do jogo."""

from __future__ import annotations

from dataclasses import dataclass

from src.core.items.consumable_category import ConsumableCategory
from src.core.items.consumable_effect import ConsumableEffect
from src.core.skills.target_type import TargetType

_DEFAULT_MAX_STACK = 10


@dataclass(frozen=True)
class Consumable:
    """Item consumivel com categoria, custo de mana, efeitos e stack."""

    consumable_id: str
    name: str
    category: ConsumableCategory
    mana_cost: int
    target_type: TargetType
    effects: tuple[ConsumableEffect, ...]
    max_stack: int = _DEFAULT_MAX_STACK
    description: str = ""
    usable_outside_combat: bool = False

    @classmethod
    def from_dict(
        cls, consumable_id: str, data: dict[str, object],
    ) -> Consumable:
        """Cria Consumable a partir de dict (JSON)."""
        raw_effects = data.get("effects", [])
        effects = tuple(
            ConsumableEffect.from_dict(e) for e in raw_effects  # type: ignore[union-attr]
        )
        return cls(
            consumable_id=consumable_id,
            name=str(data["name"]),
            category=ConsumableCategory[str(data["category"])],
            mana_cost=int(data["mana_cost"]),  # type: ignore[arg-type]
            target_type=TargetType[str(data["target_type"])],
            effects=effects,
            max_stack=int(data.get("max_stack", _DEFAULT_MAX_STACK)),  # type: ignore[arg-type]
            description=str(data.get("description", "")),
            usable_outside_combat=bool(data.get("usable_outside_combat", False)),
        )
