"""Tests for ClassResourceSnapshot and ResourceDisplayType."""

from __future__ import annotations

import pytest

from src.core.characters.class_resource_snapshot import (
    ClassResourceSnapshot,
    ResourceDisplayType,
)


class TestResourceDisplayType:
    def test_has_bar(self) -> None:
        assert ResourceDisplayType.BAR is not None

    def test_has_counter(self) -> None:
        assert ResourceDisplayType.COUNTER is not None

    def test_has_toggle(self) -> None:
        assert ResourceDisplayType.TOGGLE is not None

    def test_has_three_members(self) -> None:
        assert len(ResourceDisplayType) == 3


class TestClassResourceSnapshot:
    def test_create_bar_resource(self) -> None:
        snap = ClassResourceSnapshot(
            name="Fury",
            display_type=ResourceDisplayType.BAR,
            current=50, maximum=100,
            color=(220, 50, 30),
        )
        assert snap.name == "Fury"
        assert snap.display_type == ResourceDisplayType.BAR
        assert snap.current == 50
        assert snap.maximum == 100
        assert snap.color == (220, 50, 30)
        assert snap.label == ""

    def test_create_counter_resource(self) -> None:
        snap = ClassResourceSnapshot(
            name="AP",
            display_type=ResourceDisplayType.COUNTER,
            current=3, maximum=10,
            color=(255, 200, 50),
        )
        assert snap.display_type == ResourceDisplayType.COUNTER

    def test_create_toggle_with_label(self) -> None:
        snap = ClassResourceSnapshot(
            name="Stance",
            display_type=ResourceDisplayType.TOGGLE,
            current=1, maximum=1,
            color=(255, 200, 50),
            label="Offensive",
        )
        assert snap.label == "Offensive"
        assert snap.current == 1

    def test_is_frozen(self) -> None:
        snap = ClassResourceSnapshot(
            name="Fury",
            display_type=ResourceDisplayType.BAR,
            current=50, maximum=100,
            color=(220, 50, 30),
        )
        with pytest.raises(AttributeError):
            snap.current = 99  # type: ignore[misc]
