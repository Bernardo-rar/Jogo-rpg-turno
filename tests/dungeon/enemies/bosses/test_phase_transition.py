"""Testes para PhaseTransitionConfig — config de transicao de fase de boss."""

from __future__ import annotations

from src.core.combat.action_economy import ActionEconomy
from src.core.combat.combat_engine import CombatEvent, EventType, TurnContext
from src.core.effects.modifiable_stat import ModifiableStat
from src.dungeon.enemies.bosses.boss_phase import BossPhase
from src.dungeon.enemies.bosses.phase_handler import PhaseHandler
from src.dungeon.enemies.bosses.phase_transition import (
    PhaseTransitionConfig,
    TransitionEffect,
)
from tests.dungeon.enemies.ai.conftest import make_char


class TestTransitionEffect:

    def test_transition_effect_is_frozen(self) -> None:
        effect = TransitionEffect(
            stat="PHYSICAL_ATTACK", percent=30.0, duration=999,
        )
        try:
            effect.stat = "SPEED"  # type: ignore[misc]
            assert False, "Should be frozen"
        except AttributeError:
            pass

    def test_transition_effect_stores_values(self) -> None:
        effect = TransitionEffect(
            stat="PHYSICAL_ATTACK", percent=30.0, duration=999,
        )
        assert effect.stat == "PHYSICAL_ATTACK"
        assert effect.percent == 30.0
        assert effect.duration == 999


class TestPhaseTransitionConfig:

    def test_transition_config_defaults(self) -> None:
        config = PhaseTransitionConfig()
        assert config.battle_cry == ""
        assert config.self_buffs == ()

    def test_transition_config_from_dict_with_buffs(self) -> None:
        data = {
            "battle_cry": "The boss ENRAGES!",
            "self_buffs": [
                {"stat": "PHYSICAL_ATTACK", "percent": 30.0, "duration": 999},
                {"stat": "SPEED", "percent": 10.0, "duration": 5},
            ],
        }
        config = PhaseTransitionConfig.from_dict(data)
        assert config.battle_cry == "The boss ENRAGES!"
        assert len(config.self_buffs) == 2
        assert config.self_buffs[0].stat == "PHYSICAL_ATTACK"
        assert config.self_buffs[0].percent == 30.0
        assert config.self_buffs[0].duration == 999
        assert config.self_buffs[1].stat == "SPEED"

    def test_transition_config_from_dict_empty(self) -> None:
        data: dict = {}
        config = PhaseTransitionConfig.from_dict(data)
        assert config.battle_cry == ""
        assert config.self_buffs == ()

    def test_transition_config_from_dict_cry_only(self) -> None:
        data = {"battle_cry": "ROAR!"}
        config = PhaseTransitionConfig.from_dict(data)
        assert config.battle_cry == "ROAR!"
        assert config.self_buffs == ()

    def test_transition_config_is_frozen(self) -> None:
        config = PhaseTransitionConfig()
        try:
            config.battle_cry = "nope"  # type: ignore[misc]
            assert False, "Should be frozen"
        except AttributeError:
            pass


# --- Helpers para testes de integracao ---

_TRANSITION = PhaseTransitionConfig(
    battle_cry="The boss ENRAGES!",
    self_buffs=(
        TransitionEffect(
            stat="PHYSICAL_ATTACK", percent=30.0, duration=999,
        ),
    ),
)

_PHASE1 = BossPhase(
    phase_number=1, hp_threshold=0.5, handler_key="p1", transition=None,
)
_PHASE2 = BossPhase(
    phase_number=2, hp_threshold=0.0, handler_key="p2",
    transition=_TRANSITION,
)


class _TrackerHandler:
    """Handler de teste que registra chamadas."""

    def __init__(self, key: str) -> None:
        self.key = key
        self.call_count = 0

    def execute_turn(self, context: TurnContext) -> list[CombatEvent]:
        self.call_count += 1
        return []


def _make_context(boss, hp_pct: float) -> TurnContext:
    damage = int(boss.max_hp * (1.0 - hp_pct))
    if damage > 0:
        boss.take_damage(damage)
    return TurnContext(
        combatant=boss,
        allies=[boss],
        enemies=[make_char("Hero")],
        action_economy=ActionEconomy(),
        round_number=1,
    )


