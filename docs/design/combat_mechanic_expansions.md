# Combat Mechanic Expansions - Game Design Document

**Version**: 1.0
**Date**: 2026-03-29
**Status**: Design Draft - Pre-Implementation
**Author**: GameDesigner Agent

---

## Table of Contents

1. [Position Swapping (Front/Back Line)](#1-position-swapping)
2. [Advanced Boss Mechanics](#2-advanced-boss-mechanics)
3. [QTE (Quick Time Events)](#3-qte-quick-time-events)
4. [Enemy Synergies](#4-enemy-synergies)
5. [Rogue Free Item Use](#5-rogue-free-item-use)

---

## 1. Position Swapping

### Purpose

Position is the spatial backbone of the tactical layer. Right now it exists as
a static property that gates melee targeting. The player never has a reason to
*think* about positioning because the cost/benefit is invisible and the action
is under-powered. This expansion makes the front/back decision a real choice
every turn: the player trades survivability for damage output and vice-versa.

### Player Experience Goal

"Do I push my Mage to the front for the extra damage on this critical turn, or
keep her safe? The Fighter is at 30% HP -- if I pull him back, the enemy's
melee attacker has no front-line target and their AoE will scatter. That buys
me one round to heal."

### 1.1 Core Rules

#### Position Modifiers (Multiplicative)

```
Variable              | FRONT  | BACK   | Tuning Notes
----------------------|--------|--------|-------------------------------
damage_dealt_mult     | 1.10   | 0.90   | [PLACEHOLDER] - 10% swing both ways
damage_taken_mult     | 1.15   | 0.85   | [PLACEHOLDER] - Back is safer
heal_received_mult    | 1.00   | 1.00   | Neutral -- heals are not positional
melee_targetable      | true   | false*  | *BACK becomes targetable if no FRONT alive
```

**Rationale**: The 10-15% swing is noticeable but not build-defining. A
backliner who is forced to front does not become useless; a frontliner who
retreats does not become invincible. This is a *tactical seasoning*, not a hard
gate.

#### Swap Action

| Property          | Value                                            |
|-------------------|--------------------------------------------------|
| Action Cost       | BONUS_ACTION                                     |
| Stamina Cost      | 0 (removed -- swapping is too core to tax)       |
| Cooldown          | 0 turns (but costs your entire bonus action)     |
| Who can swap      | Any alive combatant (player or enemy)             |
| Animation         | Slide left/right (0.3s)                          |

#### Targeting Rules (Updated)

```
Melee Attack:
  1. Collect alive enemies at FRONT.
  2. If none at FRONT -> all alive enemies become valid targets (fallback).
  3. If a FRONT unit has Taunt active -> that unit is the ONLY valid target.

Ranged / Magical Attack:
  1. All alive enemies are valid targets regardless of position.
  2. Taunt has NO effect on ranged/magical attacks.
```

### 1.2 Forced Positioning (Push/Pull Skills)

Some skills forcibly move a target to a specific line.

**New SkillEffectType**: `FORCE_POSITION`

```python
# In SkillEffectType enum:
FORCE_POSITION = auto()
```

**SkillEffect fields used**:
- `effect_type`: `FORCE_POSITION`
- `mechanic_param`: `"FRONT"` or `"BACK"` (target position)
- `duration`: 0 (instant, permanent until swapped back)

**Example Skills**:

| Skill Name      | Class    | Effect                              |
|-----------------|----------|-------------------------------------|
| Shield Bash     | Fighter  | Push enemy to FRONT                  |
| Gale Force      | Mage     | Push enemy to BACK                   |
| Grappling Hook  | Rogue    | Pull enemy to FRONT from BACK        |
| Holy Ground     | Paladin  | Force self and adjacent ally to FRONT |

### 1.3 Taunt Mechanic

**Taunt** is an effect (not a position state). While active, it forces all
*melee attacks* to target the taunter.

```python
# New effect: TauntEffect(Effect)
#   stacking_key = "taunt_{character_name}"
#   duration: int (turns)
#   target_name: str (the taunter)
```

**Rules**:
- Only one Taunt can be active per side (latest replaces).
- Taunt only redirects MELEE attacks. Ranged/magical ignore it.
- Taunt breaks if the taunter dies or is moved to BACK line.
- Enemies with Taunt force the player to attack that enemy with melee.

**Balance constraint**: Taunt duration capped at 3 turns max. Permanent
taunting removes agency and is degenerate.

### 1.4 Enemy Position AI

Enemies use the same position system. Enemy AI rules for swapping:

```
Enemy Position AI Decision Tree:
  1. If HEALER/CASTER and at FRONT -> try swap to BACK (priority: HIGH)
  2. If TANK and at BACK -> try swap to FRONT (priority: HIGH)
  3. If HP < 25% and at FRONT -> try swap to BACK (priority: MEDIUM)
  4. If no FRONT allies alive and self is TANK -> swap to FRONT (priority: CRITICAL)
  5. Otherwise -> stay (no swap)
```

### 1.5 Data Structures

#### New: `data/combat/position_modifiers.json`

```json
{
  "FRONT": {
    "damage_dealt_mult": 1.10,
    "damage_taken_mult": 1.15,
    "heal_received_mult": 1.00,
    "melee_targetable": true
  },
  "BACK": {
    "damage_dealt_mult": 0.90,
    "damage_taken_mult": 0.85,
    "heal_received_mult": 1.00,
    "melee_targetable": false
  }
}
```

#### New: `PositionModifiers` frozen dataclass

```python
@dataclass(frozen=True)
class PositionModifiers:
    damage_dealt_mult: float
    damage_taken_mult: float
    heal_received_mult: float
    melee_targetable: bool
```

#### New: `TauntEffect(Effect)` in `src/core/effects/taunt_effect.py`

```python
class TauntEffect(Effect):
    """Forces melee attacks to target the taunter."""
    stacking_key: str  # "taunt_{side}"
    taunter_name: str
    duration: int
```

### 1.6 Implementation Steps

1. Create `data/combat/position_modifiers.json` with the table above.
2. Create `src/core/combat/position_modifiers.py`:
   - `PositionModifiers` dataclass
   - `load_position_modifiers()` loader
   - `get_modifiers_for(position: Position) -> PositionModifiers`
3. Modify `src/core/combat/damage.py`:
   - `resolve_damage()` accepts optional `position_mod: float` parameter
   - Apply `damage_dealt_mult` to attack_power before damage calc
4. Modify `src/core/combat/action_resolver.py` `_resolve_basic_attack()`:
   - Fetch position modifiers for attacker and target
   - Apply `damage_dealt_mult` to attack and `damage_taken_mult` to final
5. Modify `src/core/combat/targeting.py` `get_valid_targets()`:
   - Check for active TauntEffect on enemy side
   - If taunt active and attack is MELEE -> return only taunter
6. Add `FORCE_POSITION` to `SkillEffectType` enum.
7. Add `_apply_force_position()` handler in `skill_effect_applier.py`.
8. Create `src/core/effects/taunt_effect.py` with `TauntEffect`.
9. Update `src/core/combat/skill_effect_applier.py` to register taunt applier.
10. Update UI: show position indicators (FRONT/BACK label under each card).

### 1.7 Files to Create/Modify

**Create**:
- `data/combat/position_modifiers.json`
- `src/core/combat/position_modifiers.py`
- `src/core/effects/taunt_effect.py`
- `tests/core/test_combat/test_position_modifiers.py`
- `tests/core/test_combat/test_taunt.py`
- `tests/core/test_combat/test_force_position.py`

**Modify**:
- `src/core/combat/action_resolver.py` (apply position multipliers)
- `src/core/combat/basic_attack_handler.py` (apply position multipliers)
- `src/core/combat/targeting.py` (taunt redirect)
- `src/core/combat/skill_effect_applier.py` (FORCE_POSITION, taunt)
- `src/core/skills/skill_effect_type.py` (add FORCE_POSITION)
- `src/core/combat/damage_preview.py` (show position-adjusted numbers)
- `src/ui/scenes/playable_combat_scene.py` (position labels)

### 1.8 Integration Points

- **DamageResult**: Position multipliers apply BEFORE resolve_damage, so
  DamageResult.raw_damage already reflects the position bonus.
- **Effect System**: TauntEffect uses the existing Effect ABC + EffectManager.
  Stacking policy: REPLACE (one taunt per side).
- **AI TurnHandler**: Enemy handlers read position modifiers to decide swaps.
- **SkillEffect Pipeline**: FORCE_POSITION plugs into the existing applier
  dispatch table alongside DAMAGE, HEAL, etc.

### 1.9 Test Cases

```
test_front_position_increases_damage_dealt()
  Arrange: Attacker at FRONT, target alive.
  Act: Resolve basic attack.
  Assert: Final damage = base * 1.10 (rounded).

test_back_position_reduces_damage_taken()
  Arrange: Attacker at FRONT, target at BACK, no front allies.
  Act: Resolve basic attack (fallback targeting).
  Assert: Final damage = base * 0.85 (rounded).

test_swap_costs_bonus_action()
  Arrange: Character at FRONT, bonus action available.
  Act: Execute MOVE action.
  Assert: Position changed to BACK, bonus action consumed.

test_swap_fails_when_no_bonus_action()
  Arrange: Character at FRONT, bonus action already used.
  Act: Execute MOVE action.
  Assert: Position unchanged, no events returned.

test_taunt_forces_melee_to_target_taunter()
  Arrange: Tank has TauntEffect active, another enemy at FRONT.
  Act: get_valid_targets(MELEE, enemies).
  Assert: Returns only the taunter.

test_taunt_does_not_affect_ranged()
  Arrange: Tank has TauntEffect active.
  Act: get_valid_targets(RANGED, enemies).
  Assert: Returns all alive enemies.

test_taunt_breaks_on_taunter_death()
  Arrange: Taunter at FRONT with TauntEffect. Taunter dies.
  Act: get_valid_targets(MELEE, enemies).
  Assert: Normal targeting (no taunt redirect).

test_force_position_moves_target_to_front()
  Arrange: Target at BACK.
  Act: Apply FORCE_POSITION skill effect with param "FRONT".
  Assert: Target.position == Position.FRONT.

test_enemy_healer_swaps_to_back_if_at_front()
  Arrange: Enemy healer at FRONT position.
  Act: AI position decision.
  Assert: Swap to BACK.
```

---

## 2. Advanced Boss Mechanics

### Purpose

Bosses are the climax of a dungeon floor. The current phase system (HP
threshold triggers stat buffs) creates a difficulty spike but not a *cognitive
spike*. Players should be making new decisions in phase 2 that they were not
making in phase 1. Each mechanic below creates a distinct problem that demands
a distinct solution.

### Player Experience Goal

"The boss is charging -- do I interrupt with a stun or burn my mana on damage
before the AoE lands? Those minions are annoying but if I kill them the boss
will enrage. The empower bar is almost full -- someone NEEDS to hit the
weakness this turn or we're dead."

### 2.1 Charged Attacks

#### Rules

A **charged attack** is a two-turn sequence:
1. **Charge Turn**: Boss skips normal action. A `ChargeState` effect is applied
   to itself with `duration=1`. Visual: boss glows, charge bar appears.
2. **Release Turn**: At the start of the boss's next turn, the charged attack
   fires before any other action. Massive damage (AoE or single target).

```
Variable               | Value     | Tuning Notes
-----------------------|-----------|---------------------------
charge_damage_mult     | 2.5       | [PLACEHOLDER] - multiplier on boss ATK
charge_aoe_falloff     | 0.7       | [PLACEHOLDER] - each additional target takes 70%
interrupt_window       | 1 turn    | Players must interrupt during the charge turn
interrupting_effects   | freeze, paralysis, stun, knockback | Any CC that causes skip_turn
```

#### Interrupt Mechanic

If the boss receives a `skip_turn=True` TickResult during the charge turn
(from freeze, paralysis, etc.), the charge is cancelled. The ChargeState
effect is removed. Boss loses its next attack entirely.

**This is the reward for carrying CC skills.** A party with no CC will eat
the charged attack and must survive it through healing/shielding.

#### Data Structure

New field in boss JSON `phases[].charged_attacks`:

```json
{
  "charged_attacks": [
    {
      "attack_id": "golem_earthquake",
      "name": "Earthquake",
      "charge_message": "The Ancient Golem raises its fists!",
      "release_message": "The earth shatters!",
      "damage_mult": 2.5,
      "target_type": "ALL_ENEMIES",
      "element": "EARTH",
      "aoe_falloff": 0.7,
      "trigger_condition": "round_number % 4 == 0",
      "interruptible": true
    }
  ]
}
```

#### New Effect: `ChargeStateEffect`

```python
@dataclass(frozen=True)
class ChargeStateConfig:
    attack_id: str
    damage_mult: float
    target_type: str  # "ALL_ENEMIES" | "SINGLE_ENEMY"
    element: str | None
    aoe_falloff: float
    release_message: str

class ChargeStateEffect(Effect):
    """Applied to boss during charge turn. Causes skip_turn.
    On the NEXT turn, boss handler detects this effect and fires the
    charged attack instead of normal AI."""
    stacking_key = "boss_charge"
    config: ChargeStateConfig
    # tick() returns TickResult(skip_turn=False, message=charge_message)
    # The boss handler checks for this effect at turn start
```

#### Boss Handler Integration

```python
# In the boss TurnHandler:
def execute_turn(self, context: TurnContext) -> list[CombatEvent]:
    charge = _find_charge_state(context.combatant)
    if charge is not None:
        return _release_charged_attack(charge, context)
    if _should_start_charging(context):
        return _begin_charge(context)
    return _normal_boss_turn(context)
```

### 2.2 Minion Summoning

#### Rules

At phase transitions (HP thresholds), the boss summons 1-2 minions that join
the enemy team with their own turns and HP pools.

```
Variable                | Value      | Tuning Notes
------------------------|------------|---------------------------
max_minions_alive       | 2          | Never more than 2 at once
minion_hp_scale         | 0.20       | [PLACEHOLDER] - 20% of boss max HP
minion_atk_scale        | 0.40       | [PLACEHOLDER] - 40% of boss ATK
minion_enrage_buff_pct  | 15.0       | [PLACEHOLDER] - boss gets +15% ATK per dead minion
minion_enrage_duration  | 999        | Permanent (until combat ends)
summon_cooldown_rounds  | 5          | Minimum rounds between summons
```

#### Enrage on Minion Death

When a minion dies, the boss receives an `EnrageBuff` (StatBuff on
PHYSICAL_ATTACK and MAGICAL_ATTACK, percent = `minion_enrage_buff_pct`).
This stacks -- killing both minions means +30% ATK.

**Player Decision**: Kill minions fast and deal with a stronger boss, or
control/CC the minions and slowly chip the boss down.

#### Data Structure

New field in boss JSON `phases[].summons`:

```json
{
  "summons": [
    {
      "minion_id": "golem_fragment",
      "count": 2,
      "hp_scale": 0.20,
      "atk_scale": 0.40,
      "position": "FRONT",
      "enrage_on_death": {
        "stat": "PHYSICAL_ATTACK",
        "percent": 15.0,
        "duration": 999
      }
    }
  ]
}
```

#### Implementation

Summoning requires adding combatants to a live combat. This means:
1. `CombatEngine` needs `add_combatant(character, side)` method.
2. `TurnOrder` needs `insert_combatant(combatant)` to add mid-round.
3. Boss handler emits a `SummonEvent` (new EventType).
4. Engine processes SummonEvent by instantiating minion from template.

```python
# New EventType:
SUMMON = auto()

# CombatEngine new method:
def add_combatant(self, character: Character, is_enemy: bool) -> None:
    """Adds a combatant mid-combat (for summons)."""
    target_list = self._enemies if is_enemy else self._party
    target_list.append(character)
    self._participants[character.name] = character
    self._economies[character.name] = ActionEconomy()
    self._turn_order.insert(character)
```

### 2.3 Empower Bar

#### Rules

The boss has a hidden resource bar (`empower_bar`) that fills passively each
round. When full, the boss enters an **Empowered State** with boosted stats.
Hitting the boss's elemental weakness resets the bar.

```
Variable                | Value     | Tuning Notes
------------------------|-----------|---------------------------
empower_max             | 100       | Full bar triggers empower
empower_gain_per_round  | 20        | [PLACEHOLDER] - fills in 5 rounds if uncontested
empower_loss_on_weakness| 40        | [PLACEHOLDER] - one weakness hit = 2 rounds of breathing room
empowered_atk_mult      | 1.50      | [PLACEHOLDER] - +50% damage during empower
empowered_def_mult      | 1.20      | [PLACEHOLDER] - +20% defense during empower
empowered_duration       | 3         | [PLACEHOLDER] - turns of empowered state
empower_reset_after_state| true     | Bar resets to 0 after empowered state ends
```

**Player Decision**: The party MUST include at least one character who can deal
the boss's weakness element. If they do not, the boss empowers every 5 rounds
and the fight becomes increasingly harder. This is intentional -- party
composition matters.

#### Data Structure

New field in boss JSON:

```json
{
  "empower_bar": {
    "max_value": 100,
    "gain_per_round": 20,
    "loss_on_weakness_hit": 40,
    "weakness_element": "FIRE",
    "empowered_state": {
      "atk_mult": 1.50,
      "def_mult": 1.20,
      "duration": 3,
      "battle_cry": "The Golem's core reaches critical mass!"
    }
  }
}
```

#### New Class: `EmpowerBar`

```python
class EmpowerBar:
    """Boss empower resource. Fills each round, resets on weakness hit."""

    def __init__(self, config: EmpowerBarConfig) -> None:
        self._current: int = 0
        self._config = config
        self._empowered_remaining: int = 0

    @property
    def current(self) -> int: ...
    @property
    def is_full(self) -> bool: ...
    @property
    def is_empowered(self) -> bool: ...

    def tick_round(self) -> bool:
        """Fills bar by gain_per_round. Returns True if bar just became full."""
    def on_weakness_hit(self) -> None:
        """Reduces bar by loss_on_weakness_hit."""
    def activate_empowered(self) -> None:
        """Enters empowered state, resets bar to 0."""
    def tick_empowered(self) -> bool:
        """Decrements empowered turns. Returns True if it just ended."""
```

### 2.4 Field Effects (Boss)

#### Rules

Bosses can create persistent **field conditions** that affect ALL combatants
(both sides) for N turns. These are distinct from the Druid's field conditions
(which are party-friendly).

```
Variable                | Value     | Tuning Notes
------------------------|-----------|---------------------------
max_field_effects       | 1         | Only one boss field active at a time
field_damage_per_turn   | 5-15%     | [PLACEHOLDER] - % of target max HP per turn
field_debuff_value      | -15%      | [PLACEHOLDER] - stat reduction
```

**Boss Field Types**:

| Field Type    | Element  | Effect per Turn                          | Duration |
|---------------|----------|------------------------------------------|----------|
| Lava Floor    | FIRE     | 8% max HP fire damage to all grounded    | 3 turns  |
| Blizzard      | ICE      | -20% Speed to all, 5% max HP ice damage  | 4 turns  |
| Toxic Miasma  | DARK     | Poison (10 DoT) applied to all each turn | 3 turns  |
| Lightning Storm| LIGHTNING| 25% chance to paralyze each combatant    | 2 turns  |
| Holy Sanctum  | HOLY     | -30% dark damage, +15% holy damage       | 3 turns  |

**Player Counterplay**: Some fields can be "cleansed" by hitting the boss with
the opposing element (fire cleanses blizzard, water cleanses lava, etc.).

#### Data Structure

New field in boss JSON `phases[].field_effects`:

```json
{
  "field_effects": [
    {
      "field_id": "lava_floor",
      "name": "Lava Floor",
      "element": "FIRE",
      "damage_pct_max_hp": 0.08,
      "debuff_stat": null,
      "debuff_percent": 0.0,
      "duration": 3,
      "applies_to": "ALL",
      "cleanse_element": "WATER",
      "trigger_message": "The ground erupts in molten lava!"
    }
  ]
}
```

#### New Class: `BossFieldEffect(Effect)`

```python
class BossFieldEffect(Effect):
    """Persistent field that ticks all combatants each round."""
    stacking_key = "boss_field"
    config: BossFieldConfig
    _remaining: int

    def tick(self) -> TickResult:
        """Returns damage/debuff per tick."""

    def get_affected_targets(
        self, all_combatants: list[Character],
    ) -> list[Character]:
        """Returns combatants affected by this field."""
```

### 2.5 Boss Transformation

#### Rules

At a specific HP threshold, the boss **transforms entirely**: new model, new
skill set, new elemental profile, new stats. This is a hard phase cut -- the
boss essentially becomes a different enemy.

```
Variable                   | Value     | Tuning Notes
---------------------------|-----------|----------------------------
transformation_hp_threshold| 0.30      | [PLACEHOLDER] - at 30% HP
heal_on_transform_pct      | 0.20      | [PLACEHOLDER] - heals to 50% of NEW max HP
new_element                | varies    | Boss changes elemental type
stat_change_method         | replace   | New ClassModifiers replace old ones entirely
```

**Player Experience**: The party thinks they are winning, then the boss
transforms and the fight resets to a new challenge. Resources spent in phase 1
are gone. This tests resource management across the entire fight.

#### Data Structure

New field in boss JSON `phases[].transformation`:

```json
{
  "transformation": {
    "hp_threshold": 0.30,
    "new_name": "Awakened Golem",
    "battle_cry": "The Golem's ancient seal breaks!",
    "heal_pct": 0.20,
    "new_class_modifiers": {
      "hit_dice": 20,
      "mod_hp_flat": 10,
      "mod_hp_mult": 7,
      "mod_atk_physical": 10,
      "mod_atk_magical": 6,
      "mod_def_physical": 8,
      "mod_def_magical": 8
    },
    "new_elemental_profile_id": "fire_strong",
    "new_skill_ids": ["golem_magma_blast", "golem_core_meltdown"],
    "new_position": "FRONT"
  }
}
```

### 2.6 Boss Mechanic Integration with Phase System

The existing phase system triggers at HP thresholds. Each new mechanic layers
on top:

```
Phase 1 (100%-40% HP):
  - Normal attacks + basic skills
  - Charged attack every 4 rounds
  - Empower bar filling

Phase 2 (40%-0% HP):
  Transition:
    - Summon 2 minions
    - Activate field effect (Lava Floor)
    - Battle cry message
    - Self-buff (+20% DEF)
  During phase:
    - Charged attacks every 3 rounds (faster)
    - Empower bar gain increased to 30/round
    - If HP drops to 30% -> Transformation

Phase 3 (Transformation):
  - New stat block, new element, heals to 50%
  - New skill set replaces old
  - Empower bar reset, new weakness
```

### 2.7 Implementation Steps (All Boss Mechanics)

1. **ChargeStateEffect**: Create `src/core/effects/charge_state.py`.
2. **EmpowerBar**: Create `src/core/combat/boss/empower_bar.py`.
3. **BossFieldEffect**: Create `src/core/effects/boss_field_effect.py`.
4. **Summoning**: Add `add_combatant()` to CombatEngine and TurnOrder.
5. **Transformation**: Create `src/core/combat/boss/boss_transformation.py`.
6. **Boss Handler**: Create `src/core/combat/boss/boss_turn_handler.py` that
   orchestrates all mechanics per-turn.
7. **Boss Config Loader**: Extend boss JSON parser to load all new fields.
8. **EventType**: Add SUMMON, FIELD_EFFECT, CHARGE, TRANSFORM, EMPOWER.
9. **UI**: Boss charge bar, empower bar, field effect overlay, summon animation.

### 2.8 Files to Create/Modify

**Create**:
- `src/core/combat/boss/` (new package)
- `src/core/combat/boss/__init__.py`
- `src/core/combat/boss/boss_turn_handler.py`
- `src/core/combat/boss/empower_bar.py`
- `src/core/combat/boss/boss_transformation.py`
- `src/core/combat/boss/charged_attack.py`
- `src/core/effects/charge_state.py`
- `src/core/effects/boss_field_effect.py`
- `data/combat/boss_fields.json`
- `tests/core/test_combat/test_boss/` (new package)
- `tests/core/test_combat/test_boss/test_charged_attack.py`
- `tests/core/test_combat/test_boss/test_empower_bar.py`
- `tests/core/test_combat/test_boss/test_summoning.py`
- `tests/core/test_combat/test_boss/test_field_effects.py`
- `tests/core/test_combat/test_boss/test_transformation.py`

**Modify**:
- `src/core/combat/combat_engine.py` (add_combatant, field effect ticks)
- `src/core/combat/turn_order.py` (insert mid-round)
- `src/core/combat/combat_engine.py` (new EventTypes)
- `data/dungeon/enemies/bosses/*.json` (add new fields)

### 2.9 Test Cases

```
test_charged_attack_skips_boss_turn_during_charge()
  Arrange: Boss with charged attack at round 4.
  Act: Boss turn at round 4.
  Assert: Boss emits charge message, no damage dealt.

test_charged_attack_fires_on_release_turn()
  Arrange: Boss charged last turn.
  Act: Boss turn this round.
  Assert: AoE damage dealt to all party members.

test_charged_attack_interrupted_by_freeze()
  Arrange: Boss is charging. Party applies freeze.
  Act: Boss turn (should be skipped by freeze).
  Assert: Charge cancelled, no release attack next turn.

test_minion_summon_at_phase_transition()
  Arrange: Boss at 41% HP, phase 2 threshold is 40%.
  Act: Boss takes damage to 39% HP.
  Assert: 2 minions added to enemy list with own HP pools.

test_minion_death_triggers_boss_enrage()
  Arrange: Boss with 1 minion alive.
  Act: Minion dies.
  Assert: Boss gains +15% ATK buff.

test_empower_bar_fills_each_round()
  Arrange: Boss with empower_bar at 60/100.
  Act: tick_round().
  Assert: Bar at 80/100.

test_weakness_hit_reduces_empower_bar()
  Arrange: Boss weak to FIRE, bar at 80/100.
  Act: Player hits with FIRE attack.
  Assert: Bar reduced to 40/100.

test_empower_bar_full_triggers_empowered_state()
  Arrange: Bar at 90/100, gain 20.
  Act: tick_round().
  Assert: Boss enters empowered state, +50% ATK, +20% DEF.

test_field_effect_damages_all_combatants()
  Arrange: Lava Floor active.
  Act: Round tick.
  Assert: All combatants take 8% max HP fire damage.

test_field_effect_cleansed_by_opposing_element()
  Arrange: Lava Floor active (cleanse = WATER).
  Act: Player hits boss with WATER attack.
  Assert: Lava Floor removed.

test_boss_transformation_replaces_stats()
  Arrange: Boss at 31% HP, transform threshold 30%.
  Act: Boss takes damage to 29% HP.
  Assert: Boss stats replaced with new modifiers, heals to 50%.

test_boss_transformation_changes_element()
  Arrange: Boss is neutral element pre-transform.
  Act: Transformation triggers.
  Assert: Boss elemental profile is now "fire_strong".
```

---

## 3. QTE (Quick Time Events)

### Purpose

QTE adds a reflex layer to the otherwise cerebral turn-based combat. It
rewards player attention and physical engagement without punishing those who
opt out. The key design constraint: **QTE must NEVER be mandatory**. It is a
bonus opportunity, not a gate.

### Player Experience Goal

"My Mage's ultimate is ready. I activate it and -- arrows appear on screen.
LEFT, UP, RIGHT, DOWN. I nail the sequence and the spell hits for +30% damage.
Next turn I mess up the QTE and still deal 90% damage. Not bad."

### 3.1 Core Rules

```
Variable              | Value     | Tuning Notes
----------------------|-----------|---------------------------
time_window_ms        | 2500      | [PLACEHOLDER] - total time for full sequence
per_key_window_ms     | 700       | [PLACEHOLDER] - max time per individual key
min_sequence_length   | 3         | Minimum keys in a QTE
max_sequence_length   | 5         | Maximum keys in a QTE
success_bonus_mult    | 1.30      | [PLACEHOLDER] - +30% on perfect
partial_bonus_mult    | 1.15      | [PLACEHOLDER] - +15% on 50%+ correct
failure_penalty_mult  | 0.90      | [PLACEHOLDER] - -10% on total miss
partial_threshold     | 0.50      | 50% of keys correct = partial success
disabled_default      | false     | QTE enabled by default, toggle in settings
```

### 3.2 When Does QTE Trigger?

QTE is a property of individual skills, not a global system. A skill's JSON
data includes an optional `qte` field:

```json
{
  "ragnarok": {
    "name": "Ragnarok",
    "mana_cost": 40,
    "action_type": "ACTION",
    "target_type": "ALL_ENEMIES",
    "effects": [
      {"effect_type": "DAMAGE", "base_power": 80, "element": "FIRE"}
    ],
    "slot_cost": 8,
    "qte": {
      "sequence": ["LEFT", "UP", "RIGHT", "DOWN"],
      "time_window_ms": 2500,
      "difficulty": "HARD"
    }
  }
}
```

**Categories** (not hard-coded; the skill data decides):
- Ultimates: Always have QTE (4-5 keys)
- Powerful skills: Sometimes have QTE (3 keys)
- Basic skills: Never have QTE

### 3.3 QTE Flow

```
1. Player selects skill with QTE.
2. Skill animation begins.
3. QTE overlay appears:
   - Arrow keys displayed in sequence (LEFT, UP, RIGHT, DOWN)
   - Timer bar counting down (2.5 seconds total)
   - Each key highlights as it becomes "active"
4. Player presses keys in order.
   - Correct: key turns green, next key highlights
   - Wrong: key turns red, sequence continues (miss counted)
   - Timeout: remaining keys count as misses
5. QTE result calculated:
   - PERFECT: all keys correct -> 1.30x multiplier
   - PARTIAL: 50%+ correct -> 1.15x multiplier
   - FAILURE: <50% correct -> 0.90x multiplier
6. Multiplier applied to ALL effects of the skill (damage, heal, buff power).
7. If QTE disabled in settings -> always apply 1.0x (neutral).
```

### 3.4 Data Structure

#### New field in Skill: `qte`

```python
@dataclass(frozen=True)
class QteSequence:
    """QTE configuration for a skill."""
    keys: tuple[str, ...]           # ("LEFT", "UP", "RIGHT", "DOWN")
    time_window_ms: int             # Total time window
    difficulty: str                 # "EASY", "MEDIUM", "HARD" (for UI display)
```

Add to `Skill` dataclass:
```python
qte: QteSequence | None = None
```

#### New: `QteResult` value object

```python
class QteOutcome(Enum):
    PERFECT = auto()    # All keys correct
    PARTIAL = auto()    # 50%+ correct
    FAILURE = auto()    # <50% correct
    SKIPPED = auto()    # QTE disabled or auto-resolved

@dataclass(frozen=True)
class QteResult:
    outcome: QteOutcome
    correct_count: int
    total_count: int
    multiplier: float
```

#### New: `data/combat/qte_config.json`

```json
{
  "enabled": true,
  "perfect_multiplier": 1.30,
  "partial_multiplier": 1.15,
  "failure_multiplier": 0.90,
  "skipped_multiplier": 1.00,
  "partial_threshold": 0.50,
  "valid_keys": ["LEFT", "UP", "RIGHT", "DOWN"],
  "per_key_window_ms": 700
}
```

### 3.5 Implementation Steps

1. Create `data/combat/qte_config.json`.
2. Create `src/core/combat/qte/` package:
   - `qte_config.py` (QteSequence, QteResult, QteOutcome)
   - `qte_evaluator.py` (pure function: sequence + inputs -> QteResult)
   - `qte_multiplier.py` (applies QteResult multiplier to SkillEffects)
3. Add `qte: QteSequence | None = None` to `Skill` dataclass.
4. Update `Skill.from_dict()` to parse optional `qte` field.
5. Modify `src/core/combat/action_resolver.py` `_resolve_skill()`:
   - After selecting skill, check if `skill.qte` is not None.
   - If QTE enabled: yield control to UI for QTE input.
   - If QTE disabled: return `QteResult(SKIPPED, 0, 0, 1.0)`.
   - Apply multiplier to all skill effects.
6. Create `src/ui/components/qte_overlay.py` (Pygame overlay).
7. Update `src/ui/scenes/playable_combat_scene.py` to handle QTE state.

### 3.6 Files to Create/Modify

**Create**:
- `data/combat/qte_config.json`
- `src/core/combat/qte/__init__.py`
- `src/core/combat/qte/qte_config.py`
- `src/core/combat/qte/qte_evaluator.py`
- `src/core/combat/qte/qte_multiplier.py`
- `src/ui/components/qte_overlay.py`
- `tests/core/test_combat/test_qte/test_qte_evaluator.py`
- `tests/core/test_combat/test_qte/test_qte_multiplier.py`

**Modify**:
- `src/core/skills/skill.py` (add qte field)
- `src/core/skills/skill_effect.py` (no change, multiplier applied externally)
- `src/core/combat/action_resolver.py` (QTE hook before apply)
- `src/ui/scenes/playable_combat_scene.py` (QTE state machine)
- `data/skills/*.json` (add qte field to qualifying skills)

### 3.7 Integration Points

- **Core/UI Boundary**: The core layer defines `QteSequence` and `QteResult`
  as pure data. The UI layer handles input capture and timing. The core
  evaluator is a pure function: `evaluate_qte(sequence, inputs) -> QteResult`.
  This respects the `core/ NEVER imports ui/` rule.
- **Action Resolver**: The resolver needs a way to "pause" and wait for QTE
  input. In the UI-driven flow, this is handled by the scene state machine:
  the scene enters a QTE_ACTIVE state, captures input, then resumes action
  resolution with the QteResult.
- **AI**: Enemy skills with QTE fields auto-resolve as PERFECT (enemies don't
  do QTE -- they just get the base 1.0x multiplier, or optionally 0.8x as a
  hidden "AI penalty" to make player QTE feel rewarding).

### 3.8 Test Cases

```
test_perfect_qte_returns_130_multiplier()
  Arrange: Sequence = ["LEFT", "UP", "RIGHT"], inputs = ["LEFT", "UP", "RIGHT"].
  Act: evaluate_qte(sequence, inputs).
  Assert: QteResult(PERFECT, 3, 3, 1.30).

test_partial_qte_returns_115_multiplier()
  Arrange: Sequence = ["LEFT", "UP", "RIGHT", "DOWN"], inputs = ["LEFT", "UP", "DOWN", "LEFT"].
  Act: evaluate_qte(sequence, inputs).
  Assert: QteResult(PARTIAL, 2, 4, 1.15).

test_failure_qte_returns_090_multiplier()
  Arrange: Sequence = ["LEFT", "UP", "RIGHT", "DOWN"], inputs = ["DOWN", "DOWN", "DOWN", "DOWN"].
  Act: evaluate_qte(sequence, inputs).
  Assert: QteResult(FAILURE, 1, 4, 0.90).

test_skipped_qte_returns_100_multiplier()
  Arrange: QTE disabled in settings.
  Act: resolve skill with QTE.
  Assert: Damage equals base damage * 1.0.

test_qte_multiplier_applies_to_damage()
  Arrange: Skill deals 100 base damage, QTE result PERFECT (1.30x).
  Act: Apply QTE multiplier.
  Assert: Effective base_power = 130.

test_qte_multiplier_applies_to_heal()
  Arrange: Skill heals 50, QTE result PERFECT (1.30x).
  Act: Apply QTE multiplier.
  Assert: Effective heal_power = 65.

test_timeout_counts_remaining_keys_as_misses()
  Arrange: Sequence = 4 keys, player only presses 2 (both correct).
  Act: evaluate_qte with 2 correct + 2 timeouts.
  Assert: 2/4 correct = PARTIAL (1.15x).

test_empty_input_is_total_failure()
  Arrange: Sequence = 3 keys, inputs = [].
  Act: evaluate_qte.
  Assert: QteResult(FAILURE, 0, 3, 0.90).

test_skill_without_qte_ignores_qte_system()
  Arrange: Skill with qte=None.
  Act: Resolve skill.
  Assert: No QTE triggered, normal damage.
```

---

## 4. Enemy Synergies

### Purpose

Individual enemies with predictable AI are solvable puzzles. Enemies that
coordinate create *emergent* difficulty that scales with the number and type of
synergy partners. The player must identify the synergy, decide which link to
break first, and adapt their target priority accordingly.

### Player Experience Goal

"That Commander is buffing everyone -- if I don't kill it first, the wolves
will overwhelm me. But the wolves have pack tactics and the last one alive gets
a death frenzy. Do I kill the Commander and deal with frenzy wolves, or kill
wolves first and eat the buffs?"

### 4.1 Synergy Types

#### A. Healer + DPS (Symbiotic Pair)

```
When both are alive:
  - Healer prioritizes healing the DPS over self.
  - DPS targets the party's lowest-HP member (focus fire).
  - If DPS dies, Healer gains Desperation: +30% heal power, random targeting.
  - If Healer dies, DPS gains Frenzy: +25% ATK, -20% DEF for 3 turns.

Break-the-link decision: Kill Healer first (DPS gets temporary buff but loses
sustain) or kill DPS first (Healer becomes less effective).
```

#### B. Tank + Caster (Guardian Pair)

```
When both are alive:
  - Tank applies Taunt (redirects melee to self).
  - Caster charges a big spell every 3 turns.
  - If Tank dies, Caster panics: swaps to BACK position, uses only basic attacks.
  - If Caster dies, Tank gains Resolve: +30% DEF, stops taunting.

Break-the-link decision: Focus the Tank (slow, tanky, but Caster is free-
casting) or go around with ranged attacks to hit Caster directly.
```

#### C. Pack Tactics (Group Bonus)

```
When 2+ pack members are alive and attack the same target in the same round:
  - Each attacker after the first gets +15% damage.
  - At 3+ attacks: target gets Injury ailment (ATK debuff) for 2 turns.

When only 1 pack member remains:
  - Last Survivor: +50% ATK, +30% Speed for 3 turns (death frenzy).

Break-the-link decision: AoE to kill multiple wolves at once (prevents both
pack bonus and frenzy) or single-target the weakest first (risk frenzy).
```

#### D. Commander (Aura Buff)

```
While Commander is alive:
  - All allies gain +10% ATK and +10% DEF (aura, not a stacking buff).
  - Each round, Commander chooses one ally to give +20% Speed buff (2 turns).
  - Commander itself is BACK position, uses ranged attacks.

When Commander dies:
  - Aura ends immediately.
  - All surviving allies gain Demoralized: -15% ATK for 3 turns.

Priority target: Commander is high-value but positioned in BACK. Requires
ranged attacks or forced positioning to reach efficiently.
```

#### E. Combo Attackers (Sequential Bonus)

```
When Attacker A attacks a target, Attacker B gets Combo Ready buff:
  - If B attacks the same target next turn: +40% damage bonus.
  - If B attacks a different target: Combo Ready lost (wasted).
  - Combo Ready expires after 1 turn if not used.

Counter-play: If the party swaps the original target to BACK position, B
can't reach them with melee and the combo breaks.
```

### 4.2 Data Structure

#### Synergy Definition: `data/dungeon/enemies/synergies.json`

```json
{
  "healer_dps_pair": {
    "synergy_id": "healer_dps_pair",
    "type": "PAIR",
    "roles": {
      "healer": {
        "archetype_filter": "HEALER",
        "behavior_when_partner_alive": "prioritize_heal_partner",
        "behavior_when_partner_dead": "desperation",
        "on_partner_death_buff": {
          "stat": "HEALING_RECEIVED",
          "percent": 30.0,
          "duration": 999
        }
      },
      "dps": {
        "archetype_filter": "DPS",
        "behavior_when_partner_alive": "focus_lowest_hp",
        "behavior_when_partner_dead": "frenzy",
        "on_partner_death_buff": {
          "stat": "PHYSICAL_ATTACK",
          "percent": 25.0,
          "duration": 3
        },
        "on_partner_death_debuff": {
          "stat": "PHYSICAL_DEFENSE",
          "percent": -20.0,
          "duration": 3
        }
      }
    }
  },
  "pack_tactics": {
    "synergy_id": "pack_tactics",
    "type": "GROUP",
    "min_members": 2,
    "archetype_filter": "DPS",
    "same_target_bonus_pct": 15.0,
    "triple_attack_ailment": {
      "ailment_id": "injury",
      "base_power": 10,
      "duration": 2
    },
    "last_survivor": {
      "atk_bonus_pct": 50.0,
      "speed_bonus_pct": 30.0,
      "duration": 3
    }
  },
  "commander_aura": {
    "synergy_id": "commander_aura",
    "type": "COMMANDER",
    "commander_archetype": "CONTROLLER",
    "aura_buffs": {
      "atk_bonus_pct": 10.0,
      "def_bonus_pct": 10.0
    },
    "chosen_ally_speed_buff": {
      "percent": 20.0,
      "duration": 2
    },
    "on_commander_death": {
      "ailment_id": "injury",
      "base_power": 15,
      "duration": 3
    }
  },
  "combo_attackers": {
    "synergy_id": "combo_attackers",
    "type": "COMBO",
    "attacker_a_archetype": "DPS",
    "attacker_b_archetype": "DPS",
    "combo_damage_bonus_pct": 40.0,
    "combo_ready_duration": 1
  }
}
```

#### Encounter Template Extension

Encounter templates gain an optional `synergy_id`:

```json
{
  "medium_healer_dps": {
    "template_id": "medium_healer_dps",
    "difficulty": "MEDIUM",
    "synergy_id": "healer_dps_pair",
    "slots": [
      {"archetype": "HEALER", "synergy_role": "healer"},
      {"archetype": "DPS", "synergy_role": "dps"},
      {"archetype": "DPS"},
      {"archetype": "TANK"}
    ]
  }
}
```

### 4.3 AI Detection of Synergy Partners

The synergy system works through a `SynergyManager` that is injected into the
enemy TurnHandler at combat start:

```python
class SynergyManager:
    """Tracks synergy relationships between enemy combatants."""

    def __init__(self, synergies: list[SynergyBinding]) -> None:
        self._bindings = synergies

    def get_partner(self, combatant_name: str) -> Character | None:
        """Returns the synergy partner for a PAIR-type synergy."""

    def get_group_members(self, combatant_name: str) -> list[Character]:
        """Returns all members in the same GROUP synergy."""

    def is_commander(self, combatant_name: str) -> bool:
        """True if this combatant is the commander."""

    def on_death(self, dead_name: str) -> list[SynergyDeathEvent]:
        """Processes death of a synergy member. Returns triggered events."""
```

The AI TurnHandler receives the SynergyManager and uses it to adjust target
selection and behavior:

```python
class SynergyAwareTurnHandler:
    def execute_turn(self, context: TurnContext) -> list[CombatEvent]:
        synergy_behavior = self._synergy_manager.get_behavior(
            context.combatant.name
        )
        if synergy_behavior == "prioritize_heal_partner":
            return self._heal_partner(context)
        if synergy_behavior == "focus_lowest_hp":
            return self._attack_lowest_hp(context)
        return self._default_turn(context)
```

### 4.4 Implementation Steps

1. Create `data/dungeon/enemies/synergies.json`.
2. Create `src/core/combat/synergy/` package:
   - `synergy_config.py` (SynergyConfig, SynergyBinding dataclasses)
   - `synergy_manager.py` (SynergyManager class)
   - `synergy_loader.py` (loads from JSON)
3. Create `src/core/combat/synergy/synergy_behaviors.py`:
   - Pure functions for each synergy behavior (heal partner, focus lowest, etc.)
4. Modify enemy TurnHandler to accept SynergyManager.
5. Modify encounter builder to parse `synergy_id` and bind enemies.
6. Hook `SynergyManager.on_death()` into CombatEngine's passive system.
7. UI: Show synergy indicator icons between linked enemies.

### 4.5 Files to Create/Modify

**Create**:
- `data/dungeon/enemies/synergies.json`
- `src/core/combat/synergy/__init__.py`
- `src/core/combat/synergy/synergy_config.py`
- `src/core/combat/synergy/synergy_manager.py`
- `src/core/combat/synergy/synergy_loader.py`
- `src/core/combat/synergy/synergy_behaviors.py`
- `tests/core/test_combat/test_synergy/test_synergy_manager.py`
- `tests/core/test_combat/test_synergy/test_synergy_behaviors.py`
- `tests/core/test_combat/test_synergy/test_pack_tactics.py`

**Modify**:
- `data/dungeon/encounters/templates.json` (add synergy_id)
- `src/core/combat/dispatch_handler.py` (pass synergy context)
- `src/core/combat/combat_engine.py` (hook on_death for synergies)

### 4.6 Integration Points

- **PassiveManager**: Synergy death events (partner death buff/debuff) are
  dispatched through the existing passive system. The SynergyManager produces
  events; the PassiveManager applies them.
- **EffectManager**: Aura buffs from Commanders are applied as StatBuffs with
  source="synergy_aura" and refreshed each round while the commander lives.
- **TurnOrder**: Pack tactics detection happens after all enemies have acted in
  a round. A post-round check tallies attacks on the same target.
- **Encounter Builder**: The encounter template already has archetype slots.
  Adding `synergy_role` is a backward-compatible extension.

### 4.7 Test Cases

```
test_healer_prioritizes_healing_partner_over_self()
  Arrange: Healer at 50% HP, DPS partner at 70% HP.
  Act: Healer turn with synergy "prioritize_heal_partner".
  Assert: Healer heals DPS, not self.

test_dps_gains_frenzy_on_healer_death()
  Arrange: Healer dies.
  Act: SynergyManager.on_death("healer").
  Assert: DPS gains +25% ATK buff and -20% DEF debuff.

test_pack_tactics_bonus_on_same_target()
  Arrange: Wolf A and Wolf B both attack "Fighter" in same round.
  Act: Calculate pack bonus.
  Assert: Wolf B gets +15% damage bonus.

test_last_survivor_gets_frenzy()
  Arrange: 3 wolves, 2 die in one round.
  Act: SynergyManager processes deaths.
  Assert: Surviving wolf gets +50% ATK, +30% Speed.

test_commander_aura_applies_to_all_allies()
  Arrange: Commander alive with 3 allies.
  Act: Round start.
  Assert: All 3 allies have +10% ATK and +10% DEF buffs.

test_commander_death_removes_aura()
  Arrange: Commander dies.
  Act: SynergyManager.on_death("commander").
  Assert: All allies lose aura buffs, gain Demoralized.

test_combo_ready_buff_on_partner_attack()
  Arrange: Attacker A hits "Fighter".
  Act: Combo system check.
  Assert: Attacker B has Combo Ready buff targeting "Fighter".

test_combo_bonus_when_b_attacks_same_target()
  Arrange: B has Combo Ready for "Fighter".
  Act: B attacks "Fighter".
  Assert: B deals +40% damage.

test_combo_wasted_on_different_target()
  Arrange: B has Combo Ready for "Fighter".
  Act: B attacks "Mage" instead.
  Assert: No bonus, Combo Ready removed.

test_synergy_inactive_when_partner_not_in_encounter()
  Arrange: DPS with synergy config, but no HEALER partner in encounter.
  Act: DPS turn.
  Assert: Normal AI behavior, no synergy effects.
```

---

## 5. Rogue Free Item Use

### Purpose

The Rogue's class identity includes "uses items without spending turn" (RF07.5
and RF02.3). The `free_item_use` property already exists on the Rogue class but
is not wired into the action economy. This mechanic gives the Rogue a unique
utility niche: they can heal, cleanse, or throw damage items while still
attacking or using skills on the same turn.

### Player Experience Goal

"My Rogue uses a potion on the dying Fighter AS A FREE ACTION, then Backstabs
the boss on the same turn. No other class can do that. The Rogue is the party's
Swiss army knife."

### 5.1 Core Rules

```
Variable                | Value     | Tuning Notes
------------------------|-----------|---------------------------
free_items_per_turn     | 1         | Hard cap -- 2 would be broken
free_item_mana_cost     | normal    | Still costs mana (prevents spam)
free_item_classes       | [Rogue]   | Only Rogue gets this
free_item_action_type   | FREE      | New ActionType: costs nothing
```

### 5.2 Detailed Rules

1. At the start of the Rogue's turn, they gain 1 `FREE_ITEM` use.
2. When the Rogue selects "Item", the system checks `free_item_use`:
   - If `True` and `FREE_ITEM` not yet used this turn:
     - Item does NOT consume BONUS_ACTION.
     - `FREE_ITEM` counter is decremented.
   - If `free_item_use` is `False` (non-Rogue) or FREE_ITEM already used:
     - Item consumes BONUS_ACTION as normal.
3. The item still costs mana (this is the balancing lever -- Rogue has limited
   mana, so free items are not truly "free").
4. The Rogue can still use their BONUS_ACTION for other things (Move, skill).

### 5.3 Edge Cases

```
Edge Case                           | Resolution
------------------------------------|-------------------------------------------
Rogue uses free item then dies      | Free item effect still resolves (already applied)
Rogue uses free item on self        | Valid -- self-heal + attack in one turn
Rogue has 0 mana but item costs 0   | Valid -- 0-cost items are usable
Rogue has no items in inventory     | "Item" option still shows but is greyed out
2 Rogues in party (if ever)         | Each Rogue gets their own FREE_ITEM independently
Item that grants actions (e.g. Haste)| Resolved normally after free item use
Rogue is confused (random targeting) | Free item target is also randomized
```

### 5.4 Additional Rogue Mechanics (Bundled)

#### 5.4.1 Backstab Position Bonus

When Rogue is at BACK position and attacks a FRONT enemy:

```
Variable                | Value     | Tuning Notes
------------------------|-----------|---------------------------
backstab_damage_mult    | 1.40      | [PLACEHOLDER] - +40% damage from back
backstab_crit_bonus     | 0.15      | [PLACEHOLDER] - +15% crit chance from back
backstab_applies_to     | basic_attack, backstab_skill | Not ALL skills
```

**Rules**:
- Backstab bonus applies only when Rogue is at BACK and target is at FRONT.
- Stacks with stealth guaranteed crit (stealth crit + backstab = massive burst).
- Does NOT apply to AoE skills (Fan of Knives hits everyone equally).

**Implementation**: Check `combatant.position == BACK and target.position == FRONT`
in the damage calculation path. Apply multiplier if attacker has `backstab_bonus`
property.

#### 5.4.2 Stealth Guaranteed Crit (Already Exists)

The Rogue's stealth system already guarantees a crit on the next attack after
entering stealth. However, it is not wired into the damage calculation. The
integration point is:

```python
# In basic_attack_handler or action_resolver:
def _should_crit(attacker: Character) -> bool:
    if hasattr(attacker, 'guaranteed_crit') and attacker.guaranteed_crit:
        if hasattr(attacker, 'break_stealth'):
            attacker.break_stealth()
        return True
    return _roll_crit(attacker)
```

### 5.5 Data Structures

#### Updated: `data/classes/rogue_config.json`

```json
{
  "crit_bonus_per_dex": 0.005,
  "poison_damage_bonus": 0.15,
  "speed_bonus_pct": 0.10,
  "extra_skill_slots": 1,
  "crit_speed_boost_pct": 0.15,
  "crit_speed_boost_duration": 2,
  "free_items_per_turn": 1,
  "backstab_damage_mult": 1.40,
  "backstab_crit_bonus": 0.15,
  "backstab_requires_back_position": true
}
```

#### New: `ActionType.FREE_ITEM` (optional approach)

Instead of adding a new ActionType (which touches many files), the cleaner
approach is to bypass the economy check in the resolver:

```python
# In action_resolver.py _resolve_item():
def _resolve_item(action: PlayerAction, context: TurnContext) -> list[CombatEvent]:
    consumable = _find_consumable(action.consumable_id, context.combatant)
    if consumable is None:
        return []
    if consumable.mana_cost > context.combatant.current_mana:
        return []
    if not _try_consume_item_action(context):
        return []
    # ... rest of item resolution
```

```python
def _try_consume_item_action(context: TurnContext) -> bool:
    """Rogue: free item use. Others: costs bonus action."""
    if _has_free_item_use(context.combatant):
        return _use_free_item(context.combatant)
    return context.action_economy.use(_ITEM_ACTION_TYPE)


def _has_free_item_use(combatant: Character) -> bool:
    """Check if combatant has the free_item_use trait."""
    return getattr(combatant, 'free_item_use', False)
```

The Rogue tracks its free item usage per turn via a simple counter:

```python
class Rogue(Character):
    def __init__(self, ...):
        ...
        self._free_items_remaining: int = 0

    @property
    def free_item_use(self) -> bool:
        return self._free_items_remaining > 0

    def reset_free_items(self) -> None:
        """Called at turn start by CombatEngine."""
        self._free_items_remaining = _CONFIG.free_items_per_turn

    def consume_free_item(self) -> bool:
        """Consumes one free item use. Returns False if none left."""
        if self._free_items_remaining <= 0:
            return False
        self._free_items_remaining -= 1
        return True
```

### 5.6 Implementation Steps

1. Update `data/classes/rogue_config.json` with new fields.
2. Update `src/core/classes/rogue/rogue_config.py` to parse new fields.
3. Modify `src/core/classes/rogue/rogue.py`:
   - Add `_free_items_remaining` counter.
   - Add `reset_free_items()`, `consume_free_item()` methods.
   - Add `backstab_damage_mult` and `backstab_crit_bonus` properties.
   - Update `free_item_use` to check counter.
4. Modify `src/core/combat/action_resolver.py` `_resolve_item()`:
   - Before consuming BONUS_ACTION, check `free_item_use`.
   - If true, call `consume_free_item()` instead of `economy.use()`.
5. Modify `src/core/combat/combat_engine.py` `prepare_turn()`:
   - If combatant has `reset_free_items`, call it.
6. Modify `src/core/combat/action_resolver.py` `_resolve_basic_attack()`:
   - After damage calculation, check for backstab bonus.
   - Apply `backstab_damage_mult` if conditions met.
7. Wire stealth guaranteed crit into crit calculation path.
8. Update UI: show "FREE" badge on Item button when Rogue has free uses.

### 5.7 Files to Create/Modify

**Create**:
- `tests/core/test_classes/test_rogue/test_free_item_use.py`
- `tests/core/test_classes/test_rogue/test_backstab.py`
- `tests/core/test_classes/test_rogue/test_stealth_crit.py`

**Modify**:
- `data/classes/rogue_config.json` (add new fields)
- `src/core/classes/rogue/rogue_config.py` (parse new fields)
- `src/core/classes/rogue/rogue.py` (free item counter, backstab)
- `src/core/combat/action_resolver.py` (free item bypass, backstab mult)
- `src/core/combat/combat_engine.py` (reset free items on turn start)
- `src/core/combat/basic_attack_handler.py` (stealth crit check)
- `src/ui/components/action_panel.py` (FREE badge)

### 5.8 Integration Points

- **ActionEconomy**: The free item use does NOT add a new ActionType. It
  bypasses the economy check entirely for Rogues. This keeps ActionEconomy
  simple and avoids touching every file that uses it.
- **CombatEngine.prepare_turn()**: Calls `reset_free_items()` on the combatant
  if the method exists. This follows the existing pattern of resetting per-turn
  resources (like ActionEconomy.reset()).
- **Backstab**: Integrates with the Position system from Mechanic 1. The
  backstab bonus becomes more interesting when position swapping is tactical.
- **Stealth Crit**: Already exists as Rogue.guaranteed_crit. Just needs wiring
  into the crit resolution path in damage calculation.

### 5.9 Test Cases

```
test_rogue_uses_item_without_consuming_bonus_action()
  Arrange: Rogue with 1 free item use, bonus action available.
  Act: Resolve ITEM action.
  Assert: Item applied, bonus action still available.

test_rogue_free_item_limited_to_one_per_turn()
  Arrange: Rogue uses free item once.
  Act: Try to use item again.
  Assert: Second item requires bonus action.

test_non_rogue_item_uses_bonus_action()
  Arrange: Fighter with items.
  Act: Resolve ITEM action.
  Assert: Bonus action consumed.

test_rogue_free_item_still_costs_mana()
  Arrange: Rogue with 0 mana, item costs 5 mana.
  Act: Resolve ITEM action.
  Assert: Item not used (insufficient mana).

test_free_item_resets_each_turn()
  Arrange: Rogue used free item last turn.
  Act: prepare_turn (new turn starts).
  Assert: free_items_remaining == 1.

test_rogue_can_item_and_attack_same_turn()
  Arrange: Rogue with free item and action available.
  Act: Use free item, then basic attack.
  Assert: Both resolve successfully.

test_rogue_can_item_and_skill_same_turn()
  Arrange: Rogue with free item, action, and mana.
  Act: Use free item, then use skill.
  Assert: Both resolve, mana deducted for both.

test_backstab_bonus_from_back_position()
  Arrange: Rogue at BACK, target at FRONT.
  Act: Basic attack.
  Assert: Damage = base * 1.40.

test_backstab_no_bonus_when_rogue_at_front()
  Arrange: Rogue at FRONT, target at FRONT.
  Act: Basic attack.
  Assert: Damage = base * 1.00 (no bonus).

test_backstab_no_bonus_against_back_target()
  Arrange: Rogue at BACK, target at BACK (no front alive).
  Act: Basic attack.
  Assert: Damage = base * 1.00 (no backstab against back targets).

test_stealth_guarantees_crit()
  Arrange: Rogue enters stealth.
  Act: Basic attack.
  Assert: Attack is critical, stealth breaks.

test_stealth_breaks_after_attack()
  Arrange: Rogue in stealth, attacks.
  Act: Check stealth state after attack.
  Assert: stealth.is_active == False.

test_stealth_crit_stacks_with_backstab()
  Arrange: Rogue at BACK, in stealth, target at FRONT.
  Act: Basic attack.
  Assert: Crit damage * backstab_mult = massive burst.
```

---

## Cross-Mechanic Interaction Matrix

This table documents how the 5 mechanics interact with each other. Each cell
is marked: INTENDED (designed for), ACCEPTABLE (emergent but fine), BUG
(should not happen), or N/A (no interaction).

```
                  | Position Swap | Boss Mechanics | QTE        | Enemy Synergy | Rogue Item
------------------|---------------|----------------|------------|---------------|------------
Position Swap     | ---           | INTENDED       | N/A        | INTENDED      | INTENDED
Boss Mechanics    | INTENDED      | ---            | ACCEPTABLE | INTENDED      | N/A
QTE               | N/A           | ACCEPTABLE     | ---        | N/A           | N/A
Enemy Synergy     | INTENDED      | INTENDED       | N/A        | ---           | ACCEPTABLE
Rogue Item        | INTENDED      | N/A            | N/A        | ACCEPTABLE    | ---
```

**Key Interactions**:

1. **Position Swap + Boss Mechanics (INTENDED)**: Forced positioning skills can
   push party members out of boss field effects. Boss charged attacks may have
   positional targeting (front-only AoE).

2. **Position Swap + Enemy Synergy (INTENDED)**: Tank+Caster synergy relies on
   the Tank being at FRONT for Taunt. Forced positioning can break the synergy
   by pushing the Tank to BACK.

3. **Position Swap + Rogue Item (INTENDED)**: Backstab bonus requires Rogue at
   BACK. Rogue can use free item to heal a front-liner, then backstab from
   safety.

4. **Boss Mechanics + Enemy Synergy (INTENDED)**: Boss minions can participate
   in synergies. A boss that summons a healer minion creates a healer+boss
   synergy pair.

5. **Boss Mechanics + QTE (ACCEPTABLE)**: Boss charged attacks could optionally
   trigger a defensive QTE for the party ("press keys to brace for impact,
   reduce damage by 20%"). This is not in v1 but is an acceptable extension.

---

## Implementation Priority

Recommended order based on dependencies, player impact, and difficulty:

| Priority | Mechanic           | Effort  | Dependencies             | Player Impact |
|----------|--------------------|---------|--------------------------|---------------|
| 1        | Position Swapping  | MEDIUM  | None                     | HIGH          |
| 2        | Rogue Free Item    | LOW     | None (slight benefit from #1) | MEDIUM   |
| 3        | Advanced Boss      | HIGH    | Benefits from #1         | HIGH          |
| 4        | Enemy Synergies    | HIGH    | Benefits from #1 and #3  | HIGH          |
| 5        | QTE                | MEDIUM  | Requires UI/Pygame       | MEDIUM        |

**Rationale**:
- Position Swapping is foundational -- every other mechanic becomes more
  interesting when position is tactical.
- Rogue Free Item is small, self-contained, and immediately makes a class more
  fun to play.
- Boss Mechanics and Enemy Synergies are the biggest content expansion and
  should come after the tactical foundation (position) is solid.
- QTE requires Pygame input handling and is the most "polish" mechanic --
  it can wait until the core systems are stable.

---

## Changelog

| Version | Date       | Changes                                      |
|---------|------------|----------------------------------------------|
| 1.0     | 2026-03-29 | Initial design draft for all 5 mechanics     |
