"""EnemyTemplate — blueprint imutável de um monstro."""

from __future__ import annotations

from dataclasses import dataclass, field

from src.core.attributes.attribute_types import AttributeType
from src.core.characters.class_modifiers import ClassModifiers
from src.core.characters.position import Position
from src.dungeon.enemies.enemy_archetype import EnemyArchetype


@dataclass(frozen=True)
class EnemyTemplate:
    """Blueprint de dados para criar um Character inimigo."""

    enemy_id: str
    name: str
    tier: int
    archetype: EnemyArchetype
    class_modifiers: ClassModifiers
    base_attributes: dict[AttributeType, int]
    position: Position
    elemental_profile_id: str
    weapon_id: str
    skill_ids: tuple[str, ...] = ()
    special_traits: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, data: dict) -> EnemyTemplate:
        """Cria EnemyTemplate a partir de um dict (JSON parsed)."""
        mods = ClassModifiers.from_dict(data["class_modifiers"])
        attrs = {
            AttributeType[k]: v
            for k, v in data["base_attributes"].items()
        }
        return cls(
            enemy_id=data["enemy_id"],
            name=data["name"],
            tier=data["tier"],
            archetype=EnemyArchetype(data["archetype"].lower()),
            class_modifiers=mods,
            base_attributes=attrs,
            position=Position[data["position"]],
            elemental_profile_id=data.get("elemental_profile_id", "neutral"),
            weapon_id=data.get("weapon_id", ""),
            skill_ids=tuple(data.get("skill_ids", [])),
            special_traits=tuple(data.get("special_traits", [])),
        )
