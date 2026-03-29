"""Tests for SynergyManager — partner/group/commander tracking."""

import pytest

from src.core.combat.synergy.synergy_config import (
    CommanderAuraConfig,
    DeathEffect,
    LastSurvivorConfig,
    SynergyBinding,
    SynergyConfig,
    SynergyRole,
    SynergyType,
)
from src.core.combat.synergy.synergy_manager import SynergyManager

from tests.core.test_combat.conftest import _build_char as _make_char


def _pair_synergy() -> SynergyConfig:
    healer_role = SynergyRole(
        role_key="healer",
        on_partner_death_buffs=(
            DeathEffect(stat="HEALING_RECEIVED", percent=30.0, duration=999),
        ),
    )
    dps_role = SynergyRole(
        role_key="dps",
        on_partner_death_buffs=(
            DeathEffect(stat="PHYSICAL_ATTACK", percent=25.0, duration=3),
            DeathEffect(stat="PHYSICAL_DEFENSE", percent=-20.0, duration=3),
        ),
    )
    return SynergyConfig(
        synergy_id="healer_dps",
        synergy_type=SynergyType.PAIR,
        roles=(healer_role, dps_role),
    )


def _pack_synergy() -> SynergyConfig:
    return SynergyConfig(
        synergy_id="pack_tactics",
        synergy_type=SynergyType.GROUP,
        pack_same_target_bonus_pct=15.0,
        last_survivor=LastSurvivorConfig(
            atk_bonus_pct=50.0, speed_bonus_pct=30.0, duration=3,
        ),
    )


def _commander_synergy() -> SynergyConfig:
    return SynergyConfig(
        synergy_id="commander_aura",
        synergy_type=SynergyType.COMMANDER,
        commander_aura=CommanderAuraConfig(
            atk_bonus_pct=10.0, def_bonus_pct=10.0,
        ),
        commander_death_debuff=DeathEffect(
            stat="PHYSICAL_ATTACK", percent=-15.0, duration=3,
        ),
    )


class TestSynergyManagerPair:

    def test_get_partner_returns_partner(self) -> None:
        synergies = {"healer_dps": _pair_synergy()}
        bindings = [
            SynergyBinding("Healer", "healer_dps", "healer"),
            SynergyBinding("DPS", "healer_dps", "dps"),
        ]
        chars = [_make_char("Healer"), _make_char("DPS")]
        mgr = SynergyManager(synergies, bindings, chars)
        assert mgr.get_partner("Healer") == "DPS"
        assert mgr.get_partner("DPS") == "Healer"

    def test_get_partner_returns_none_for_unbound(self) -> None:
        mgr = SynergyManager({}, [], [])
        assert mgr.get_partner("Nobody") is None

    def test_on_death_applies_partner_buffs(self) -> None:
        synergies = {"healer_dps": _pair_synergy()}
        bindings = [
            SynergyBinding("Healer", "healer_dps", "healer"),
            SynergyBinding("DPS", "healer_dps", "dps"),
        ]
        healer = _make_char("Healer")
        dps = _make_char("DPS")
        mgr = SynergyManager(synergies, bindings, [healer, dps])
        # Healer dies -> DPS gets frenzy buffs
        events = mgr.on_death("Healer", round_number=1)
        assert len(events) > 0
        assert dps.effect_manager.active_effects


class TestSynergyManagerGroup:

    def test_get_group_members(self) -> None:
        synergies = {"pack": _pack_synergy()}
        bindings = [
            SynergyBinding("Wolf1", "pack"),
            SynergyBinding("Wolf2", "pack"),
            SynergyBinding("Wolf3", "pack"),
        ]
        chars = [
            _make_char("Wolf1"), _make_char("Wolf2"),
            _make_char("Wolf3"),
        ]
        mgr = SynergyManager(synergies, bindings, chars)
        members = mgr.get_group_members("Wolf1")
        assert len(members) == 3

    def test_last_survivor_buff_on_second_to_last_death(self) -> None:
        synergies = {"pack": _pack_synergy()}
        bindings = [
            SynergyBinding("W1", "pack"),
            SynergyBinding("W2", "pack"),
        ]
        w1 = _make_char("W1")
        w2 = _make_char("W2")
        mgr = SynergyManager(synergies, bindings, [w1, w2])
        w1.take_damage(w1.current_hp)
        events = mgr.on_death("W1", round_number=1)
        # W2 is last survivor, should get buff
        assert w2.effect_manager.active_effects
        assert len(events) > 0


class TestSynergyManagerCommander:

    def test_is_commander(self) -> None:
        synergies = {"cmd": _commander_synergy()}
        bindings = [
            SynergyBinding("Commander", "cmd", "commander"),
            SynergyBinding("Soldier", "cmd", "follower"),
        ]
        chars = [_make_char("Commander"), _make_char("Soldier")]
        mgr = SynergyManager(synergies, bindings, chars)
        assert mgr.is_commander("Commander")
        assert not mgr.is_commander("Soldier")

    def test_commander_death_debuffs_followers(self) -> None:
        synergies = {"cmd": _commander_synergy()}
        bindings = [
            SynergyBinding("Commander", "cmd", "commander"),
            SynergyBinding("Soldier", "cmd", "follower"),
        ]
        commander = _make_char("Commander")
        soldier = _make_char("Soldier")
        mgr = SynergyManager(synergies, bindings, [commander, soldier])
        commander.take_damage(commander.current_hp)
        events = mgr.on_death("Commander", round_number=1)
        assert soldier.effect_manager.active_effects
        assert len(events) > 0

    def test_follower_death_no_commander_debuff(self) -> None:
        synergies = {"cmd": _commander_synergy()}
        bindings = [
            SynergyBinding("Commander", "cmd", "commander"),
            SynergyBinding("Soldier", "cmd", "follower"),
        ]
        commander = _make_char("Commander")
        soldier = _make_char("Soldier")
        mgr = SynergyManager(synergies, bindings, [commander, soldier])
        soldier.take_damage(soldier.current_hp)
        events = mgr.on_death("Soldier", round_number=1)
        assert not commander.effect_manager.active_effects


class TestSynergyConfigParsing:

    def test_pair_from_dict(self) -> None:
        data = {
            "synergy_id": "test_pair",
            "type": "PAIR",
            "roles": {
                "a": {
                    "on_partner_death_buff": {
                        "stat": "PHYSICAL_ATTACK",
                        "percent": 10.0,
                        "duration": 3,
                    },
                },
                "b": {},
            },
        }
        cfg = SynergyConfig.from_dict(data)
        assert cfg.synergy_type == SynergyType.PAIR
        assert len(cfg.roles) == 2

    def test_group_from_dict(self) -> None:
        data = {
            "synergy_id": "pack",
            "type": "GROUP",
            "same_target_bonus_pct": 15.0,
            "last_survivor": {
                "atk_bonus_pct": 50.0,
                "speed_bonus_pct": 30.0,
                "duration": 3,
            },
        }
        cfg = SynergyConfig.from_dict(data)
        assert cfg.synergy_type == SynergyType.GROUP
        assert cfg.last_survivor is not None
