"""Testes para ElementMarker - marker temporario de elemento no alvo."""

from __future__ import annotations

from src.core.effects.effect_category import EffectCategory
from src.core.elements.combo.element_marker import ElementMarker
from src.core.elements.element_type import ElementType


def test_marker_has_correct_stacking_key() -> None:
    """Stacking key deve conter o nome do elemento."""
    marker = ElementMarker(element=ElementType.FIRE)

    assert marker.stacking_key == "element_marker_FIRE"


def test_marker_expires_after_ticks() -> None:
    """Marker dura 1 round completo (2 ticks = expira apos tick 2)."""
    marker = ElementMarker(element=ElementType.ICE)

    marker.tick()
    assert not marker.is_expired

    marker.tick()
    assert marker.is_expired


def test_marker_name_contains_element() -> None:
    """Nome legivel deve conter o nome do elemento."""
    marker = ElementMarker(element=ElementType.LIGHTNING)

    assert "LIGHTNING" in marker.name


def test_marker_category_is_ailment() -> None:
    """Categoria deve ser AILMENT para nao conflitar com buffs/debuffs."""
    marker = ElementMarker(element=ElementType.WATER)

    assert marker.category == EffectCategory.AILMENT


def test_marker_exposes_element_property() -> None:
    """Propriedade element retorna o ElementType original."""
    marker = ElementMarker(element=ElementType.EARTH)

    assert marker.element == ElementType.EARTH


def test_marker_tick_returns_empty_result() -> None:
    """Marker nao causa dano, cura, ou efeitos colaterais."""
    marker = ElementMarker(element=ElementType.FIRE)

    result = marker.tick()

    assert result.damage == 0
    assert result.healing == 0
    assert not result.skip_turn
