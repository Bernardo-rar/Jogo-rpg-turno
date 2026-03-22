"""Teste de integracao: batalha com dano elemental, on-hit effects e DoT."""

from dataclasses import dataclass

import pytest

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_modifiers import ClassModifiers
from src.core.combat.action_economy import ActionType
from src.core.combat.combat_engine import (
    CombatEngine,
    CombatEvent,
    CombatResult,
    TurnContext,
)
from src.core.combat.damage import resolve_damage
from src.core.combat.dispatch_handler import DispatchTurnHandler
from src.core.combat.elemental_attack import (
    ElementalContext,
    apply_on_hit_effects,
    resolve_elemental_attack,
)
from src.core.combat.targeting import AttackRange, get_valid_targets
from src.core.effects.ailments.ailment_factory import create_freeze, create_poison
from src.core.effects.ailments.burn import Burn
from src.core.elements.element_type import ElementType
from src.core.elements.elemental_profile import ElementalProfile
from src.core.elements.on_hit.on_hit_config import load_on_hit_configs

EMPTY_THRESHOLDS = ThresholdCalculator({})
ON_HIT_CONFIGS = load_on_hit_configs()

PARTY_MODS = ClassModifiers(
    hit_dice=10, mod_hp_flat=0, mod_hp_mult=8, mana_multiplier=8,
    mod_atk_physical=8, mod_atk_magical=8, mod_def_physical=4,
    mod_def_magical=4, regen_hp_mod=3, regen_mana_mod=3,
)
ENEMY_MODS = ClassModifiers(
    hit_dice=8, mod_hp_flat=0, mod_hp_mult=6, mana_multiplier=4,
    mod_atk_physical=6, mod_atk_magical=4, mod_def_physical=3,
    mod_def_magical=3, regen_hp_mod=2, regen_mana_mod=2,
)


def _attrs(primary: int = 8, secondary: int = 5) -> Attributes:
    return Attributes({
        AttributeType.STRENGTH: primary,
        AttributeType.DEXTERITY: secondary,
        AttributeType.CONSTITUTION: secondary,
        AttributeType.INTELLIGENCE: primary,
        AttributeType.WISDOM: secondary,
        AttributeType.CHARISMA: secondary,
        AttributeType.MIND: secondary,
    })


@dataclass
class BattleSetup:
    """Setup de uma batalha elemental para testes."""
    engine: CombatEngine
    party: list[Character]
    enemies: list[Character]
    fire_mage: Character
    holy_cleric: Character
    warrior: Character


class _FireMageHandler:
    """Ataque magico FIRE em primeiro inimigo vivo."""

    def execute_turn(self, context: TurnContext) -> list[CombatEvent]:
        if not context.action_economy.has_actions:
            return []
        context.action_economy.use(ActionType.ACTION)
        targets = get_valid_targets(AttackRange.RANGED, context.enemies)
        if not targets:
            return []
        target = targets[0]
        base_result = resolve_damage(
            attack_power=context.combatant.magical_attack,
            defense=target.magical_defense,
        )
        outcome = resolve_elemental_attack(
            base_result,
            ElementalContext(ElementType.FIRE, target.elemental_profile, ON_HIT_CONFIGS),
        )
        target.take_damage(outcome.elemental_result.final_damage)
        apply_on_hit_effects(
            outcome, target.effect_manager, context.combatant.effect_manager,
        )
        return [CombatEvent(
            round_number=context.round_number,
            actor_name=context.combatant.name,
            target_name=target.name,
            damage=base_result,
        )]


