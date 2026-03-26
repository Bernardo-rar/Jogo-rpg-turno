"""Testes para Reckless Stance do Barbarian."""

from __future__ import annotations

from src.core.characters.class_resource_snapshot import ResourceDisplayType
from src.core.classes.class_id import ClassId
from src.core.items.weapon_loader import load_weapons
from src.dungeon.run.party_factory import PartyFactory

_WEAPONS = load_weapons()
_FACTORY = PartyFactory(_WEAPONS)


def _make_barbarian(name: str = "Barb"):
    return _FACTORY.create(ClassId.BARBARIAN, name)


class TestRecklessToggle:
    def test_starts_off(self) -> None:
        barb = _make_barbarian()
        assert not barb.is_reckless

    def test_toggle_on(self) -> None:
        barb = _make_barbarian()
        barb.toggle_reckless()
        assert barb.is_reckless

    def test_toggle_off_again(self) -> None:
        barb = _make_barbarian()
        barb.toggle_reckless()
        barb.toggle_reckless()
        assert not barb.is_reckless


class TestRecklessMultipliers:
    def test_reckless_increases_attack(self) -> None:
        barb = _make_barbarian()
        base_atk = barb.physical_attack
        barb.toggle_reckless()
        assert barb.physical_attack > base_atk

    def test_reckless_decreases_physical_defense(self) -> None:
        barb = _make_barbarian()
        base_def = barb.physical_defense
        barb.toggle_reckless()
        assert barb.physical_defense < base_def

    def test_reckless_decreases_magical_defense(self) -> None:
        barb = _make_barbarian()
        base_def = barb.magical_defense
        barb.toggle_reckless()
        assert barb.magical_defense < base_def

    def test_normal_defense_restored(self) -> None:
        barb = _make_barbarian()
        base_def = barb.physical_defense
        barb.toggle_reckless()
        barb.toggle_reckless()
        assert barb.physical_defense == base_def


class TestRecklessSnapshot:
    def test_snapshot_shows_reckless_toggle(self) -> None:
        barb = _make_barbarian()
        snaps = barb.get_resource_snapshots()
        assert len(snaps) == 2
        reckless_snap = snaps[1]
        assert reckless_snap.name == "Reckless"
        assert reckless_snap.display_type == ResourceDisplayType.TOGGLE
        assert reckless_snap.label == "OFF"

    def test_snapshot_active_when_reckless(self) -> None:
        barb = _make_barbarian()
        barb.toggle_reckless()
        snaps = barb.get_resource_snapshots()
        reckless_snap = snaps[1]
        assert reckless_snap.label == "ACTIVE"
        assert reckless_snap.current == 1
