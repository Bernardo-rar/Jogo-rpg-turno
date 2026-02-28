import pytest

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character import Character
from src.core.characters.class_modifiers import ClassModifiers
from src.core.combat.action_economy import ActionType
from src.core.combat.basic_attack_handler import BasicAttackHandler
from src.core.combat.combat_engine import (
    MAX_ROUNDS,
    CombatEngine,
    CombatEvent,
    CombatResult,
    TurnContext,
)
from src.core.combat.damage import DamageResult

# -- Stats de teste --
# Todos attrs = 10, mod_atk=2, mod_def=1, regen=0
# HP = ((10+10+0)*2)*1 = 40
# ATK = (0+10+10)*2 = 40
# DEF = (10+10+10)*1 = 30
# DMG = 40-30 = 10 por hit, 4 rounds pra matar
# Ordem: mesmo speed (10), desempate por nome (alfabetico)

SIMPLE_MODIFIERS = ClassModifiers(
    hit_dice=10,
    vida_mod=0,
    mod_hp=1,
    mana_multiplier=1,
    mod_atk_physical=2,
    mod_atk_magical=1,
    mod_def_physical=1,
    mod_def_magical=1,
    regen_hp_mod=0,
    regen_mana_mod=0,
)

EMPTY_THRESHOLDS = ThresholdCalculator({})


def _make_char(name: str, speed: int = 10) -> Character:
    attrs = Attributes()
    for attr_type in AttributeType:
        attrs.set(attr_type, 10)
    if speed != 10:
        attrs.set(AttributeType.DEXTERITY, speed)
    return Character(
        name, attrs, SIMPLE_MODIFIERS, threshold_calculator=EMPTY_THRESHOLDS
    )


class DoNothingHandler:
    """Handler que nao faz nada - para testar mecanica do engine."""

    def execute_turn(self, context: TurnContext) -> list[CombatEvent]:
        return []


class OneHitKillHandler:
    """Handler que mata o primeiro inimigo instantaneamente."""

    def execute_turn(self, context: TurnContext) -> list[CombatEvent]:
        targets = [e for e in context.enemies if e.is_alive]
        if not targets:
            return []
        context.action_economy.use(ActionType.ACTION)
        target = targets[0]
        target.take_damage(target.current_hp)
        result = DamageResult(
            raw_damage=target.current_hp,
            defense_value=0,
            is_critical=False,
            final_damage=target.current_hp,
        )
        return [
            CombatEvent(
                round_number=context.round_number,
                actor_name=context.combatant.name,
                target_name=target.name,
                damage=result,
            )
        ]


@pytest.fixture
def handler():
    return BasicAttackHandler()


class TestCombatResult:
    def test_has_party_victory(self):
        assert CombatResult.PARTY_VICTORY is not None

    def test_has_party_defeat(self):
        assert CombatResult.PARTY_DEFEAT is not None

    def test_has_draw(self):
        assert CombatResult.DRAW is not None

    def test_has_three_values(self):
        assert len(list(CombatResult)) == 3


class TestCombatEngineInit:
    def test_initial_round_is_zero(self, handler):
        engine = CombatEngine([_make_char("A")], [_make_char("Z")], handler)
        assert engine.round_number == 0

    def test_initial_events_empty(self, handler):
        engine = CombatEngine([_make_char("A")], [_make_char("Z")], handler)
        assert engine.events == []

    def test_initial_result_is_none(self, handler):
        engine = CombatEngine([_make_char("A")], [_make_char("Z")], handler)
        assert engine.result is None


class TestCombatEngineRound:
    def test_run_round_increments_round_number(self):
        engine = CombatEngine(
            [_make_char("A")], [_make_char("Z")], DoNothingHandler()
        )
        engine.run_round()
        assert engine.round_number == 1

    def test_two_rounds_increments_to_two(self):
        engine = CombatEngine(
            [_make_char("A")], [_make_char("Z")], DoNothingHandler()
        )
        engine.run_round()
        engine.run_round()
        assert engine.round_number == 2

    def test_run_round_returns_none_when_ongoing(self, handler):
        # 1 round de combate: 10 dmg cada, ninguem morre
        engine = CombatEngine([_make_char("A")], [_make_char("Z")], handler)
        result = engine.run_round()
        assert result is None

    def test_run_round_records_events(self, handler):
        engine = CombatEngine([_make_char("A")], [_make_char("Z")], handler)
        engine.run_round()
        assert len(engine.events) == 2  # A ataca Z, Z ataca A


