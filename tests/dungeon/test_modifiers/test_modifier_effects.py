"""Testes para aggregate_modifiers."""

import pytest

from src.dungeon.modifiers.modifier_effects import aggregate_modifiers
from src.dungeon.modifiers.run_modifier import (
    ModifierCategory,
    ModifierEffect,
    RunModifier,
)

NEUTRAL = ModifierEffect()


def _make_modifier(effect: ModifierEffect) -> RunModifier:
    """Cria um RunModifier genérico com o effect dado."""
    return RunModifier(
        modifier_id="test",
        name="Test",
        description="test",
        category=ModifierCategory.DIFFICULTY,
        effect=effect,
    )


class TestAggregateModifiers:

    def test_empty_modifiers_returns_neutral(self) -> None:
        # Act
        result = aggregate_modifiers([])

        # Assert
        assert result == NEUTRAL

    def test_single_modifier_returns_its_effect(self) -> None:
        # Arrange
        effect = ModifierEffect(damage_taken_mult=1.15, gold_mult=1.15)
        modifier = _make_modifier(effect)

        # Act
        result = aggregate_modifiers([modifier])

        # Assert
        assert result.damage_taken_mult == pytest.approx(1.15)
        assert result.gold_mult == pytest.approx(1.15)

    def test_multiple_modifiers_multiply(self) -> None:
        # Arrange
        mod_a = _make_modifier(ModifierEffect(gold_mult=1.15))
        mod_b = _make_modifier(ModifierEffect(gold_mult=1.2))

        # Act
        result = aggregate_modifiers([mod_a, mod_b])

        # Assert — 1.15 * 1.2 = 1.38
        assert result.gold_mult == pytest.approx(1.38)

    def test_start_hp_takes_minimum(self) -> None:
        # Arrange
        mod_a = _make_modifier(ModifierEffect(start_hp_pct=0.7))
        mod_b = _make_modifier(ModifierEffect(start_hp_pct=0.85))

        # Act
        result = aggregate_modifiers([mod_a, mod_b])

        # Assert — pega o mais restritivo (menor)
        assert result.start_hp_pct == pytest.approx(0.7)

    def test_score_multiplies_all(self) -> None:
        # Arrange
        mod_a = _make_modifier(ModifierEffect(score_mult=1.1))
        mod_b = _make_modifier(ModifierEffect(score_mult=1.2))

        # Act
        result = aggregate_modifiers([mod_a, mod_b])

        # Assert — 1.1 * 1.2 = 1.32
        assert result.score_mult == pytest.approx(1.32)