class _HolyClericHandler:
    """Ataque magico HOLY em primeiro inimigo + distribui party healing."""

    def __init__(self, allies: list[Character]) -> None:
        self._allies = allies

    def execute_turn(self, context: TurnContext) -> list[CombatEvent]:
        if not context.action_economy.has_actions:
            return []
        context.action_economy.use(ActionType.ACTION)
        targets = get_valid_targets(AttackRange.RANGED, context.enemies)
        if not targets:
            return []
        target = targets[0]
        base_result = resolve_damage(
            attack_power=context.combatant.magical_attack,
            defense=target.magical_defense,
        )
        outcome = resolve_elemental_attack(
            base_result,
            ElementalContext(ElementType.HOLY, target.elemental_profile, ON_HIT_CONFIGS),
        )
        target.take_damage(outcome.elemental_result.final_damage)
        self._distribute_healing(outcome.on_hit.party_healing)
        return [CombatEvent(
            round_number=context.round_number,
            actor_name=context.combatant.name,
            target_name=target.name,
            damage=base_result,
        )]

    def _distribute_healing(self, total: int) -> None:
        alive = [a for a in self._allies if a.is_alive]
        if not alive or total <= 0:
            return
        per_ally = max(1, total // len(alive))
        for ally in alive:
            ally.heal(per_ally)


@pytest.fixture
def elemental_battle():
    """Party: FireMage + HolyCleric + Fighter vs 3 enemies.

    Enemy_weak: fraco a FIRE (1.5x)
    Enemy_poison: tem Poison pre-aplicado em party member 'Warrior'
    Enemy_frozen: comeca com Freeze (nao age no primeiro turno)
    """
    fire_mage = Character(
        name="Ignis", attributes=_attrs(primary=9),
        config=CharacterConfig(
            class_modifiers=PARTY_MODS,
            threshold_calculator=EMPTY_THRESHOLDS,
        ),
    )
    holy_cleric = Character(
        name="Seraph", attributes=_attrs(primary=7, secondary=6),
        config=CharacterConfig(
            class_modifiers=PARTY_MODS,
            threshold_calculator=EMPTY_THRESHOLDS,
        ),
    )
    warrior = Character(
        name="Warrior", attributes=_attrs(primary=8),
        config=CharacterConfig(
            class_modifiers=PARTY_MODS,
            threshold_calculator=EMPTY_THRESHOLDS,
        ),
    )
    party = [fire_mage, holy_cleric, warrior]

    weak_profile = ElementalProfile(resistances={ElementType.FIRE: 1.5})
    enemy_weak = Character(
        name="FireWeak", attributes=_attrs(primary=5, secondary=4),
        config=CharacterConfig(
            class_modifiers=ENEMY_MODS,
            threshold_calculator=EMPTY_THRESHOLDS,
            elemental_profile=weak_profile,
        ),
    )
    enemy_normal = Character(
        name="Grunt", attributes=_attrs(primary=5, secondary=4),
        config=CharacterConfig(
            class_modifiers=ENEMY_MODS,
            threshold_calculator=EMPTY_THRESHOLDS,
        ),
    )
    enemy_frozen = Character(
        name="FrozenFoe", attributes=_attrs(primary=5, secondary=4),
        config=CharacterConfig(
            class_modifiers=ENEMY_MODS,
            threshold_calculator=EMPTY_THRESHOLDS,
        ),
    )
    enemies = [enemy_weak, enemy_normal, enemy_frozen]

    # Pre-apply effects
    warrior.effect_manager.add_effect(
        create_poison(damage_per_tick=5, duration=3),
    )
    enemy_frozen.effect_manager.add_effect(create_freeze(duration=1))

    cleric_handler = _HolyClericHandler(party)
    handler = DispatchTurnHandler(
        {"Ignis": _FireMageHandler(), "Seraph": cleric_handler},
        default=_PhysicalHandler(),
    )
    engine = CombatEngine(party, enemies, handler)
    return BattleSetup(
        engine=engine, party=party, enemies=enemies,
        fire_mage=fire_mage, holy_cleric=holy_cleric, warrior=warrior,
    )


class _PhysicalHandler:
    """Handler padrao: ataque fisico melee."""

    def execute_turn(self, context: TurnContext) -> list[CombatEvent]:
        if not context.action_economy.has_actions:
            return []
        context.action_economy.use(ActionType.ACTION)
        targets = get_valid_targets(AttackRange.MELEE, context.enemies)
        if not targets:
            return []
        target = targets[0]
        result = resolve_damage(
            attack_power=context.combatant.physical_attack,
            defense=target.physical_defense,
        )
        target.take_damage(result.final_damage)
        return [CombatEvent(
            round_number=context.round_number,
            actor_name=context.combatant.name,
            target_name=target.name,
            damage=result,
        )]


class TestMockBattleElementalRuns:

    def test_combat_runs_to_completion(self, elemental_battle) -> None:
        result = elemental_battle.engine.run_combat()
        assert isinstance(result, CombatResult)

    def test_result_is_not_draw(self, elemental_battle) -> None:
        result = elemental_battle.engine.run_combat()
        assert result != CombatResult.DRAW

    def test_result_consistent_with_state(self, elemental_battle) -> None:
        result = elemental_battle.engine.run_combat()
        if result == CombatResult.PARTY_VICTORY:
            assert not any(e.is_alive for e in elemental_battle.enemies)
        elif result == CombatResult.PARTY_DEFEAT:
            assert not any(p.is_alive for p in elemental_battle.party)


class TestFireMageElemental:

    def test_fire_mage_applies_burn_to_target(self, elemental_battle) -> None:
        elemental_battle.engine.run_round()
        target = elemental_battle.enemies[0]
        has_burn = any(
            isinstance(e, Burn)
            for e in target.effect_manager.active_effects
        )
        assert has_burn

    def test_weak_enemy_takes_extra_fire_damage(self, elemental_battle) -> None:
        target = elemental_battle.enemies[0]
        hp_before = target.current_hp
        elemental_battle.engine.run_round()
        damage_taken = hp_before - target.current_hp
        base = resolve_damage(
            attack_power=elemental_battle.fire_mage.magical_attack,
            defense=target.magical_defense,
        )
        assert damage_taken > base.final_damage


class TestHolyClericHealing:

    def test_holy_cleric_heals_party(self, elemental_battle) -> None:
        warrior = elemental_battle.warrior
        poison_damage_per_tick = 5
        # Warrior perde HP do poison tick no round 1
        elemental_battle.engine.run_round()
        warrior_hp_after_r1 = warrior.current_hp
        elemental_battle.engine.run_round()
        # Warrior sofre poison (5 dmg) mas recebe cura do cleric HOLY.
        # Se a cura funciona, a perda de HP sera menor que o dano puro do poison.
        warrior_hp_loss = warrior_hp_after_r1 - warrior.current_hp
        assert warrior_hp_loss < poison_damage_per_tick


class TestPoisonTicks:

    def test_poison_ticks_on_warrior(self, elemental_battle) -> None:
        warrior = elemental_battle.warrior
        hp_before = warrior.current_hp
        elemental_battle.engine.run_round()
        assert warrior.current_hp < hp_before

    def test_poison_expires_after_duration(self, elemental_battle) -> None:
        warrior = elemental_battle.warrior
        combat_ended = False
        for _ in range(5):
            result = elemental_battle.engine.run_round()
            if result is not None:
                combat_ended = True
                break
        # Poison duration=3: ou expirou, ou combate terminou antes
        poison_count = sum(
            1 for e in warrior.effect_manager.active_effects
            if type(e).__name__ == "Poison"
        )
        assert poison_count == 0 or combat_ended


class TestFrozenEnemySkips:

    def test_frozen_enemy_skips_first_turn(self, elemental_battle) -> None:
        elemental_battle.engine.run_round()
        # FrozenFoe tinha Freeze duration=1, deve ter expirado
        has_skip = any(
            entry.is_skip for entry in elemental_battle.engine.effect_log
            if entry.character_name == "FrozenFoe"
        )
        assert has_skip

    def test_frozen_enemy_acts_after_expire(self, elemental_battle) -> None:
        elemental_battle.engine.run_round()
        elemental_battle.engine.run_round()
        # No round 2, FrozenFoe deveria ter agido (sem skip)
        r2_skips = [
            entry for entry in elemental_battle.engine.effect_log
            if entry.character_name == "FrozenFoe"
            and entry.is_skip
            and entry.round_number == 2
        ]
        assert len(r2_skips) == 0


class TestEffectLogPopulated:

    def test_effect_log_has_entries(self, elemental_battle) -> None:
        elemental_battle.engine.run_combat()
        assert len(elemental_battle.engine.effect_log) > 0

    def test_all_participants_contributed(self, elemental_battle) -> None:
        elemental_battle.engine.run_combat()
        actors = {e.actor_name for e in elemental_battle.engine.events}
        assert "Ignis" in actors
        assert "Warrior" in actors
