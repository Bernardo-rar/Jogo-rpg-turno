"""RunModifier — modificador de run roguelite."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ModifierCategory(Enum):
    """Categorias de modificadores de run."""

    DIFFICULTY = "DIFFICULTY"
    ECONOMY = "ECONOMY"
    RESTRICTION = "RESTRICTION"
    CHAOS = "CHAOS"


@dataclass(frozen=True)
class ModifierEffect:
    """Efeitos numéricos de um modificador — todos multiplicativos."""

    damage_taken_mult: float = 1.0
    damage_dealt_mult: float = 1.0
    healing_mult: float = 1.0
    gold_mult: float = 1.0
    elite_spawn_mult: float = 1.0
    boss_stat_mult: float = 1.0
    xp_mult: float = 1.0
    score_mult: float = 1.0
    start_hp_pct: float = 1.0

    @classmethod
    def from_dict(cls, data: dict) -> ModifierEffect:
        """Cria ModifierEffect a partir de dict (campos opcionais)."""
        return cls(
            damage_taken_mult=data.get("damage_taken_mult", 1.0),
            damage_dealt_mult=data.get("damage_dealt_mult", 1.0),
            healing_mult=data.get("healing_mult", 1.0),
            gold_mult=data.get("gold_mult", 1.0),
            elite_spawn_mult=data.get("elite_spawn_mult", 1.0),
            boss_stat_mult=data.get("boss_stat_mult", 1.0),
            xp_mult=data.get("xp_mult", 1.0),
            score_mult=data.get("score_mult", 1.0),
            start_hp_pct=data.get("start_hp_pct", 1.0),
        )


@dataclass(frozen=True)
class RunModifier:
    """Modificador selecionável antes de iniciar uma run."""

    modifier_id: str
    name: str
    description: str
    category: ModifierCategory
    effect: ModifierEffect

    @classmethod
    def from_dict(cls, modifier_id: str, data: dict) -> RunModifier:
        """Cria RunModifier a partir de dict (JSON parsed)."""
        return cls(
            modifier_id=modifier_id,
            name=data["name"],
            description=data["description"],
            category=ModifierCategory[data["category"]],
            effect=ModifierEffect.from_dict(data.get("effect", {})),
        )
