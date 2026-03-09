"""ConsumableEffect frozen dataclass - descreve um efeito atomico de um consumivel."""

from __future__ import annotations

from dataclasses import dataclass

from src.core.effects.modifiable_stat import ModifiableStat
from src.core.elements.element_type import ElementType
from src.core.items.consumable_effect_type import ConsumableEffectType

_DEFAULT_BASE_POWER = 0
_DEFAULT_DURATION = 0


@dataclass(frozen=True)
class ConsumableEffect:
    """Um efeito atomico que um consumivel produz (cura, dano, buff, etc)."""

    effect_type: ConsumableEffectType
    base_power: int = _DEFAULT_BASE_POWER
    element: ElementType | None = None
    stat: ModifiableStat | None = None
    duration: int = _DEFAULT_DURATION

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> ConsumableEffect:
        """Cria ConsumableEffect a partir de dict (JSON)."""
        return cls(
            effect_type=ConsumableEffectType[str(data["effect_type"])],
            base_power=int(data.get("base_power", _DEFAULT_BASE_POWER)),  # type: ignore[arg-type]
            element=_parse_element(data.get("element")),
            stat=_parse_stat(data.get("stat")),
            duration=int(data.get("duration", _DEFAULT_DURATION)),  # type: ignore[arg-type]
        )


def _parse_element(raw: object) -> ElementType | None:
    if raw is None:
        return None
    return ElementType[str(raw)]


def _parse_stat(raw: object) -> ModifiableStat | None:
    if raw is None:
        return None
    return ModifiableStat[str(raw)]
