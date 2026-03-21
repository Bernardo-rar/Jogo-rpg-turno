"""SkillEffect frozen dataclass - descreve um efeito atomico de uma skill."""

from __future__ import annotations

from dataclasses import dataclass

from src.core.effects.modifiable_stat import ModifiableStat
from src.core.elements.element_type import ElementType
from src.core.skills.skill_effect_type import SkillEffectType

_DEFAULT_BASE_POWER = 0
_DEFAULT_DURATION = 0


@dataclass(frozen=True)
class SkillEffect:
    """Um efeito atomico que uma skill produz (dano, cura, buff, etc)."""

    effect_type: SkillEffectType
    base_power: int = _DEFAULT_BASE_POWER
    element: ElementType | None = None
    stat: ModifiableStat | None = None
    ailment_id: str | None = None
    duration: int = _DEFAULT_DURATION
    mechanic_id: str | None = None
    resource_type: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> SkillEffect:
        """Cria SkillEffect a partir de dict (JSON)."""
        element = _parse_element(data.get("element"))
        stat = _parse_stat(data.get("stat"))
        return cls(
            effect_type=SkillEffectType[str(data["effect_type"])],
            base_power=int(data.get("base_power", _DEFAULT_BASE_POWER)),  # type: ignore[arg-type]
            element=element,
            stat=stat,
            ailment_id=data.get("ailment_id"),  # type: ignore[arg-type]
            duration=int(data.get("duration", _DEFAULT_DURATION)),  # type: ignore[arg-type]
            mechanic_id=data.get("mechanic_id"),  # type: ignore[arg-type]
            resource_type=data.get("resource_type"),  # type: ignore[arg-type]
        )


def _parse_element(raw: object) -> ElementType | None:
    if raw is None:
        return None
    return ElementType[str(raw)]


def _parse_stat(raw: object) -> ModifiableStat | None:
    if raw is None:
        return None
    return ModifiableStat[str(raw)]
