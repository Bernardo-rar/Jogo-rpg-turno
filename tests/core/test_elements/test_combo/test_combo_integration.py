"""Testes de integracao: combo elemental no fluxo de ataque."""

from __future__ import annotations

from src.core.effects.effect_manager import EffectManager
from src.core.elements.combo.combo_config import ComboConfig, ComboEffect
from src.core.elements.combo.combo_detector import ComboDetector
from src.core.elements.combo.combo_resolver import (
    ComboOutcome,
    resolve_combo,
)
from src.core.elements.combo.element_marker import ElementMarker
from src.core.elements.element_type import ElementType


def _make_detector() -> ComboDetector:
    """Cria detector com combo FIRE+ICE para testes."""
    combo = ComboConfig(
        combo_name="Freeze Burst",
        element_a=ElementType.FIRE,
        element_b=ElementType.ICE,
        effect=ComboEffect(
            ailment_id="freeze",
            ailment_duration=3,
            bonus_damage=15,
        ),
    )
    combos = {frozenset({ElementType.FIRE, ElementType.ICE}): combo}
    return ComboDetector(combos=combos)


def test_fire_then_ice_triggers_freeze_burst() -> None:
    """FIRE marker no alvo + ataque ICE deve aplicar freeze."""
    target_effects = EffectManager()
    target_effects.add_effect(ElementMarker(ElementType.FIRE))
    detector = _make_detector()

    outcome = resolve_combo(
        element=ElementType.ICE,
        target_effects=target_effects,
        combo_detector=detector,
    )

    assert outcome is not None
    assert outcome.combo_name == "Freeze Burst"
    assert outcome.bonus_damage == 15
    assert outcome.ailment is not None
    assert target_effects.has_effect("ailment_freeze")


def test_combo_consumes_markers() -> None:
    """Apos combo, markers dos dois elementos devem ser removidos."""
    target_effects = EffectManager()
    target_effects.add_effect(ElementMarker(ElementType.FIRE))
    detector = _make_detector()

    resolve_combo(
        element=ElementType.ICE,
        target_effects=target_effects,
        combo_detector=detector,
    )

    assert not target_effects.has_effect("element_marker_FIRE")
    assert not target_effects.has_effect("element_marker_ICE")


def test_no_combo_first_hit() -> None:
    """Primeiro ataque elemental nao gera combo, apenas adiciona marker."""
    target_effects = EffectManager()
    detector = _make_detector()

    outcome = resolve_combo(
        element=ElementType.FIRE,
        target_effects=target_effects,
        combo_detector=detector,
    )

    assert outcome is None


def test_combo_applies_ailment_to_target_manager() -> None:
    """Ailment do combo deve ser adicionado ao EffectManager do alvo."""
    target_effects = EffectManager()
    target_effects.add_effect(ElementMarker(ElementType.FIRE))
    detector = _make_detector()

    resolve_combo(
        element=ElementType.ICE,
        target_effects=target_effects,
        combo_detector=detector,
    )

    assert target_effects.has_effect("ailment_freeze")


def test_combo_with_dot_ailment() -> None:
    """Combo com DoT (burn) deve aplicar o ailment corretamente."""
    combo = ComboConfig(
        combo_name="Magma Surge",
        element_a=ElementType.FIRE,
        element_b=ElementType.EARTH,
        effect=ComboEffect(
            ailment_id="burn",
            ailment_power=12,
            ailment_duration=4,
            bonus_damage=10,
        ),
    )
    combos = {frozenset({ElementType.FIRE, ElementType.EARTH}): combo}
    detector = ComboDetector(combos=combos)
    target_effects = EffectManager()
    target_effects.add_effect(ElementMarker(ElementType.FIRE))

    outcome = resolve_combo(
        element=ElementType.EARTH,
        target_effects=target_effects,
        combo_detector=detector,
    )

    assert outcome is not None
    assert outcome.combo_name == "Magma Surge"
    assert target_effects.has_effect("ailment_burn")


def test_resolve_combo_returns_none_when_no_detector() -> None:
    """Sem detector, resolve_combo retorna None."""
    target_effects = EffectManager()

    outcome = resolve_combo(
        element=ElementType.FIRE,
        target_effects=target_effects,
        combo_detector=None,
    )

    assert outcome is None
