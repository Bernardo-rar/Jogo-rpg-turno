"""Teste de integracao: batalha completa Fighter + Mage + Cleric vs inimigos."""

import pytest

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character import Character
from src.core.characters.class_modifiers import ClassModifiers
from src.core.classes.cleric.cleric import HEAL_MANA_COST, Cleric
from src.core.classes.cleric.divinity import Divinity
from src.core.classes.fighter.fighter import Fighter
from src.core.classes.mage.barrier import BARRIER_EFFICIENCY
from src.core.classes.mage.mage import Mage
from src.core.combat.action_economy import ActionType
from src.core.combat.basic_attack_handler import BasicAttackHandler
from src.core.combat.combat_engine import (
    CombatEngine,
    CombatEvent,
    CombatResult,
    TurnContext,
)
from src.core.combat.combat_log import CombatLog, CombatLogEntry, EventType
from src.core.combat.damage import resolve_damage
from src.core.combat.dispatch_handler import DispatchTurnHandler
from src.core.combat.log_formatter import LogFormatter
from src.core.combat.targeting import AttackRange, get_valid_targets

EMPTY_THRESHOLDS = ThresholdCalculator({})

FIGHTER_MODS = ClassModifiers(
    hit_dice=12, vida_mod=0, mod_hp=10, mana_multiplier=6,
    mod_atk_physical=10, mod_atk_magical=6, mod_def_physical=5,
    mod_def_magical=3, regen_hp_mod=5, regen_mana_mod=3,
)
MAGE_MODS = ClassModifiers(
    hit_dice=6, vida_mod=0, mod_hp=6, mana_multiplier=12,
    mod_atk_physical=4, mod_atk_magical=10, mod_def_physical=2,
    mod_def_magical=5, regen_hp_mod=2, regen_mana_mod=5,
)
CLERIC_MODS = ClassModifiers(
    hit_dice=8, vida_mod=0, mod_hp=8, mana_multiplier=8,
    mod_atk_physical=5, mod_atk_magical=8, mod_def_physical=3,
    mod_def_magical=4, regen_hp_mod=3, regen_mana_mod=4,
)
ENEMY_MODS = ClassModifiers(
    hit_dice=8, vida_mod=0, mod_hp=7, mana_multiplier=4,
    mod_atk_physical=7, mod_atk_magical=4, mod_def_physical=3,
    mod_def_magical=3, regen_hp_mod=3, regen_mana_mod=2,
)


# --- Handlers auxiliares de teste (comportamento simples para integracao) ---


BARRIER_MANA_COST = 50


class _MageCombatHandler:
    """Mage: cria barreira no round 1, depois ataque magico + gera mana."""

    def __init__(self, mage: Mage, log: CombatLog) -> None:
        self._mage = mage
        self._log = log
        self._first_turn = True

    def execute_turn(self, context: TurnContext) -> list[CombatEvent]:
        if not context.action_economy.has_actions:
            return []
        if self._first_turn:
            self._first_turn = False
            self._mage.create_barrier(BARRIER_MANA_COST)
            self._log.add(CombatLogEntry(
                round_number=context.round_number,
                event_type=EventType.BARRIER_CREATE,
                actor_name=context.combatant.name,
                value=BARRIER_MANA_COST * BARRIER_EFFICIENCY,
            ))
        context.action_economy.use(ActionType.ACTION)
        targets = get_valid_targets(AttackRange.RANGED, context.enemies)
        if not targets:
            return []
        target = targets[0]
        result = resolve_damage(
            attack_power=context.combatant.magical_attack,
            defense=target.magical_defense,
        )
        target.take_damage(result.final_damage)
        mana_restored = self._mage.mana_per_basic_attack
        self._mage.restore_mana(mana_restored)
        self._log.add(CombatLogEntry(
            round_number=context.round_number,
            event_type=EventType.MANA_RESTORE,
            actor_name=context.combatant.name,
            value=mana_restored,
        ))
        return [CombatEvent(
            round_number=context.round_number,
            actor_name=context.combatant.name,
            target_name=target.name,
            damage=result,
        )]


