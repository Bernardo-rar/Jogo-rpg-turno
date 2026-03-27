"""Testes para help_overlay — dados e estrutura dos keybindings."""

from src.ui.components.help_overlay import KEYBINDINGS


def test_keybindings_not_empty() -> None:
    assert len(KEYBINDINGS) > 0


def test_keybindings_are_tuples_of_two_strings() -> None:
    for entry in KEYBINDINGS:
        assert isinstance(entry, tuple)
        assert len(entry) == 2
        key_label, description = entry
        assert isinstance(key_label, str)
        assert isinstance(description, str)
