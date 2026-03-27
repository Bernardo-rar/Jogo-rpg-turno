"""Factory para criar ailments a partir de ComboEffect config."""

from __future__ import annotations

from typing import Callable

from src.core.effects.ailments.ailment_factory import (
    create_burn,
    create_cold,
    create_confusion,
    create_freeze,
    create_paralysis,
    create_scorch,
)
from src.core.effects.effect import Effect
from src.core.elements.combo.combo_config import ComboEffect

DEFAULT_COLD_REDUCTION = 25.0


def _create_freeze(effect: ComboEffect) -> Effect:
    return create_freeze(duration=effect.ailment_duration)


def _create_burn(effect: ComboEffect) -> Effect:
    return create_burn(
        damage_per_tick=effect.ailment_power,
        duration=effect.ailment_duration,
    )


def _create_paralysis(effect: ComboEffect) -> Effect:
    return create_paralysis(duration=effect.ailment_duration)


def _create_cold(effect: ComboEffect) -> Effect:
    reduction = effect.ailment_power or DEFAULT_COLD_REDUCTION
    return create_cold(
        duration=effect.ailment_duration,
        reduction_percent=float(reduction),
    )


def _create_scorch(effect: ComboEffect) -> Effect:
    return create_scorch(
        damage_per_tick=effect.ailment_power,
        duration=effect.ailment_duration,
    )


def _create_confusion(effect: ComboEffect) -> Effect:
    return create_confusion(duration=effect.ailment_duration)


_COMBO_AILMENT_FACTORIES: dict[
    str, Callable[[ComboEffect], Effect],
] = {
    "freeze": _create_freeze,
    "burn": _create_burn,
    "paralysis": _create_paralysis,
    "cold": _create_cold,
    "scorch": _create_scorch,
    "confusion": _create_confusion,
}


def create_combo_ailment(effect: ComboEffect) -> Effect | None:
    """Cria ailment a partir de ComboEffect. None se ailment_id vazio."""
    if not effect.ailment_id:
        return None
    factory = _COMBO_AILMENT_FACTORIES.get(effect.ailment_id)
    if factory is None:
        return None
    return factory(effect)
