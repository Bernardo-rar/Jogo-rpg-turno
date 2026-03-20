"""Mapeamento ElementType -> cor RGB para animacoes."""

from __future__ import annotations

from src.core.elements.element_type import ElementType
from src.ui import colors

ELEMENT_COLORS: dict[ElementType, tuple] = {
    ElementType.FIRE: colors.ELEMENT_FIRE,
    ElementType.WATER: colors.ELEMENT_WATER,
    ElementType.ICE: colors.ELEMENT_ICE,
    ElementType.LIGHTNING: colors.ELEMENT_LIGHTNING,
    ElementType.EARTH: colors.ELEMENT_EARTH,
    ElementType.HOLY: colors.ELEMENT_HOLY,
    ElementType.DARKNESS: colors.ELEMENT_DARKNESS,
    ElementType.CELESTIAL: colors.ELEMENT_CELESTIAL,
    ElementType.PSYCHIC: colors.ELEMENT_PSYCHIC,
    ElementType.FORCE: colors.ELEMENT_FORCE,
}


def get_element_color(element: ElementType | None) -> tuple:
    """Retorna cor RGB para o elemento, ou DEFAULT_MAGIC_COLOR se None."""
    if element is None:
        return colors.DEFAULT_MAGIC_COLOR
    return ELEMENT_COLORS.get(element, colors.DEFAULT_MAGIC_COLOR)
