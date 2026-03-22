"""Roda uma batalha mock e exibe o combat log formatado.

Uso:
    python -m scripts.run_mock_battle
    python -m scripts.run_mock_battle --json
"""

from __future__ import annotations

import sys

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_modifiers import ClassModifiers
from src.core.characters.position import Position
from src.core.classes.cleric.cleric import HEAL_MANA_COST, Cleric
from src.core.classes.cleric.divinity import Divinity
from src.core.classes.fighter.fighter import Fighter
from src.core.classes.mage.barrier import BARRIER_EFFICIENCY
from src.core.classes.mage.mage import Mage
from src.core.combat.action_economy import ActionType
from src.core.combat.basic_attack_handler import BasicAttackHandler
from src.core.combat.combat_engine import CombatEngine, CombatEvent, TurnContext
from src.core.combat.combat_log import CombatLog, CombatLogEntry, EventType
from src.core.combat.damage import resolve_damage
from src.core.combat.dispatch_handler import DispatchTurnHandler
from src.core.combat.log_formatter import LogFormatter
from src.core.combat.targeting import AttackRange, get_valid_targets

EMPTY_THRESHOLDS = ThresholdCalculator({})

FIGHTER_MODS = ClassModifiers(
    hit_dice=12, mod_hp_flat=0, mod_hp_mult=10, mana_multiplier=6,
    mod_atk_physical=10, mod_atk_magical=6, mod_def_physical=5,
    mod_def_magical=3, regen_hp_mod=5, regen_mana_mod=3,
)
MAGE_MODS = ClassModifiers(
    hit_dice=6, mod_hp_flat=0, mod_hp_mult=6, mana_multiplier=12,
    mod_atk_physical=4, mod_atk_magical=10, mod_def_physical=2,
    mod_def_magical=5, regen_hp_mod=2, regen_mana_mod=5,
)
CLERIC_MODS = ClassModifiers(
    hit_dice=8, mod_hp_flat=0, mod_hp_mult=8, mana_multiplier=8,
    mod_atk_physical=5, mod_atk_magical=8, mod_def_physical=3,
    mod_def_magical=4, regen_hp_mod=3, regen_mana_mod=4,
)
ENEMY_MODS = ClassModifiers(
    hit_dice=8, mod_hp_flat=0, mod_hp_mult=7, mana_multiplier=4,
    mod_atk_physical=7, mod_atk_magical=4, mod_def_physical=3,
    mod_def_magical=3, regen_hp_mod=3, regen_mana_mod=2,
)

BARRIER_MANA_COST = 50


def _attrs(s: int, d: int, c: int, i: int, w: int, ch: int, m: int) -> Attributes:
    return Attributes({
        AttributeType.STRENGTH: s, AttributeType.DEXTERITY: d,
        AttributeType.CONSTITUTION: c, AttributeType.INTELLIGENCE: i,
        AttributeType.WISDOM: w, AttributeType.CHARISMA: ch,
        AttributeType.MIND: m,
    })


class _MageCombatHandler:
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
            actor_name=context.combatant.name, value=mana_restored,
        ))
        return [CombatEvent(
            round_number=context.round_number,
            actor_name=context.combatant.name,
            target_name=target.name, damage=result,
        )]


class _ClericCombatHandler:
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
                target_name=wounded.name, value=healed,
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
            target_name=target.name, damage=result,
        )]

    def _find_wounded(self, allies: list[Character]) -> Character | None:
        wounded = [a for a in allies if a.is_alive and a.current_hp < a.max_hp]
        if not wounded:
            return None
        return min(wounded, key=lambda a: a.current_hp)


def run_battle(output_json: bool = False) -> None:
    """Monta e roda a batalha, exibindo o combat log."""
    fighter_config = CharacterConfig(
        class_modifiers=FIGHTER_MODS,
        threshold_calculator=EMPTY_THRESHOLDS,
    )
    fighter = Fighter(
        name="Gareth", attributes=_attrs(8, 6, 7, 3, 4, 3, 3),
        config=fighter_config,
    )
    mage_config = CharacterConfig(
        class_modifiers=MAGE_MODS,
        threshold_calculator=EMPTY_THRESHOLDS,
        position=Position.BACK,
    )
    mage = Mage(
        name="Merlin", attributes=_attrs(3, 5, 4, 9, 8, 7, 10),
        config=mage_config,
    )
    cleric_config = CharacterConfig(
        class_modifiers=CLERIC_MODS,
        threshold_calculator=EMPTY_THRESHOLDS,
        position=Position.BACK,
    )
    cleric = Cleric(
        name="Aurelia", attributes=_attrs(4, 5, 6, 7, 9, 8, 7),
        config=cleric_config, divinity=Divinity.HOLY,
    )
    enemy_config = CharacterConfig(
        class_modifiers=ENEMY_MODS,
        threshold_calculator=EMPTY_THRESHOLDS,
    )
    enemies = [
        Character(
            name=f"Goblin_{i}", attributes=_attrs(6, 5, 6, 4, 4, 3, 3),
            config=enemy_config,
        )
        for i in range(3)
    ]

    combat_log = CombatLog()
    mage_handler = _MageCombatHandler(mage, combat_log)
    cleric_handler = _ClericCombatHandler(cleric, combat_log)
    handler = DispatchTurnHandler(
        {"Merlin": mage_handler, "Aurelia": cleric_handler},
        BasicAttackHandler(),
    )
    engine = CombatEngine([fighter, mage, cleric], enemies, handler)
    result = engine.run_combat()

    for event in engine.events:
        combat_log.add_from_combat_event(event)

    if output_json:
        print(LogFormatter.to_json(combat_log))
        return

    print(f"=== COMBAT LOG ({engine.round_number} rounds) ===")
    print(LogFormatter.to_text(combat_log))
    print(f"=== RESULT: {result.name} ===")
    print()
    attacks = combat_log.get_by_type(EventType.ATTACK)
    heals = combat_log.get_by_type(EventType.HEAL)
    barriers = combat_log.get_by_type(EventType.BARRIER_CREATE)
    restores = combat_log.get_by_type(EventType.MANA_RESTORE)
    print(f"Total entries: {len(combat_log.entries)}")
    print(f"  Attacks: {len(attacks)}")
    print(f"  Heals: {len(heals)}")
    print(f"  Barriers: {len(barriers)}")
    print(f"  Mana restores: {len(restores)}")


if __name__ == "__main__":
    use_json = "--json" in sys.argv
    run_battle(output_json=use_json)
