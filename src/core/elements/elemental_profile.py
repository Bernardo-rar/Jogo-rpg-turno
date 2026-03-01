"""ElementalProfile - perfil de fraquezas e resistencias elementais."""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from src.core._paths import resolve_data_path
from src.core.elements.element_type import ElementType

NEUTRAL_MULTIPLIER = 1.0
IMMUNE_MULTIPLIER = 0.0
PROFILES_DATA_PATH = "data/elements/elemental_profiles.json"


@dataclass(frozen=True)
class ElementalProfile:
    """Perfil imutavel de resistencias/fraquezas elementais.

    Multiplier: 0.0=immune, 0.5=resistant, 1.0=neutral, 1.5=weak, 2.0=very weak.
    Elementos nao listados sao tratados como neutros (1.0).
    """

    resistances: dict[ElementType, float] = field(default_factory=dict)

    def get_multiplier(self, element: ElementType) -> float:
        """Retorna multiplicador para o elemento. 1.0 se nao configurado."""
        return self.resistances.get(element, NEUTRAL_MULTIPLIER)

    def is_weak_to(self, element: ElementType) -> bool:
        """True se multiplicador > 1.0."""
        return self.get_multiplier(element) > NEUTRAL_MULTIPLIER

    def is_resistant_to(self, element: ElementType) -> bool:
        """True se multiplicador < 1.0."""
        return self.get_multiplier(element) < NEUTRAL_MULTIPLIER

    def is_immune_to(self, element: ElementType) -> bool:
        """True se multiplicador <= 0.0."""
        return self.get_multiplier(element) <= IMMUNE_MULTIPLIER


def create_profile(
    resistances: dict[ElementType, float],
) -> ElementalProfile:
    """Cria ElementalProfile a partir de dict de resistencias."""
    return ElementalProfile(resistances=resistances)


def load_profiles(
    filepath: str = PROFILES_DATA_PATH,
) -> dict[str, ElementalProfile]:
    """Carrega profiles nomeados do JSON."""
    with open(resolve_data_path(filepath), encoding="utf-8") as f:
        data = json.load(f)
    return {
        name: _parse_profile(raw)
        for name, raw in data.items()
    }


def _parse_profile(raw: dict[str, float]) -> ElementalProfile:
    """Converte dict string->float para ElementalProfile."""
    resistances = {
        ElementType[key]: value
        for key, value in raw.items()
    }
    return ElementalProfile(resistances=resistances)
