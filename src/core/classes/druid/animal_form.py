from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path

ANIMAL_FORM_DATA_PATH = "data/classes/druid_forms.json"


class AnimalForm(Enum):
    """Formas animais do Druida."""

    HUMANOID = auto()
    BEAR = auto()
    WOLF = auto()
    EAGLE = auto()
    SERPENT = auto()


@dataclass(frozen=True)
class AnimalFormModifier:
    """Multiplicadores de stats por forma animal."""

    phys_atk_multiplier: float
    mag_atk_multiplier: float
    phys_def_multiplier: float
    mag_def_multiplier: float
    speed_multiplier: float
    hp_regen_multiplier: float


def load_animal_form_modifiers(
    filepath: str = ANIMAL_FORM_DATA_PATH,
) -> dict[AnimalForm, AnimalFormModifier]:
    """Carrega modificadores de forma animal do JSON."""
    with open(Path(filepath), encoding="utf-8") as f:
        data = json.load(f)
    return {
        AnimalForm[name]: AnimalFormModifier(**values)
        for name, values in data.items()
    }