class TestPhaseTransitionIntegration:

    def test_phase_transition_fires_once_on_hp_threshold(self) -> None:
        """Transicao dispara ao entrar na fase 2."""
        p1 = _TrackerHandler("p1")
        p2 = _TrackerHandler("p2")
        handler = PhaseHandler(
            phases=(_PHASE1, _PHASE2),
            phase_handlers={"p1": p1, "p2": p2},
            default_handler=_TrackerHandler("default"),
        )
        boss = make_char("Boss")
        # Primeira vez na fase 2
        ctx = _make_context(boss, hp_pct=0.3)
        events = handler.execute_turn(ctx)
        battle_cry_events = [
            e for e in events if e.event_type == EventType.BUFF
        ]
        assert len(battle_cry_events) >= 1

    def test_phase_transition_does_not_refire(self) -> None:
        """Transicao so dispara uma vez por fase."""
        p1 = _TrackerHandler("p1")
        p2 = _TrackerHandler("p2")
        handler = PhaseHandler(
            phases=(_PHASE1, _PHASE2),
            phase_handlers={"p1": p1, "p2": p2},
            default_handler=_TrackerHandler("default"),
        )
        boss = make_char("Boss")
        # Primeira vez — dispara transicao
        ctx = _make_context(boss, hp_pct=0.3)
        events_first = handler.execute_turn(ctx)
        buff_count_first = sum(
            1 for e in events_first if e.event_type == EventType.BUFF
        )
        # Segunda vez na mesma fase — NAO dispara
        ctx2 = _make_context(boss, hp_pct=0.2)
        events_second = handler.execute_turn(ctx2)
        buff_count_second = sum(
            1 for e in events_second if e.event_type == EventType.BUFF
        )
        assert buff_count_first >= 1
        assert buff_count_second == 0

    def test_phase_transition_applies_self_buff(self) -> None:
        """Transicao aplica StatBuff ao boss."""
        p1 = _TrackerHandler("p1")
        p2 = _TrackerHandler("p2")
        handler = PhaseHandler(
            phases=(_PHASE1, _PHASE2),
            phase_handlers={"p1": p1, "p2": p2},
            default_handler=_TrackerHandler("default"),
        )
        boss = make_char("Boss")
        ctx = _make_context(boss, hp_pct=0.3)
        handler.execute_turn(ctx)
        mods = boss.effect_manager.get_modifiers_for(
            ModifiableStat.PHYSICAL_ATTACK,
        )
        assert len(mods) == 1
        assert mods[0].percent == 30.0

    def test_phase_transition_returns_battle_cry_event(self) -> None:
        """Evento retornado contem o battle cry na descricao."""
        p1 = _TrackerHandler("p1")
        p2 = _TrackerHandler("p2")
        handler = PhaseHandler(
            phases=(_PHASE1, _PHASE2),
            phase_handlers={"p1": p1, "p2": p2},
            default_handler=_TrackerHandler("default"),
        )
        boss = make_char("Boss")
        ctx = _make_context(boss, hp_pct=0.3)
        events = handler.execute_turn(ctx)
        cry_events = [
            e for e in events if "ENRAGES" in e.description
        ]
        assert len(cry_events) == 1
        assert cry_events[0].actor_name == "Boss"

    def test_no_transition_when_config_is_none(self) -> None:
        """Sem transicao quando phase nao tem config de transition."""
        phase_no_transition = BossPhase(
            phase_number=1, hp_threshold=0.0,
            handler_key="p1", transition=None,
        )
        p1 = _TrackerHandler("p1")
        handler = PhaseHandler(
            phases=(phase_no_transition,),
            phase_handlers={"p1": p1},
            default_handler=_TrackerHandler("default"),
        )
        boss = make_char("Boss")
        ctx = _make_context(boss, hp_pct=0.5)
        events = handler.execute_turn(ctx)
        buff_events = [
            e for e in events if e.event_type == EventType.BUFF
        ]
        assert buff_events == []


class TestBossPhaseWithTransition:

    def test_boss_phase_from_dict_with_transition(self) -> None:
        data = {
            "phase_number": 2,
            "hp_threshold": 0.0,
            "handler_key": "p2",
            "transition": {
                "battle_cry": "ROAR!",
                "self_buffs": [
                    {"stat": "PHYSICAL_ATTACK", "percent": 30.0, "duration": 999},
                ],
            },
        }
        phase = BossPhase.from_dict(data)
        assert phase.transition is not None
        assert phase.transition.battle_cry == "ROAR!"
        assert len(phase.transition.self_buffs) == 1

    def test_boss_phase_from_dict_without_transition(self) -> None:
        data = {
            "phase_number": 1,
            "hp_threshold": 0.5,
            "handler_key": "p1",
        }
        phase = BossPhase.from_dict(data)
        assert phase.transition is None