class _ClericCombatHandler:
    """Cleric: cura aliado mais ferido se alguem perdeu HP, senao ataque magico."""

    def __init__(self, cleric: Cleric, log: CombatLog) -> None:
        self._cleric = cleric
        self._log = log

    def execute_turn(self, context: TurnContext) -> list[CombatEvent]:
        if not context.action_economy.has_actions:
            return []
        wounded = self._find_wounded(context.allies)
        if wounded is not None and self._cleric.current_mana >= HEAL_MANA_COST:
            context.action_economy.use(ActionType.ACTION)
            healed = self._cleric.heal_target(wounded)
            self._log.add(CombatLogEntry(
                round_number=context.round_number,
                event_type=EventType.HEAL,
                actor_name=context.combatant.name,
                target_name=wounded.name,
                value=healed,
            ))
            return []
        context.action_economy.use(ActionType.ACTION)
        targets = get_valid_targets(AttackRange.RANGED, context.enemies)
        if not targets:
            return []
        target = targets[0]
        result = resolve_damage(
            attack_power=context.combatant.magical_attack,
            defense=target.magical_defense,
        )
        target.take_damage(result.final_damage)
        return [CombatEvent(
            round_number=context.round_number,
            actor_name=context.combatant.name,
            target_name=target.name,
            damage=result,
        )]

    def _find_wounded(self, allies: list[Character]) -> Character | None:
        wounded = [a for a in allies if a.is_alive and a.current_hp < a.max_hp]
        if not wounded:
            return None
        return min(wounded, key=lambda a: a.current_hp)


# --- Fixtures ---


def _fighter_attrs() -> Attributes:
    return Attributes({
        AttributeType.STRENGTH: 8, AttributeType.DEXTERITY: 6,
        AttributeType.CONSTITUTION: 7, AttributeType.INTELLIGENCE: 3,
        AttributeType.WISDOM: 4, AttributeType.CHARISMA: 3,
        AttributeType.MIND: 3,
    })


def _mage_attrs() -> Attributes:
    return Attributes({
        AttributeType.STRENGTH: 3, AttributeType.DEXTERITY: 5,
        AttributeType.CONSTITUTION: 4, AttributeType.INTELLIGENCE: 9,
        AttributeType.WISDOM: 8, AttributeType.CHARISMA: 7,
        AttributeType.MIND: 10,
    })


def _cleric_attrs() -> Attributes:
    return Attributes({
        AttributeType.STRENGTH: 4, AttributeType.DEXTERITY: 5,
        AttributeType.CONSTITUTION: 6, AttributeType.INTELLIGENCE: 7,
        AttributeType.WISDOM: 9, AttributeType.CHARISMA: 8,
        AttributeType.MIND: 7,
    })


def _enemy_attrs() -> Attributes:
    return Attributes({
        AttributeType.STRENGTH: 6, AttributeType.DEXTERITY: 5,
        AttributeType.CONSTITUTION: 6, AttributeType.INTELLIGENCE: 4,
        AttributeType.WISDOM: 4, AttributeType.CHARISMA: 3,
        AttributeType.MIND: 3,
    })


@pytest.fixture
def battle_setup():
    """Cria party + enemies + engine + combat log pronta para rodar."""
    fighter = Fighter(
        name="Gareth", attributes=_fighter_attrs(),
        class_modifiers=FIGHTER_MODS, threshold_calculator=EMPTY_THRESHOLDS,
    )
    mage = Mage(
        name="Merlin", attributes=_mage_attrs(),
        class_modifiers=MAGE_MODS, threshold_calculator=EMPTY_THRESHOLDS,
    )
    cleric = Cleric(
        name="Aurelia", attributes=_cleric_attrs(),
        class_modifiers=CLERIC_MODS, threshold_calculator=EMPTY_THRESHOLDS,
        divinity=Divinity.HOLY,
    )
    enemies = [
        Character(
            name=f"Goblin_{i}", attributes=_enemy_attrs(),
            class_modifiers=ENEMY_MODS, threshold_calculator=EMPTY_THRESHOLDS,
        )
        for i in range(3)
    ]
    party = [fighter, mage, cleric]
    combat_log = CombatLog()
    mage_handler = _MageCombatHandler(mage, combat_log)
    cleric_handler = _ClericCombatHandler(cleric, combat_log)
    handler = DispatchTurnHandler(
        {"Merlin": mage_handler, "Aurelia": cleric_handler},
        BasicAttackHandler(),
    )
    engine = CombatEngine(party, enemies, handler)
    return engine, party, enemies, fighter, mage, cleric, combat_log


