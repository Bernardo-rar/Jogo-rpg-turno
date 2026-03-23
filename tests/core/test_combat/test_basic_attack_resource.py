"""Testes para basic_attack_resource — ganho de recurso ao atacar."""

from __future__ import annotations

from src.core.combat.basic_attack_resource import on_basic_attack
from src.core.items.weapon_loader import load_weapons
from src.core.classes.class_id import ClassId
from src.dungeon.run.party_factory import PartyFactory


def _factory() -> PartyFactory:
    return PartyFactory(weapon_catalog=load_weapons())


class TestOnBasicAttack:

    def test_fighter_gains_ap(self) -> None:
        f = _factory()
        char = f.create(ClassId.FIGHTER, "F")
        initial = char.action_points.current
        on_basic_attack(char)
        assert char.action_points.current == initial + 1

    def test_barbarian_gains_fury(self) -> None:
        f = _factory()
        char = f.create(ClassId.BARBARIAN, "B")
        initial = char.fury_bar.current
        on_basic_attack(char)
        assert char.fury_bar.current == initial + 10

    def test_cleric_gains_holy_power(self) -> None:
        f = _factory()
        char = f.create(ClassId.CLERIC, "C")
        initial = char.holy_power.current
        on_basic_attack(char)
        assert char.holy_power.current == initial + 1

    def test_mage_no_resource(self) -> None:
        f = _factory()
        char = f.create(ClassId.MAGE, "M")
        # Should not raise — just a no-op
        on_basic_attack(char)

    def test_bard_gains_groove(self) -> None:
        f = _factory()
        char = f.create(ClassId.BARD, "Bd")
        initial = char.groove.stacks
        on_basic_attack(char)
        assert char.groove.stacks == initial + 1
