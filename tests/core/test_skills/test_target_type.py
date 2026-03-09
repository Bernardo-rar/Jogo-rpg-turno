"""Testes para TargetType enum."""

from __future__ import annotations

from src.core.skills.target_type import TargetType


class TestTargetType:
    def test_has_self(self) -> None:
        assert TargetType.SELF is not None

    def test_has_single_ally(self) -> None:
        assert TargetType.SINGLE_ALLY is not None

    def test_has_single_enemy(self) -> None:
        assert TargetType.SINGLE_ENEMY is not None

    def test_has_all_allies(self) -> None:
        assert TargetType.ALL_ALLIES is not None

    def test_has_all_enemies(self) -> None:
        assert TargetType.ALL_ENEMIES is not None

    def test_has_five_members(self) -> None:
        assert len(TargetType) == 5
