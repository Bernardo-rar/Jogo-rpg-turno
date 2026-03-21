"""Skill frozen dataclass - descreve uma habilidade do jogo."""

from __future__ import annotations

from dataclasses import dataclass

from src.core.combat.action_economy import ActionType
from src.core.skills.resource_cost import ResourceCost
from src.core.skills.skill_effect import SkillEffect
from src.core.skills.target_type import TargetType

_DEFAULT_COOLDOWN = 0
_DEFAULT_STAMINA = 0
_DEFAULT_LEVEL = 1


@dataclass(frozen=True)
class Skill:
    """Habilidade equipavel com custo, efeitos e cooldown."""

    skill_id: str
    name: str
    mana_cost: int
    action_type: ActionType
    target_type: TargetType
    effects: tuple[SkillEffect, ...]
    slot_cost: int
    cooldown_turns: int = _DEFAULT_COOLDOWN
    stamina_cost: int = _DEFAULT_STAMINA
    required_level: int = _DEFAULT_LEVEL
    description: str = ""
    class_id: str = ""
    resource_costs: tuple[ResourceCost, ...] = ()
    reaction_trigger: str = ""
    reaction_mode: str = ""

    @classmethod
    def from_dict(cls, skill_id: str, data: dict[str, object]) -> Skill:
        """Cria Skill a partir de dict (JSON)."""
        raw_effects = data.get("effects", [])
        effects = tuple(
            SkillEffect.from_dict(e) for e in raw_effects  # type: ignore[union-attr]
        )
        resource_costs = _parse_resource_costs(data.get("resource_costs"))
        return cls(
            skill_id=skill_id,
            name=str(data["name"]),
            mana_cost=int(data["mana_cost"]),  # type: ignore[arg-type]
            action_type=ActionType[str(data["action_type"])],
            target_type=TargetType[str(data["target_type"])],
            effects=effects,
            slot_cost=int(data["slot_cost"]),  # type: ignore[arg-type]
            cooldown_turns=int(data.get("cooldown_turns", _DEFAULT_COOLDOWN)),  # type: ignore[arg-type]
            stamina_cost=int(data.get("stamina_cost", _DEFAULT_STAMINA)),  # type: ignore[arg-type]
            required_level=int(data.get("required_level", _DEFAULT_LEVEL)),  # type: ignore[arg-type]
            description=str(data.get("description", "")),
            class_id=str(data.get("class_id", "")),
            resource_costs=resource_costs,
            reaction_trigger=str(data.get("reaction_trigger", "")),
            reaction_mode=str(data.get("reaction_mode", "")),
        )


def _parse_resource_costs(
    raw: object,
) -> tuple[ResourceCost, ...]:
    if not raw:
        return ()
    return tuple(ResourceCost.from_dict(rc) for rc in raw)  # type: ignore[union-attr]
