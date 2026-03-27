"""ComboConfig - configuracao data-driven de combos elementais."""

from __future__ import annotations

import json
from dataclasses import dataclass

from src.core._paths import resolve_data_path
from src.core.elements.element_type import ElementType

COMBO_DATA_PATH = "data/elements/elemental_combos.json"


@dataclass(frozen=True)
class ComboEffect:
    """Efeito produzido por um combo elemental."""

    ailment_id: str = ""
    ailment_power: int = 0
    ailment_duration: int = 0
    bonus_damage: int = 0


@dataclass(frozen=True)
class ComboConfig:
    """Configuracao de um combo elemental (par de elementos)."""

    combo_name: str
    element_a: ElementType
    element_b: ElementType
    effect: ComboEffect
    consumes_markers: bool = True

    @classmethod
    def from_dict(cls, data: dict) -> ComboConfig:
        """Cria ComboConfig a partir de dict do JSON."""
        effect_data = data.get("effect", {})
        effect = ComboEffect(
            ailment_id=effect_data.get("ailment_id", ""),
            ailment_power=effect_data.get("ailment_power", 0),
            ailment_duration=effect_data.get("ailment_duration", 0),
            bonus_damage=effect_data.get("bonus_damage", 0),
        )
        return cls(
            combo_name=data["combo_name"],
            element_a=ElementType[data["element_a"]],
            element_b=ElementType[data["element_b"]],
            effect=effect,
            consumes_markers=data.get("consumes_markers", True),
        )


def load_combo_configs(
    filepath: str = COMBO_DATA_PATH,
) -> dict[frozenset[ElementType], ComboConfig]:
    """Carrega configuracoes de combos elementais do JSON."""
    with open(resolve_data_path(filepath), encoding="utf-8") as f:
        data = json.load(f)
    return _parse_combo_list(data)


def _parse_combo_list(
    data: list[dict],
) -> dict[frozenset[ElementType], ComboConfig]:
    """Converte lista de dicts para dict com chave frozenset."""
    combos: dict[frozenset[ElementType], ComboConfig] = {}
    for raw in data:
        config = ComboConfig.from_dict(raw)
        key = frozenset({config.element_a, config.element_b})
        combos[key] = config
    return combos
