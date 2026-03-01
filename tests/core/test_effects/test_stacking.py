"""Testes para StackingPolicy enum."""

from src.core.effects.stacking import StackingPolicy


class TestStackingPolicy:
    def test_has_replace(self):
        assert StackingPolicy.REPLACE is not None

    def test_has_stack(self):
        assert StackingPolicy.STACK is not None

    def test_has_refresh(self):
        assert StackingPolicy.REFRESH is not None
