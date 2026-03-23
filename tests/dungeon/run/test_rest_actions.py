"""Testes para rest_actions."""

from src.dungeon.run.rest_actions import apply_rest_heal, apply_rest_meditate
from tests.core.test_combat.conftest import _build_char


class TestApplyRestHeal:

    def test_heals_alive_members(self) -> None:
        char = _build_char("A")
        char.take_damage(char.max_hp // 2)
        results = apply_rest_heal([char])
        assert results["A"] > 0

    def test_skips_dead_members(self) -> None:
        char = _build_char("A")
        char.take_damage(char.max_hp)
        results = apply_rest_heal([char])
        assert "A" not in results

    def test_does_not_overheal(self) -> None:
        char = _build_char("A")
        # Full HP
        results = apply_rest_heal([char])
        assert results["A"] == 0


class TestApplyRestMeditate:

    def test_restores_mana(self) -> None:
        char = _build_char("A")
        char.spend_mana(char.max_mana // 2)
        results = apply_rest_meditate([char])
        assert results["A"] > 0

    def test_caps_at_max(self) -> None:
        char = _build_char("A")
        # Full mana
        results = apply_rest_meditate([char])
        assert results["A"] == 0

    def test_skips_dead(self) -> None:
        char = _build_char("A")
        char.take_damage(char.max_hp)
        results = apply_rest_meditate([char])
        assert "A" not in results
