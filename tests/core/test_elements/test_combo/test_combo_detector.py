"""Testes para ComboDetector - detecta combos elementais via markers."""

from __future__ import annotations

import pytest

from src.core.effects.effect_manager import EffectManager
from src.core.elements.combo.combo_config import ComboConfig, ComboEffect
from src.core.elements.combo.combo_detector import ComboDetector
from src.core.elements.combo.element_marker import ElementMarker
from src.core.elements.element_type import ElementType


@pytest.fixture()
def fire_ice_combo() -> ComboConfig:
    """Combo FIRE + ICE de teste."""
    return ComboConfig(
        combo_name="Freeze Burst",
        element_a=ElementType.FIRE,
        element_b=ElementType.ICE,
        effect=ComboEffect(
            ailment_id="freeze",
            ailment_duration=3,
            bonus_damage=15,
        ),
    )


@pytest.fixture()
def lightning_water_combo() -> ComboConfig:
    """Combo LIGHTNING + WATER de teste."""
    return ComboConfig(
        combo_name="Chain Lightning",
        element_a=ElementType.LIGHTNING,
        element_b=ElementType.WATER,
        effect=ComboEffect(
            ailment_id="paralysis",
            ailment_duration=2,
            bonus_damage=20,
        ),
    )


@pytest.fixture()
def detector(
    fire_ice_combo: ComboConfig,
    lightning_water_combo: ComboConfig,
) -> ComboDetector:
    """Detector com dois combos registrados."""
    combos = {
        frozenset({ElementType.FIRE, ElementType.ICE}): fire_ice_combo,
        frozenset(
            {ElementType.LIGHTNING, ElementType.WATER},
        ): lightning_water_combo,
    }
    return ComboDetector(combos=combos)


def test_no_combo_when_no_markers(detector: ComboDetector) -> None:
    """Sem markers no alvo, nenhum combo deve disparar."""
    target_effects = EffectManager()

    result = detector.check_combo(ElementType.ICE, target_effects)

    assert result is None


def test_combo_detected_when_marker_present(
    detector: ComboDetector,
    fire_ice_combo: ComboConfig,
) -> None:
    """FIRE marker + ataque ICE deve detectar Freeze Burst."""
    target_effects = EffectManager()
    target_effects.add_effect(ElementMarker(ElementType.FIRE))

    result = detector.check_combo(ElementType.ICE, target_effects)

    assert result is fire_ice_combo


def test_combo_order_independent(
    detector: ComboDetector,
    fire_ice_combo: ComboConfig,
) -> None:
    """ICE marker + ataque FIRE deve detectar o mesmo combo."""
    target_effects = EffectManager()
    target_effects.add_effect(ElementMarker(ElementType.ICE))

    result = detector.check_combo(ElementType.FIRE, target_effects)

    assert result is fire_ice_combo


def test_no_combo_for_same_element(detector: ComboDetector) -> None:
    """FIRE marker + ataque FIRE nao deve gerar combo."""
    target_effects = EffectManager()
    target_effects.add_effect(ElementMarker(ElementType.FIRE))

    result = detector.check_combo(ElementType.FIRE, target_effects)

    assert result is None


def test_combo_not_detected_for_unrelated_element(
    detector: ComboDetector,
) -> None:
    """FIRE marker + ataque EARTH nao deve gerar combo (nao registrado)."""
    target_effects = EffectManager()
    target_effects.add_effect(ElementMarker(ElementType.FIRE))

    result = detector.check_combo(ElementType.EARTH, target_effects)

    assert result is None
