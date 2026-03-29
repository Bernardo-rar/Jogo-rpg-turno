"""Testes para campfire_actions."""

from src.dungeon.map.map_generator import MapGenerator
from src.dungeon.run.campfire_actions import (
    CampfireBuff,
    apply_campfire_buff,
    load_campfire_buffs,
)
from src.dungeon.run.run_state import RunState
from tests.core.test_combat.conftest import _build_char


def _make_state() -> RunState:
    fm = MapGenerator().generate(seed=1)
    party = [_build_char("A"), _build_char("B")]
    return RunState(seed=1, party=party, floor_map=fm)


class TestLoadCampfireBuffs:

    def test_returns_dict(self) -> None:
        buffs = load_campfire_buffs()
        assert isinstance(buffs, dict)
        assert len(buffs) > 0

    def test_each_value_is_campfire_buff(self) -> None:
        buffs = load_campfire_buffs()
        for buff in buffs.values():
            assert isinstance(buff, CampfireBuff)

    def test_regen_has_heal_pct(self) -> None:
        buffs = load_campfire_buffs()
        assert buffs["regen"].heal_pct > 0

    def test_attack_boost_has_buff_stat(self) -> None:
        buffs = load_campfire_buffs()
        assert buffs["attack_boost"].buff_stat == "attack"


class TestApplyCampfireHeal:

    def test_heals_party_members(self) -> None:
        state = _make_state()
        for c in state.party:
            c.take_damage(c.max_hp // 2)
        buffs = load_campfire_buffs()
        result = apply_campfire_buff(state, buffs["regen"])
        assert result["healed"] > 0

    def test_skips_dead_members(self) -> None:
        state = _make_state()
        state.party[0].take_damage(state.party[0].max_hp)
        state.party[1].take_damage(state.party[1].max_hp // 2)
        buffs = load_campfire_buffs()
        result = apply_campfire_buff(state, buffs["regen"])
        assert not state.party[0].is_alive


class TestApplyCampfireBuff:

    def test_buff_returns_stat_info(self) -> None:
        state = _make_state()
        buffs = load_campfire_buffs()
        result = apply_campfire_buff(state, buffs["attack_boost"])
        assert result["buff_stat"] == "attack"
        assert result["buff_value"] == 15

    def test_buff_returns_duration(self) -> None:
        state = _make_state()
        buffs = load_campfire_buffs()
        result = apply_campfire_buff(state, buffs["defense_boost"])
        assert result["duration_rooms"] == 3
