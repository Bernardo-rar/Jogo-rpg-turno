"""Tests for BossTurnHandler — orchestrates all boss mechanics."""

import pytest

from src.core.combat.action_economy import ActionEconomy, ActionType
from src.core.combat.boss.boss_field_effect import BossFieldConfig
from src.core.combat.boss.boss_mechanic_config import (
    BossMechanicConfig,
    SummonConfig,
)
from src.core.combat.boss.boss_transformation import TransformationConfig
from src.core.combat.boss.boss_turn_handler import BossTurnHandler
from src.core.combat.boss.charged_attack import ChargedAttackConfig
from src.core.combat.boss.empower_bar import EmpowerBarConfig
from src.core.combat.combat_engine import EventType, TurnContext
from src.core.characters.class_modifiers import ClassModifiers

from tests.core.test_combat.conftest import _build_char as _make_char


class StubHandler:
    """Base handler that records calls."""

    def __init__(self):
        self.call_count = 0

    def execute_turn(self, context):
        from src.core.combat.combat_engine import CombatEvent

        self.call_count += 1
        return [CombatEvent(
            round_number=context.round_number,
            actor_name=context.combatant.name,
            target_name=context.enemies[0].name if context.enemies else "",
            description="base_attack",
        )]


def _ctx(boss, enemies=None, round_num=1):
    enemies = enemies or [_make_char("Hero")]
    return TurnContext(
        combatant=boss,
        allies=[],
        enemies=enemies,
        action_economy=ActionEconomy(),
        round_number=round_num,
    )


def _empty_config(**overrides) -> BossMechanicConfig:
    return BossMechanicConfig(**overrides)


def _charge_config() -> ChargedAttackConfig:
    return ChargedAttackConfig(
        attack_id="slam",
        name="Slam",
        charge_message="Charging!",
        release_message="SLAM!",
        damage_mult=2.0,
    )


def _empower_config() -> EmpowerBarConfig:
    return EmpowerBarConfig(
        max_value=100,
        gain_per_round=50,
        loss_on_weakness_hit=40,
        empowered_atk_mult=1.50,
        empowered_def_mult=1.20,
        empowered_duration=2,
    )


def _field_config() -> BossFieldConfig:
    return BossFieldConfig(
        field_id="lava",
        name="Lava Floor",
        element="FIRE",
        damage_pct_max_hp=0.10,
        duration=3,
        trigger_message="Lava!",
    )


def _transform_config() -> TransformationConfig:
    mods = ClassModifiers(
        hit_dice=20, mod_hp_flat=10, mod_hp_mult=7,
        mana_multiplier=0, mod_atk_physical=10, mod_atk_magical=6,
        mod_def_physical=8, mod_def_magical=8,
        regen_hp_mod=3, regen_mana_mod=0,
    )
    return TransformationConfig(
        hp_threshold=0.30,
        new_name="Transformed Boss",
        battle_cry="I transform!",
        heal_pct=0.20,
        new_class_modifiers=mods,
    )


class TestBossTurnHandlerNormal:

    def test_delegates_to_base_when_no_mechanics(self) -> None:
        base = StubHandler()
        handler = BossTurnHandler(base, _empty_config())
        boss = _make_char("Boss")
        events = handler.execute_turn(_ctx(boss))
        assert base.call_count == 1
        assert any("base_attack" in e.description for e in events)


class TestBossTurnHandlerCharge:

    def test_charge_starts_at_interval(self) -> None:
        cfg = _empty_config(
            charged_attacks=(_charge_config(),),
            charge_every_n_rounds=4,
        )
        base = StubHandler()
        handler = BossTurnHandler(base, cfg)
        boss = _make_char("Boss")
        events = handler.execute_turn(_ctx(boss, round_num=4))
        assert any(e.event_type == EventType.CHARGE for e in events)
        assert base.call_count == 0

    def test_charge_does_not_start_before_interval(self) -> None:
        cfg = _empty_config(
            charged_attacks=(_charge_config(),),
            charge_every_n_rounds=4,
        )
        base = StubHandler()
        handler = BossTurnHandler(base, cfg)
        boss = _make_char("Boss")
        events = handler.execute_turn(_ctx(boss, round_num=2))
        assert not any(e.event_type == EventType.CHARGE for e in events)
        assert base.call_count == 1

    def test_release_fires_next_turn(self) -> None:
        cfg = _empty_config(
            charged_attacks=(_charge_config(),),
            charge_every_n_rounds=4,
        )
        base = StubHandler()
        handler = BossTurnHandler(base, cfg)
        boss = _make_char("Boss")
        hero = _make_char("Hero")
        handler.execute_turn(_ctx(boss, [hero], round_num=4))
        old_hp = hero.current_hp
        handler.execute_turn(_ctx(boss, [hero], round_num=5))
        assert hero.current_hp < old_hp

    def test_release_deals_boosted_damage(self) -> None:
        cfg = _empty_config(
            charged_attacks=(_charge_config(),),
            charge_every_n_rounds=1,
        )
        base = StubHandler()
        handler = BossTurnHandler(base, cfg)
        boss = _make_char("Boss")
        hero = _make_char("Hero")
        handler.execute_turn(_ctx(boss, [hero], round_num=1))
        events = handler.execute_turn(_ctx(boss, [hero], round_num=2))
        charge_events = [
            e for e in events
            if e.event_type == EventType.CHARGE and e.damage
        ]
        assert len(charge_events) >= 1


