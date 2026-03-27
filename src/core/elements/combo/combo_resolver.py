"""ComboResolver - orquestra deteccao e resolucao de combos elementais."""

from __future__ import annotations

from dataclasses import dataclass

from src.core.effects.effect import Effect
from src.core.effects.effect_manager import EffectManager
from src.core.elements.combo.combo_ailment_factory import create_combo_ailment
from src.core.elements.combo.combo_detector import ComboDetector
from src.core.elements.element_type import ElementType

MARKER_KEY_PREFIX = "element_marker_"


@dataclass(frozen=True)
class ComboOutcome:
    """Resultado de um combo elemental disparado."""

    combo_name: str
    bonus_damage: int
    ailment: Effect | None


def resolve_combo(
    element: ElementType,
    target_effects: EffectManager,
    combo_detector: ComboDetector | None,
) -> ComboOutcome | None:
    """Detecta e resolve combo elemental, se houver.

    Retorna ComboOutcome se combo disparou, None caso contrario.
    Consome markers e aplica ailment ao target_effects.
    """
    if combo_detector is None:
        return None
    config = combo_detector.check_combo(element, target_effects)
    if config is None:
        return None
    ailment = create_combo_ailment(config.effect)
    if ailment is not None:
        target_effects.add_effect(ailment)
    if config.consumes_markers:
        _consume_markers(config.element_a, config.element_b, target_effects)
    return ComboOutcome(
        combo_name=config.combo_name,
        bonus_damage=config.effect.bonus_damage,
        ailment=ailment,
    )


def _consume_markers(
    element_a: ElementType,
    element_b: ElementType,
    target_effects: EffectManager,
) -> None:
    """Remove markers dos dois elementos envolvidos no combo."""
    target_effects.remove_by_key(f"{MARKER_KEY_PREFIX}{element_a.name}")
    target_effects.remove_by_key(f"{MARKER_KEY_PREFIX}{element_b.name}")
