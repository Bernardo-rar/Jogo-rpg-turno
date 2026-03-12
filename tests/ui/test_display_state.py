"""Testes para DisplayState — estado mutavel de HP/mana para a UI."""

from __future__ import annotations

import pytest

from src.core.characters.position import Position
from src.core.combat.effect_phase import EffectLogEntry
from src.ui.replay.battle_snapshot import CharacterSnapshot, RoundSnapshot
from src.ui.replay.display_state import DisplayState


def _make_snapshot(
    characters: tuple[CharacterSnapshot, ...],
    round_number: int = 0,
) -> RoundSnapshot:
    return RoundSnapshot(round_number=round_number, characters=characters)


def _make_char(
    name: str = "Gareth",
    current_hp: int = 100,
    max_hp: int = 100,
    current_mana: int = 50,
    max_mana: int = 50,
    is_alive: bool = True,
    is_party: bool = True,
) -> CharacterSnapshot:
    return CharacterSnapshot(
        name=name,
        current_hp=current_hp,
        max_hp=max_hp,
        current_mana=current_mana,
        max_mana=max_mana,
        position=Position.FRONT,
        is_alive=is_alive,
        active_effects=(),
        is_party=is_party,
    )


class TestDisplayStateInit:
    def test_initial_matches_snapshot(self) -> None:
        char = _make_char(current_hp=80, max_hp=100)
        snap = _make_snapshot((char,))
        state = DisplayState(snap)
        result = state.to_round_snapshot(0)
        assert result.characters[0].current_hp == 80
        assert result.characters[0].max_hp == 100

    def test_to_round_snapshot_is_frozen(self) -> None:
        snap = _make_snapshot((_make_char(),))
        state = DisplayState(snap)
        result = state.to_round_snapshot(0)
        with pytest.raises(AttributeError):
            result.round_number = 5  # type: ignore[misc]


class TestApplyDamage:
    def test_reduces_hp(self) -> None:
        snap = _make_snapshot((_make_char(current_hp=100),))
        state = DisplayState(snap)
        state.apply_damage("Gareth", 30)
        result = state.to_round_snapshot(0)
        assert result.characters[0].current_hp == 70

    def test_clamps_to_zero(self) -> None:
        snap = _make_snapshot((_make_char(current_hp=20),))
        state = DisplayState(snap)
        state.apply_damage("Gareth", 50)
        result = state.to_round_snapshot(0)
        assert result.characters[0].current_hp == 0

    def test_kills_character(self) -> None:
        snap = _make_snapshot((_make_char(current_hp=20),))
        state = DisplayState(snap)
        state.apply_damage("Gareth", 20)
        result = state.to_round_snapshot(0)
        assert not result.characters[0].is_alive

    def test_cumulative_damage(self) -> None:
        snap = _make_snapshot((_make_char(current_hp=100),))
        state = DisplayState(snap)
        state.apply_damage("Gareth", 30)
        state.apply_damage("Gareth", 40)
        result = state.to_round_snapshot(0)
        assert result.characters[0].current_hp == 30

    def test_unknown_target_ignored(self) -> None:
        snap = _make_snapshot((_make_char(),))
        state = DisplayState(snap)
        state.apply_damage("NonExistent", 50)
        result = state.to_round_snapshot(0)
        assert result.characters[0].current_hp == 100


class TestApplyHeal:
    def test_increases_hp(self) -> None:
        snap = _make_snapshot((_make_char(current_hp=60, max_hp=100),))
        state = DisplayState(snap)
        state.apply_heal("Gareth", 20)
        result = state.to_round_snapshot(0)
        assert result.characters[0].current_hp == 80

    def test_clamps_to_max(self) -> None:
        snap = _make_snapshot((_make_char(current_hp=90, max_hp=100),))
        state = DisplayState(snap)
        state.apply_heal("Gareth", 50)
        result = state.to_round_snapshot(0)
        assert result.characters[0].current_hp == 100


