"""Testes para MenuLevel e MenuOption — tipos de dados do menu."""

import pytest

from src.ui.input.menu_state import MenuLevel, MenuOption


class TestMenuLevel:
    def test_has_three_levels(self):
        assert len(MenuLevel) == 3

    def test_action_type_is_first(self):
        levels = list(MenuLevel)
        assert levels[0] == MenuLevel.ACTION_TYPE


class TestMenuOption:
    def test_is_frozen(self):
        opt = MenuOption(key=1, label="Attack")
        with pytest.raises(AttributeError):
            opt.key = 2  # type: ignore[misc]

    def test_defaults_to_available(self):
        opt = MenuOption(key=1, label="Attack")
        assert opt.available is True
        assert opt.reason == ""

    def test_unavailable_with_reason(self):
        opt = MenuOption(key=2, label="Fireball", available=False, reason="Cooldown: 2")
        assert opt.available is False
        assert opt.reason == "Cooldown: 2"
