"""Testes para event_loader."""

from src.dungeon.events.event_loader import load_events
from src.dungeon.events.event_template import (
    EventChoice,
    EventEffect,
    EventTemplate,
)


class TestLoadEvents:

    def test_returns_dict_of_templates(self) -> None:
        events = load_events()
        assert isinstance(events, dict)
        assert len(events) > 0

    def test_each_value_is_event_template(self) -> None:
        events = load_events()
        for event in events.values():
            assert isinstance(event, EventTemplate)

    def test_mysterious_chest_exists(self) -> None:
        events = load_events()
        assert "mysterious_chest" in events

    def test_event_has_choices(self) -> None:
        events = load_events()
        chest = events["mysterious_chest"]
        assert len(chest.choices) == 3

    def test_choice_has_effects(self) -> None:
        events = load_events()
        chest = events["mysterious_chest"]
        open_choice = chest.choices[0]
        assert len(open_choice.effects) >= 1
        assert isinstance(open_choice.effects[0], EventEffect)

    def test_event_id_matches_key(self) -> None:
        events = load_events()
        for key, event in events.items():
            assert event.event_id == key

    def test_all_choices_have_result_text(self) -> None:
        events = load_events()
        for event in events.values():
            for choice in event.choices:
                assert isinstance(choice.result_text, str)
                assert len(choice.result_text) > 0