class TestCombatEngineVictory:
    def test_party_wins_1v1_when_name_first_alphabetically(self, handler):
        # "Alpha" < "Zeta", Alpha age primeiro, mata Zeta no round 4
        result = CombatEngine(
            [_make_char("Alpha")], [_make_char("Zeta")], handler
        ).run_combat()
        assert result == CombatResult.PARTY_VICTORY

    def test_party_loses_1v1_when_name_last_alphabetically(self, handler):
        # "Zeta" > "Alpha", Alpha (enemy) age primeiro
        result = CombatEngine(
            [_make_char("Zeta")], [_make_char("Alpha")], handler
        ).run_combat()
        assert result == CombatResult.PARTY_DEFEAT

    def test_party_wins_when_faster(self, handler):
        # Hero speed=15 > Enemy speed=5, hero sempre age primeiro
        result = CombatEngine(
            [_make_char("Hero", speed=15)],
            [_make_char("Enemy", speed=5)],
            handler,
        ).run_combat()
        assert result == CombatResult.PARTY_VICTORY

    def test_party_wins_2v1(self, handler):
        # 2 aliados vs 1 inimigo, vantagem numerica
        result = CombatEngine(
            [_make_char("A1"), _make_char("A2")],
            [_make_char("Zed")],
            handler,
        ).run_combat()
        assert result == CombatResult.PARTY_VICTORY

    def test_one_hit_kill_ends_in_round_one(self):
        engine = CombatEngine(
            [_make_char("Alpha")],
            [_make_char("Zeta")],
            OneHitKillHandler(),
        )
        result = engine.run_combat()
        assert result == CombatResult.PARTY_VICTORY
        assert engine.round_number == 1


class TestCombatEngineDraw:
    def test_draw_after_max_rounds(self):
        engine = CombatEngine(
            [_make_char("A")], [_make_char("Z")], DoNothingHandler()
        )
        result = engine.run_combat()
        assert result == CombatResult.DRAW
        assert engine.round_number == MAX_ROUNDS


class TestCombatEngineEvents:
    def test_events_have_correct_round_number(self, handler):
        engine = CombatEngine([_make_char("A")], [_make_char("Z")], handler)
        engine.run_round()
        assert all(e.round_number == 1 for e in engine.events)

    def test_events_have_correct_actor_names(self, handler):
        engine = CombatEngine([_make_char("A")], [_make_char("Z")], handler)
        engine.run_round()
        actors = [e.actor_name for e in engine.events]
        assert actors == ["A", "Z"]  # A first (alphabetical)

    def test_events_accumulate_across_rounds(self, handler):
        engine = CombatEngine([_make_char("A")], [_make_char("Z")], handler)
        engine.run_round()
        engine.run_round()
        assert len(engine.events) == 4  # 2 per round

    def test_event_damage_is_correct(self, handler):
        engine = CombatEngine([_make_char("A")], [_make_char("Z")], handler)
        engine.run_round()
        first_event = engine.events[0]
        assert first_event.damage.final_damage == 10  # ATK=40 - DEF=30


class TestCombatEngineDeadSkip:
    def test_dead_combatant_does_not_act(self):
        # Alpha (party) one-hit-kills Bravo (enemy, faster)
        # Charlie (enemy, slower) should still act
        engine = CombatEngine(
            [_make_char("Alpha", speed=15)],
            [_make_char("Bravo", speed=10), _make_char("Charlie", speed=5)],
            OneHitKillHandler(),
        )
        engine.run_round()
        # Alpha kills Bravo. Bravo is dead. Charlie kills Alpha.
        actors = [e.actor_name for e in engine.events]
        assert "Bravo" not in actors  # Bravo morreu antes de agir
        assert "Alpha" in actors
        assert "Charlie" in actors

    def test_combat_ends_mid_round_when_side_wiped(self, handler):
        # Alpha (party, fast) vs Zeta (enemy, slow, low HP enough to die)
        engine = CombatEngine(
            [_make_char("Alpha")],
            [_make_char("Zeta")],
            OneHitKillHandler(),
        )
        engine.run_round()
        # Alpha kills Zeta. Combat ends. Zeta doesn't act.
        assert len(engine.events) == 1
        assert engine.events[0].actor_name == "Alpha"
        assert engine.result == CombatResult.PARTY_VICTORY
