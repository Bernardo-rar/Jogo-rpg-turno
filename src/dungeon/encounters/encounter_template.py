"""Templates de encounter — definem composicao de slots por dificuldade."""

from __future__ import annotations

from dataclasses import dataclass

from src.dungeon.encounters.encounter_difficulty import EncounterDifficulty
from src.dungeon.enemies.enemy_archetype import EnemyArchetype


@dataclass(frozen=True)
class EncounterSlot:
    """Slot de inimigo no encounter: archetype + flag de elite."""

    archetype: EnemyArchetype
    is_elite: bool = False
    synergy_role: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> EncounterSlot:
        return cls(
            archetype=EnemyArchetype(data["archetype"].lower()),
            is_elite=data.get("is_elite", False),
            synergy_role=str(data.get("synergy_role", "")),
        )


@dataclass(frozen=True)
class EncounterTemplate:
    """Template de encounter: dificuldade + slots de inimigos."""

    template_id: str
    difficulty: EncounterDifficulty
    slots: tuple[EncounterSlot, ...]
    synergy_id: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> EncounterTemplate:
        slots = tuple(EncounterSlot.from_dict(s) for s in data["slots"])
        return cls(
            template_id=data["template_id"],
            difficulty=EncounterDifficulty[data["difficulty"].upper()],
            slots=slots,
            synergy_id=str(data.get("synergy_id", "")),
        )
