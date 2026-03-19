"""Testes para live_display — cria RoundSnapshot de Characters vivos."""

from src.core.effects.buff_factory import create_flat_buff
from src.core.effects.modifiable_stat import ModifiableStat
from src.ui.replay.live_display import create_live_snapshot

from tests.core.test_combat.conftest import _build_char


class TestCreateLiveSnapshot:
    def test_reflects_current_hp(self) -> None:
        hero = _build_char("Hero")
        hero.take_damage(10)
        snap = create_live_snapshot([hero], [], round_number=1)
        char = snap.characters[0]
        assert char.current_hp == hero.current_hp

    def test_shows_death(self) -> None:
        hero = _build_char("Hero")
        hero.take_damage(hero.max_hp + 100)
        snap = create_live_snapshot([hero], [], round_number=1)
        assert snap.characters[0].is_alive is False

    def test_includes_active_effects(self) -> None:
        hero = _build_char("Hero")
        buff = create_flat_buff(ModifiableStat.SPEED, 5, 3)
        hero.effect_manager.add_effect(buff)
        snap = create_live_snapshot([hero], [], round_number=1)
        assert len(snap.characters[0].active_effects) == 1

    def test_party_flag_correct(self) -> None:
        hero = _build_char("Hero")
        goblin = _build_char("Goblin")
        snap = create_live_snapshot([hero], [goblin], round_number=1)
        party_char = next(c for c in snap.characters if c.name == "Hero")
        enemy_char = next(c for c in snap.characters if c.name == "Goblin")
        assert party_char.is_party is True
        assert enemy_char.is_party is False

    def test_all_characters_included(self) -> None:
        party = [_build_char("A"), _build_char("B")]
        enemies = [_build_char("X"), _build_char("Y")]
        snap = create_live_snapshot(party, enemies, round_number=2)
        assert len(snap.characters) == 4
        assert snap.round_number == 2

    def test_mana_reflects_current(self) -> None:
        hero = _build_char("Hero")
        original_mana = hero.current_mana
        hero.spend_mana(5)
        snap = create_live_snapshot([hero], [], round_number=1)
        assert snap.characters[0].current_mana == original_mana - 5
