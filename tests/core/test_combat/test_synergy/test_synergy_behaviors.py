"""Tests for synergy behaviors — aura, pack tactics, combo."""

from src.core.combat.synergy.synergy_behaviors import (
    apply_commander_aura,
    check_pack_same_target,
    remove_commander_aura,
)
from src.core.combat.synergy.synergy_config import CommanderAuraConfig
from src.core.effects.modifiable_stat import ModifiableStat

from tests.core.test_combat.conftest import _build_char as _make_char


AURA_CONFIG = CommanderAuraConfig(atk_bonus_pct=10.0, def_bonus_pct=10.0)


class TestCommanderAura:

    def test_apply_aura_adds_buffs(self) -> None:
        soldier = _make_char("Soldier")
        apply_commander_aura([soldier], AURA_CONFIG)
        effects = soldier.effect_manager.active_effects
        assert len(effects) >= 2

    def test_apply_aura_skips_dead(self) -> None:
        soldier = _make_char("Soldier")
        soldier.take_damage(soldier.current_hp)
        apply_commander_aura([soldier], AURA_CONFIG)
        assert not soldier.effect_manager.active_effects

    def test_remove_aura_clears_buffs(self) -> None:
        soldier = _make_char("Soldier")
        apply_commander_aura([soldier], AURA_CONFIG)
        remove_commander_aura([soldier])
        aura_effects = [
            e for e in soldier.effect_manager.active_effects
            if "aura" in e.stacking_key
        ]
        assert len(aura_effects) == 0

    def test_aura_is_idempotent(self) -> None:
        soldier = _make_char("Soldier")
        apply_commander_aura([soldier], AURA_CONFIG)
        apply_commander_aura([soldier], AURA_CONFIG)
        aura_effects = [
            e for e in soldier.effect_manager.active_effects
            if "aura" in e.stacking_key
        ]
        # Should replace, not stack
        assert len(aura_effects) == 2  # atk + def


class TestPackSameTarget:

    def test_two_attacks_on_same_target_returns_bonus(self) -> None:
        attacks = {"Wolf1": "Hero", "Wolf2": "Hero"}
        bonus = check_pack_same_target(attacks, 15.0)
        assert bonus["Wolf2"] == 15.0

    def test_first_attacker_gets_no_bonus(self) -> None:
        attacks = {"Wolf1": "Hero", "Wolf2": "Hero"}
        bonus = check_pack_same_target(attacks, 15.0)
        assert "Wolf1" not in bonus

    def test_different_targets_no_bonus(self) -> None:
        attacks = {"Wolf1": "Hero", "Wolf2": "Mage"}
        bonus = check_pack_same_target(attacks, 15.0)
        assert len(bonus) == 0

    def test_three_attacks_stacks(self) -> None:
        attacks = {"W1": "Hero", "W2": "Hero", "W3": "Hero"}
        bonus = check_pack_same_target(attacks, 15.0)
        assert "W2" in bonus
        assert "W3" in bonus
        assert len(bonus) == 2
