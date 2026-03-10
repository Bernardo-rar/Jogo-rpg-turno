"""Testes para battle_snapshot - dataclasses de snapshot do estado da batalha."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from src.core.characters.position import Position
from src.ui.replay.battle_snapshot import (
    BattleReplay,
    CharacterSnapshot,
    RoundSnapshot,
    snapshot_character,
)

from tests.core.test_combat.conftest import _build_char


class TestCharacterSnapshot:
    def test_is_frozen(self) -> None:
        snap = CharacterSnapshot(
            name="A", current_hp=10, max_hp=20,
            current_mana=5, max_mana=10,
            position=Position.FRONT, is_alive=True,
            active_effects=(), is_party=True,
        )
        with pytest.raises(FrozenInstanceError):
            snap.current_hp = 0  # type: ignore[misc]

    def test_stores_all_fields(self) -> None:
        snap = CharacterSnapshot(
            name="Hero", current_hp=50, max_hp=100,
            current_mana=30, max_mana=60,
            position=Position.BACK, is_alive=True,
            active_effects=("Poison", "Haste"), is_party=False,
        )
        assert snap.name == "Hero"
        assert snap.current_hp == 50
        assert snap.max_hp == 100
        assert snap.position == Position.BACK
        assert snap.active_effects == ("Poison", "Haste")
        assert snap.is_party is False


class TestSnapshotCharacter:
    def test_captures_hp_and_mana(self) -> None:
        char = _build_char("Fighter")
        char.take_damage(10)
        snap = snapshot_character(char, is_party=True)
        assert snap.current_hp == char.current_hp
        assert snap.max_hp == char.max_hp
        assert snap.current_mana == char.current_mana
        assert snap.max_mana == char.max_mana

    def test_captures_name_and_position(self) -> None:
        char = _build_char("Mage")
        snap = snapshot_character(char, is_party=False)
        assert snap.name == "Mage"
        assert snap.position == char.position
        assert snap.is_party is False

    def test_captures_alive_status(self) -> None:
        char = _build_char("Target")
        char.take_damage(char.max_hp + 100)
        snap = snapshot_character(char, is_party=True)
        assert snap.is_alive is False

    def test_captures_active_effect_names(self) -> None:
        char = _build_char("Buffed")
        from src.core.effects.buff_factory import create_flat_buff
        from src.core.effects.modifiable_stat import ModifiableStat
        buff = create_flat_buff(ModifiableStat.SPEED, 5, 3)
        char.effect_manager.add_effect(buff)
        snap = snapshot_character(char, is_party=True)
        assert len(snap.active_effects) == 1
        assert "Speed" in snap.active_effects[0]


class TestRoundSnapshot:
    def test_is_frozen(self) -> None:
        snap = RoundSnapshot(round_number=1, characters=())
        with pytest.raises(FrozenInstanceError):
            snap.round_number = 2  # type: ignore[misc]

    def test_holds_character_snapshots(self) -> None:
        c1 = CharacterSnapshot(
            name="A", current_hp=10, max_hp=20,
            current_mana=5, max_mana=10,
            position=Position.FRONT, is_alive=True,
            active_effects=(), is_party=True,
        )
        snap = RoundSnapshot(round_number=3, characters=(c1,))
        assert snap.round_number == 3
        assert len(snap.characters) == 1