class TestMockBattleRuns:
    def test_combat_runs_to_completion(self, battle_setup):
        engine, *_ = battle_setup
        result = engine.run_combat()
        assert result is not None

    def test_result_is_not_draw(self, battle_setup):
        engine, *_ = battle_setup
        result = engine.run_combat()
        assert result != CombatResult.DRAW

    def test_events_were_generated(self, battle_setup):
        engine, *_ = battle_setup
        engine.run_combat()
        assert len(engine.events) > 0


class TestMockBattleParticipants:
    def test_fighter_appears_in_events(self, battle_setup):
        engine, *_ = battle_setup
        engine.run_combat()
        actors = {e.actor_name for e in engine.events}
        assert "Gareth" in actors

    def test_mage_appears_in_events(self, battle_setup):
        engine, *_ = battle_setup
        engine.run_combat()
        actors = {e.actor_name for e in engine.events}
        assert "Merlin" in actors

    def test_enemies_appear_in_events(self, battle_setup):
        engine, *_ = battle_setup
        engine.run_combat()
        actors = {e.actor_name for e in engine.events}
        enemy_names = {"Goblin_0", "Goblin_1", "Goblin_2"}
        assert actors & enemy_names


class TestMockBattleClassMechanics:
    def test_mage_used_barrier(self, battle_setup):
        engine, _, _, _, mage, _, _ = battle_setup
        engine.run_round()
        expected = BARRIER_MANA_COST * BARRIER_EFFICIENCY
        # Barrier foi criada (pode ter absorvido dano, reduzindo current)
        assert mage.barrier.current <= expected
        # Mage gastou mana (barrier 50, mas restaurou 30 via basic attack)
        assert mage.current_mana < mage.max_mana

    def test_cleric_heals_when_ally_wounded(self, battle_setup):
        engine, party, _, _, _, cleric, _ = battle_setup
        # Roda varios rounds para garantir que alguem tome dano
        for _ in range(5):
            result = engine.run_round()
            if result is not None:
                break
        # Se combate durou 5+ rounds, cleric deve ter curado alguem
        assert cleric.holy_power.current > 0

    def test_result_consistent_with_state(self, battle_setup):
        engine, party, enemies, _, _, _, _ = battle_setup
        result = engine.run_combat()
        if result == CombatResult.PARTY_VICTORY:
            assert not any(e.is_alive for e in enemies)
        elif result == CombatResult.PARTY_DEFEAT:
            assert not any(p.is_alive for p in party)


class TestMockBattleCombatLog:
    def test_combat_log_has_entries_after_battle(self, battle_setup):
        engine, *_, combat_log = battle_setup
        engine.run_combat()
        for event in engine.events:
            combat_log.add_from_combat_event(event)
        assert len(combat_log.entries) > 0

    def test_combat_log_contains_attack_events(self, battle_setup):
        engine, *_, combat_log = battle_setup
        engine.run_combat()
        for event in engine.events:
            combat_log.add_from_combat_event(event)
        attacks = combat_log.get_by_type(EventType.ATTACK)
        assert len(attacks) > 0

    def test_combat_log_contains_barrier_create(self, battle_setup):
        engine, *_, combat_log = battle_setup
        engine.run_combat()
        barriers = combat_log.get_by_type(EventType.BARRIER_CREATE)
        assert len(barriers) == 1
        assert barriers[0].actor_name == "Merlin"

    def test_combat_log_contains_mana_restore(self, battle_setup):
        engine, *_, combat_log = battle_setup
        engine.run_combat()
        restores = combat_log.get_by_type(EventType.MANA_RESTORE)
        assert len(restores) >= 1
        assert all(r.actor_name == "Merlin" for r in restores)

    def test_combat_log_contains_heal_events(self, battle_setup):
        engine, *_, combat_log = battle_setup
        for _ in range(5):
            result = engine.run_round()
            if result is not None:
                break
        heals = combat_log.get_by_type(EventType.HEAL)
        assert len(heals) >= 1
        assert all(h.actor_name == "Aurelia" for h in heals)

    def test_formatted_log_is_readable(self, battle_setup, capsys):
        engine, *_, combat_log = battle_setup
        result = engine.run_combat()
        for event in engine.events:
            combat_log.add_from_combat_event(event)
        text = LogFormatter.to_text(combat_log)
        print(f"\n=== COMBAT LOG ({engine.round_number} rounds) ===")
        print(text)
        print(f"=== RESULT: {result.name} ===")
        captured = capsys.readouterr()
        assert "Round" in captured.out
        assert result.name in captured.out
