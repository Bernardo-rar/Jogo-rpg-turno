"""Testes para action_panel — logica de titulos e labels do menu."""

from src.ui.components.action_panel import get_level_title
from src.ui.input.menu_state import MenuLevel


class TestActionPanelTitles:
    def test_action_type_title(self) -> None:
        assert get_level_title(MenuLevel.ACTION_TYPE) == "Choose Action Type"

    def test_specific_action_title(self) -> None:
        assert get_level_title(MenuLevel.SPECIFIC_ACTION) == "Choose Action"

    def test_target_select_title(self) -> None:
        assert get_level_title(MenuLevel.TARGET_SELECT) == "Choose Target"