class TestBossTurnHandlerEmpower:

    def test_empower_bar_fills(self) -> None:
        cfg = _empty_config(empower_bar=_empower_config())
        handler = BossTurnHandler(StubHandler(), cfg)
        boss = _make_char("Boss")
        handler.execute_turn(_ctx(boss, round_num=1))
        assert handler.empower_bar.current == 50

    def test_empower_activates_when_full(self) -> None:
        cfg = _empty_config(empower_bar=_empower_config())
        handler = BossTurnHandler(StubHandler(), cfg)
        boss = _make_char("Boss")
        handler.execute_turn(_ctx(boss, round_num=1))
        events = handler.execute_turn(_ctx(boss, round_num=2))
        assert handler.empower_bar.is_empowered
        assert any(e.event_type == EventType.EMPOWER for e in events)

    def test_weakness_hit_reduces_bar(self) -> None:
        cfg = _empty_config(empower_bar=_empower_config())
        handler = BossTurnHandler(StubHandler(), cfg)
        boss = _make_char("Boss")
        handler.execute_turn(_ctx(boss, round_num=1))
        handler.on_weakness_hit()
        assert handler.empower_bar.current == 10


class TestBossTurnHandlerField:

    def test_field_damages_enemies(self) -> None:
        cfg = _empty_config()
        handler = BossTurnHandler(StubHandler(), cfg)
        handler.activate_field(_field_config())
        boss = _make_char("Boss")
        hero = _make_char("Hero")
        old_hp = hero.current_hp
        handler.execute_turn(_ctx(boss, [hero], round_num=1))
        assert hero.current_hp < old_hp

    def test_field_expires(self) -> None:
        cfg = _empty_config()
        handler = BossTurnHandler(StubHandler(), cfg)
        field_cfg = BossFieldConfig(
            field_id="x", name="X", element="FIRE",
            damage_pct_max_hp=0.01, duration=1,
            trigger_message="!",
        )
        handler.activate_field(field_cfg)
        boss = _make_char("Boss")
        hero = _make_char("Hero")
        handler.execute_turn(_ctx(boss, [hero], round_num=1))
        # Field should have expired after 1 tick
        handler.execute_turn(_ctx(boss, [hero], round_num=2))
        assert handler.field_effect is None


class TestBossTurnHandlerTransform:

    def test_transforms_at_threshold(self) -> None:
        cfg = _empty_config(transformation=_transform_config())
        handler = BossTurnHandler(StubHandler(), cfg)
        boss = _make_char("Boss")
        dmg = boss.current_hp - 1
        boss.take_damage(dmg)
        events = handler.execute_turn(_ctx(boss, round_num=1))
        assert handler.is_transformed
        assert boss.name == "Transformed Boss"
        assert any(e.event_type == EventType.TRANSFORM for e in events)

    def test_does_not_transform_above_threshold(self) -> None:
        cfg = _empty_config(transformation=_transform_config())
        handler = BossTurnHandler(StubHandler(), cfg)
        boss = _make_char("Boss")
        handler.execute_turn(_ctx(boss, round_num=1))
        assert not handler.is_transformed

    def test_transforms_only_once(self) -> None:
        cfg = _empty_config(transformation=_transform_config())
        handler = BossTurnHandler(StubHandler(), cfg)
        boss = _make_char("Boss")
        boss.take_damage(boss.current_hp - 1)
        handler.execute_turn(_ctx(boss, round_num=1))
        events = handler.execute_turn(_ctx(boss, round_num=2))
        assert not any(e.event_type == EventType.TRANSFORM for e in events)


class TestBossTurnHandlerMinions:

    def test_on_minion_death_enrages(self) -> None:
        summon = SummonConfig(
            minion_template_id="minion_a",
            enrage_atk_pct=15.0,
        )
        cfg = _empty_config(summons=(summon,))
        handler = BossTurnHandler(StubHandler(), cfg)
        boss = _make_char("Boss")
        handler.register_minion("Minion_1")
        events = handler.on_minion_death(boss, "Minion_1")
        assert any(e.event_type == EventType.BUFF for e in events)

    def test_minion_tracking(self) -> None:
        cfg = _empty_config()
        handler = BossTurnHandler(StubHandler(), cfg)
        handler.register_minion("M1")
        handler.register_minion("M2")
        m1 = _make_char("M1")
        m2 = _make_char("M2")
        assert handler.alive_minion_count([m1, m2]) == 2
        m1.take_damage(m1.current_hp)
        assert handler.alive_minion_count([m1, m2]) == 1
