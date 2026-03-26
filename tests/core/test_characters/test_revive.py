"""Testes para Character.revive()."""

from __future__ import annotations

from src.core.classes.class_id import ClassId
from src.core.items.weapon_loader import load_weapons
from src.dungeon.run.party_factory import PartyFactory

_WEAPONS = load_weapons()
_FACTORY = PartyFactory(_WEAPONS)


def _make_char(name: str = "Hero"):
    return _FACTORY.create(ClassId.FIGHTER, name)


class TestRevive:
    def test_revive_dead_character(self) -> None:
        c = _make_char()
        c.take_damage(c.max_hp)
        assert not c.is_alive
        c.revive(0.5)
        assert c.is_alive
        assert c.current_hp == int(c.max_hp * 0.5)

    def test_revive_with_30_percent(self) -> None:
        c = _make_char()
        c.take_damage(c.max_hp)
        c.revive(0.3)
        assert c.current_hp == int(c.max_hp * 0.3)

    def test_revive_alive_does_nothing(self) -> None:
        c = _make_char()
        original_hp = c.current_hp
        c.revive(0.5)
        assert c.current_hp == original_hp

    def test_revive_minimum_1_hp(self) -> None:
        c = _make_char()
        c.take_damage(c.max_hp)
        c.revive(0.001)
        assert c.is_alive
        assert c.current_hp >= 1

    def test_can_heal_after_revive(self) -> None:
        c = _make_char()
        c.take_damage(c.max_hp)
        c.revive(0.3)
        healed = c.heal(50)
        assert healed > 0
