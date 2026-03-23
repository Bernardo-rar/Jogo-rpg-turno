"""BossTemplate — blueprint de boss com fases."""

from __future__ import annotations

from dataclasses import dataclass

from src.core.attributes.attribute_types import AttributeType
from src.core.characters.class_modifiers import ClassModifiers
from src.core.characters.position import Position
from src.dungeon.enemies.bosses.boss_phase import BossPhase
from src.dungeon.enemies.enemy_archetype import EnemyArchetype


@dataclass(frozen=True)
class BossPhaseConfig:
    """Config de uma fase: phase + skill_ids da fase."""

    phase: BossPhase
    skill_ids: tuple[str, ...]

    @classmethod
    def from_dict(cls, data: dict) -> BossPhaseConfig:
        phase = BossPhase.from_dict(data)
        skill_ids = tuple(data.get("skill_ids", []))
        return cls(phase=phase, skill_ids=skill_ids)


@dataclass(frozen=True)
class BossTemplate:
    """Blueprint de um boss com múltiplas fases."""

    enemy_id: str
    name: str
    tier: int
    archetype: EnemyArchetype
    class_modifiers: ClassModifiers
    base_attributes: dict[AttributeType, int]
    position: Position
    elemental_profile_id: str
    weapon_id: str
    phases: tuple[BossPhaseConfig, ...]
    special_traits: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, data: dict) -> BossTemplate:
        mods = ClassModifiers.from_dict(data["class_modifiers"])
        attrs = {
            AttributeType[k]: v
            for k, v in data["base_attributes"].items()
        }
        phases = tuple(
            BossPhaseConfig.from_dict(p) for p in data["phases"]
        )
        return cls(
            enemy_id=data["enemy_id"],
            name=data["name"],
            tier=int(data["tier"]),
            archetype=EnemyArchetype(data["archetype"].lower()),
            class_modifiers=mods,
            base_attributes=attrs,
            position=Position[data["position"]],
            elemental_profile_id=data.get(
                "elemental_profile_id", "neutral",
            ),
            weapon_id=data.get("weapon_id", ""),
            phases=phases,
            special_traits=tuple(data.get("special_traits", [])),
        )

    def all_skill_ids(self) -> tuple[str, ...]:
        """Retorna todos os skill_ids de todas as fases (sem duplicatas)."""
        seen: set[str] = set()
        result: list[str] = []
        for phase_cfg in self.phases:
            for sid in phase_cfg.skill_ids:
                if sid not in seen:
                    seen.add(sid)
                    result.append(sid)
        return tuple(result)
