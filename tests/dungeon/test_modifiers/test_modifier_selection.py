"""Testes para ModifierSelection — logica de selecao de modifiers."""

from random import Random

from src.dungeon.modifiers.run_modifier import (
    ModifierCategory,
    ModifierEffect,
    RunModifier,
)
from src.dungeon.run.modifier_selection import ModifierSelection


def _make_modifier(modifier_id: str) -> RunModifier:
    return RunModifier(
        modifier_id=modifier_id,
        name=modifier_id.capitalize(),
        description=f"Desc {modifier_id}",
        category=ModifierCategory.DIFFICULTY,
        effect=ModifierEffect(),
    )


def _pool(count: int) -> list[RunModifier]:
    return [_make_modifier(f"mod_{i}") for i in range(count)]


class TestModifierSelectionOffered:

    def test_offered_samples_n_from_pool(self) -> None:
        pool = _pool(10)
        sel = ModifierSelection(pool, rng=Random(1), count=3)
        assert len(sel.offered) == 3
        for mod in sel.offered:
            assert mod in pool

    def test_offered_clamps_to_pool_size(self) -> None:
        pool = _pool(2)
        sel = ModifierSelection(pool, rng=Random(1), count=5)
        assert len(sel.offered) == 2


class TestModifierSelectionToggle:

    def test_toggle_selects_and_deselects(self) -> None:
        pool = _pool(5)
        sel = ModifierSelection(pool, rng=Random(1), count=3)
        sel.toggle(0)
        assert len(sel.selected) == 1
        sel.toggle(0)
        assert len(sel.selected) == 0

    def test_toggle_invalid_index_is_noop(self) -> None:
        pool = _pool(5)
        sel = ModifierSelection(pool, rng=Random(1), count=3)
        sel.toggle(-1)
        sel.toggle(99)
        assert len(sel.selected) == 0


class TestModifierSelectionSelected:

    def test_selected_returns_only_active(self) -> None:
        pool = _pool(5)
        sel = ModifierSelection(pool, rng=Random(1), count=3)
        sel.toggle(0)
        sel.toggle(2)
        result = sel.selected
        assert len(result) == 2
        assert result[0] == sel.offered[0]
        assert result[1] == sel.offered[2]

    def test_selected_empty_when_none_toggled(self) -> None:
        pool = _pool(5)
        sel = ModifierSelection(pool, rng=Random(1), count=3)
        assert sel.selected == []


class TestModifierSelectionDeterminism:

    def test_deterministic_with_same_seed(self) -> None:
        pool = _pool(10)
        sel_a = ModifierSelection(pool, rng=Random(42), count=3)
        sel_b = ModifierSelection(pool, rng=Random(42), count=3)
        assert sel_a.offered == sel_b.offered

    def test_different_seed_different_offering(self) -> None:
        pool = _pool(10)
        sel_a = ModifierSelection(pool, rng=Random(1), count=3)
        sel_b = ModifierSelection(pool, rng=Random(99), count=3)
        assert sel_a.offered != sel_b.offered
