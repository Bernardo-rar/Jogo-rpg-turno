"""Testes para mapeamento ElementType -> cor RGB."""

from src.core.elements.element_type import ElementType
from src.ui import colors
from src.ui.animations.element_colors import ELEMENT_COLORS, get_element_color


class TestElementColors:
    def test_dict_has_all_10_elements(self) -> None:
        assert len(ELEMENT_COLORS) == len(ElementType)
        for elem in ElementType:
            assert elem in ELEMENT_COLORS

    def test_fire_color_is_warm_orange(self) -> None:
        assert ELEMENT_COLORS[ElementType.FIRE] == colors.ELEMENT_FIRE

    def test_ice_color_is_light_blue(self) -> None:
        assert ELEMENT_COLORS[ElementType.ICE] == colors.ELEMENT_ICE

    def test_get_element_color_returns_mapped_color(self) -> None:
        assert get_element_color(ElementType.FIRE) == colors.ELEMENT_FIRE

    def test_get_element_color_none_returns_default(self) -> None:
        assert get_element_color(None) == colors.DEFAULT_MAGIC_COLOR
