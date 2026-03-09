"""Testes para target_resolver - resolve TargetType em alvos concretos."""

from __future__ import annotations

from src.core.characters.position import Position
from src.core.combat.action_economy import ActionEconomy
from src.core.combat.combat_engine import TurnContext
from src.core.combat.target_resolver import resolve_targets
from src.core.skills.target_type import TargetType

from tests.core.test_combat.conftest import _build_char


def _context(combatant, allies, enemies):
    return TurnContext(
        combatant=combatant, allies=allies, enemies=enemies,
        action_economy=ActionEconomy(), round_number=1,
    )


class TestResolveTargets:
    def test_self_returns_combatant(self) -> None:
        hero = _build_char("Hero")
        ctx = _context(hero, [hero], [_build_char("Enemy")])
        targets = resolve_targets(TargetType.SELF, ctx)
        assert targets == [hero]

    def test_single_ally_returns_first_alive(self) -> None:
        hero = _build_char("Hero")
        ally = _build_char("Ally")
        ctx = _context(hero, [hero, ally], [_build_char("Enemy")])
        targets = resolve_targets(TargetType.SINGLE_ALLY, ctx)
        assert len(targets) == 1
        assert targets[0].is_alive

    def test_single_ally_skips_dead(self) -> None:
        hero = _build_char("Hero")
        dead = _build_char("Dead")
        dead.take_damage(dead.max_hp)
        alive = _build_char("Alive")
        ctx = _context(hero, [dead, alive], [_build_char("E")])
        targets = resolve_targets(TargetType.SINGLE_ALLY, ctx)
        assert targets == [alive]

    def test_single_enemy_prefers_front(self) -> None:
        hero = _build_char("Hero")
        front = _build_char("Front")
        back = _build_char("Back")
        back.change_position(Position.BACK)
        ctx = _context(hero, [hero], [front, back])
        targets = resolve_targets(TargetType.SINGLE_ENEMY, ctx)
        assert targets == [front]

    def test_single_enemy_fallback_to_back(self) -> None:
        hero = _build_char("Hero")
        front = _build_char("Front")
        front.take_damage(front.max_hp)
        back = _build_char("Back")
        back.change_position(Position.BACK)
        ctx = _context(hero, [hero], [front, back])
        targets = resolve_targets(TargetType.SINGLE_ENEMY, ctx)
        assert targets == [back]

    def test_all_allies_returns_only_alive(self) -> None:
        hero = _build_char("Hero")
        dead = _build_char("Dead")
        dead.take_damage(dead.max_hp)
        alive = _build_char("Alive")
        ctx = _context(hero, [hero, dead, alive], [_build_char("E")])
        targets = resolve_targets(TargetType.ALL_ALLIES, ctx)
        assert hero in targets
        assert alive in targets
        assert dead not in targets

    def test_all_enemies_returns_only_alive(self) -> None:
        hero = _build_char("Hero")
        e1 = _build_char("E1")
        e2 = _build_char("E2")
        e2.take_damage(e2.max_hp)
        ctx = _context(hero, [hero], [e1, e2])
        targets = resolve_targets(TargetType.ALL_ENEMIES, ctx)
        assert targets == [e1]