class TestApplyManaRestore:
    def test_increases_mana(self) -> None:
        snap = _make_snapshot((_make_char(current_mana=20, max_mana=50),))
        state = DisplayState(snap)
        state.apply_mana_restore("Gareth", 15)
        result = state.to_round_snapshot(0)
        assert result.characters[0].current_mana == 35

    def test_clamps_to_max(self) -> None:
        snap = _make_snapshot((_make_char(current_mana=45, max_mana=50),))
        state = DisplayState(snap)
        state.apply_mana_restore("Gareth", 20)
        result = state.to_round_snapshot(0)
        assert result.characters[0].current_mana == 50


class TestSyncFromSnapshot:
    def test_overwrites_all(self) -> None:
        char = _make_char(current_hp=100)
        snap = _make_snapshot((char,))
        state = DisplayState(snap)
        state.apply_damage("Gareth", 60)

        new_char = _make_char(current_hp=80, current_mana=30)
        new_snap = _make_snapshot((new_char,), round_number=1)
        state.sync_from_snapshot(new_snap)
        result = state.to_round_snapshot(1)
        assert result.characters[0].current_hp == 80
        assert result.characters[0].current_mana == 30


class TestActiveEffects:
    def test_add_effect(self) -> None:
        snap = _make_snapshot((_make_char(),))
        state = DisplayState(snap)
        state.apply_add_effect("Gareth", "poison")
        result = state.to_round_snapshot(0)
        assert "poison" in result.characters[0].active_effects

    def test_add_multiple_effects(self) -> None:
        snap = _make_snapshot((_make_char(),))
        state = DisplayState(snap)
        state.apply_add_effect("Gareth", "poison")
        state.apply_add_effect("Gareth", "burn")
        result = state.to_round_snapshot(0)
        assert "poison" in result.characters[0].active_effects
        assert "burn" in result.characters[0].active_effects

    def test_add_effect_unknown_target_ignored(self) -> None:
        snap = _make_snapshot((_make_char(),))
        state = DisplayState(snap)
        state.apply_add_effect("Ghost", "poison")
        result = state.to_round_snapshot(0)
        assert result.characters[0].active_effects == ()

    def test_remove_effects(self) -> None:
        char = _make_char()
        snap = _make_snapshot((char,))
        state = DisplayState(snap)
        state.apply_add_effect("Gareth", "poison")
        state.apply_add_effect("Gareth", "burn")
        state.apply_remove_effects("Gareth")
        result = state.to_round_snapshot(0)
        assert result.characters[0].active_effects == ()

    def test_remove_effects_unknown_target_ignored(self) -> None:
        snap = _make_snapshot((_make_char(),))
        state = DisplayState(snap)
        state.apply_remove_effects("Ghost")  # nao crasha


class TestEffectTicks:
    def test_damage_tick(self) -> None:
        snap = _make_snapshot((_make_char(current_hp=100),))
        state = DisplayState(snap)
        entry = EffectLogEntry(
            round_number=1,
            character_name="Gareth",
            value=10,
            message="Poison deals 10 damage",
        )
        state.apply_effect_ticks([entry])
        result = state.to_round_snapshot(0)
        assert result.characters[0].current_hp == 90

    def test_heal_tick(self) -> None:
        snap = _make_snapshot((_make_char(current_hp=60, max_hp=100),))
        state = DisplayState(snap)
        entry = EffectLogEntry(
            round_number=1,
            character_name="Gareth",
            value=15,
            message="Regen heals 15 HP",
        )
        state.apply_effect_ticks([entry])
        result = state.to_round_snapshot(0)
        assert result.characters[0].current_hp == 75

    def test_skip_entries_ignored(self) -> None:
        snap = _make_snapshot((_make_char(current_hp=100),))
        state = DisplayState(snap)
        entry = EffectLogEntry(
            round_number=1,
            character_name="Gareth",
            value=0,
            message="Stunned",
            is_skip=True,
        )
        state.apply_effect_ticks([entry])
        result = state.to_round_snapshot(0)
        assert result.characters[0].current_hp == 100

    def test_zero_value_ignored(self) -> None:
        snap = _make_snapshot((_make_char(current_hp=100),))
        state = DisplayState(snap)
        entry = EffectLogEntry(
            round_number=1,
            character_name="Gareth",
            value=0,
            message="Something happened",
        )
        state.apply_effect_ticks([entry])
        result = state.to_round_snapshot(0)
        assert result.characters[0].current_hp == 100
