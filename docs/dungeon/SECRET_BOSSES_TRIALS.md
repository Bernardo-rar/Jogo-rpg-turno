# Secret Bosses & Trials -- Design Document

## Design Pillars

1. **Reward mastery, not grinding**: Trial conditions test how well the player uses their party's abilities, not how long they have been playing. Every condition is achievable in a single run with deliberate play.
2. **Discovery is the reward**: The first time a player unlocks a trial, the "wait, what is THIS?" moment should be thrilling. The system is not announced or tutorialized -- it is found.
3. **Opt-in challenge**: Trials are harder than normal encounters but entirely optional. Failure has zero penalty. The player can walk away and continue their run.
4. **Cumulative excellence unlocks the ultimate test**: Completing ALL trials in a single run reveals the Secret Boss -- a final test of everything the player has learned.

---

## Player Experience Goal

The player should feel: "I cleared that combat in 2 rounds... huh, a strange symbol appeared on my map. What is that?" Then after entering the trial: "This is a completely different kind of fight. I love this." And after unlocking the Secret Boss: "Wait -- there's MORE? I have to beat this."

---

## System 3A: Trial Conditions (Achievement Tracking)

### Purpose
Track specific in-combat achievements during the run. When a condition is met N times, a trial room becomes available on the map.

### Conditions

| Trial ID | Condition | Times Required | Difficulty to Achieve | Player Fantasy |
|----------|-----------|---------------|----------------------|----------------|
| `speed_trial` | Win a combat in 2 rounds or fewer | 3 | Medium (requires strong builds) | "I am unstoppable" |
| `perfection_trial` | Win a combat where no party member took damage | 1 | Hard (requires CC, barriers, or evasion) | "Untouchable" |
| `synergy_trial` | Use all 4 party members' class skills in a single combat | 2 | Medium (requires diverse party) | "We fight as one" |
| `greed_trial` | Accumulate 300+ gold at any point during the run | 1 | Easy-Medium (requires saving gold) | "Dragon's hoard" |

**Design Note**: 4 trials, one per cardinal virtue of gameplay: offense (speed), defense (perfection), teamwork (synergy), resource management (greed). Each tests a different player skill axis.

### Tracking Data Structure

```python
@dataclass
class TrialConditionProgress:
    """Progresso de uma condicao de trial."""
    trial_id: str
    description: str
    current_count: int = 0
    required_count: int = 1
    unlocked: bool = False

@dataclass
class TrialTracker:
    """Rastreia todas as condicoes de trial durante a run."""
    conditions: dict[str, TrialConditionProgress]
    trials_completed: set[str]      # IDs of beaten trials
    secret_boss_available: bool = False
```

### When Conditions Are Checked

| Condition | Check Point | Data Source |
|-----------|------------|-------------|
| Speed Trial | After combat victory | `engine.round_number <= 2` |
| Perfection Trial | After combat victory | All party members: `current_hp == max_hp` at end of combat (no damage taken, or fully healed is NOT counted -- must be literally untouched) |
| Synergy Trial | After combat victory | Track a set of character names that used a class-specific skill during combat (via CombatEvent with `event_type == SKILL_USE`) |
| Greed Trial | After gold is awarded | `run_state.gold >= 300` |

### Perfection Trial: Precision Rules

"No damage taken" means:
- No party member's `current_hp` decreased at ANY point during the combat.
- Barrier damage does NOT count (barriers exist to absorb damage).
- DoT ticks DO count as damage taken.
- Healing back to full does NOT satisfy the condition -- the player must avoid ALL damage entirely.

**Implementation**: Track `starting_hp` for each party member at combat start. At combat end, compare `current_hp >= starting_hp` for all living members, AND no member died during combat.

### Synergy Trial: What Counts as "Class Skill"

For the initial implementation (only Fighter, Mage, Cleric implemented):
- Fighter: Any stance change or Overdrive
- Mage: Any spell (Overcharge state usage)
- Cleric: Any heal or buff skill

Future classes will register their "signature action" via a `has_used_class_skill: bool` flag on the Character or via a new `CombatEvent` marker.

### Greed Trial: When Gold Is Checked

Checked after every `run_state.gold` mutation (combat reward, treasure, event). The condition triggers the FIRST time gold reaches 300+. Spending gold below 300 afterward does not revoke the unlock.

---

## System 3B: Trial Rooms

### Purpose
Special encounter rooms that replace a normal node on the map when a trial condition is unlocked. Each trial has unique combat rules that test the skill the condition measured.

### Map Integration

When a trial is unlocked:
1. A new `MapNode` with `RoomType.TRIAL` is injected into the next unvisited layer of the map.
2. It replaces one existing node (preferably a COMBAT node, never a REST or BOSS).
3. The trial node is visually distinct on the map (special icon, pulsing glow in UI).
4. The player can choose to enter or skip it.

If multiple trials are unlocked simultaneously, only one trial node appears per layer. Remaining trials queue for subsequent layers.

### RoomType Extension

```python
class RoomType(Enum):
    COMBAT = auto()
    ELITE = auto()
    REST = auto()
    BOSS = auto()
    TREASURE = auto()
    EVENT = auto()
    CAMPFIRE = auto()
    SHOP = auto()
    TRIAL = auto()        # NEW
    SECRET_BOSS = auto()  # NEW
```

### Trial Encounter Design

Each trial has a unique rule that constrains the combat:

| Trial | Special Rule | Enemy Composition | Reward |
|-------|-------------|-------------------|--------|
| Speed Trial | **Timer: 3 rounds.** If enemies not dead in 3 rounds, trial ends (failure). No penalty. | 3 enemies with moderate HP and high regen. Must burst them down. | Relic: "Swiftblade Emblem" (+15% speed, +10% damage when combat ends in 3 rounds or fewer) |
| Perfection Trial | **Glass Cannon mode.** All party members have 1 HP for this fight. Any hit = death. Barriers and dodges work normally. | 2 enemies with high damage but low HP. Pattern-based attacks (telegraphed). | Relic: "Aegis of Perfection" (+20% dodge chance, barrier regen per turn) |
| Synergy Trial | **Locked skills.** Each party member can ONLY use their class skill (no basic attacks, no items). Must coordinate 4 different class abilities to win. | 4 enemies, each weak to a different class ability type. | Relic: "Unity Band" (+10% all stats when all 4 party members are alive) |
| Greed Trial | **Gold = HP.** Party's gold serves as a shared HP pool. Every point of damage taken subtracts from gold. If gold hits 0, trial fails. Remaining gold is kept. | 1 strong enemy that deals gold-damage. Boss-style with telegraphed big attacks. | Relic: "Midas Crown" (+25% gold gain, enemies drop gold on hit) |

### Trial Victory & Failure

**Victory**:
- Trial-specific legendary relic awarded (unique, only obtainable here).
- Trial marked as completed in `TrialTracker.trials_completed`.
- If all 4 trials completed, Secret Boss becomes available.

**Failure**:
- No penalty. No gold loss. No HP loss.
- Party returns to map at pre-trial state (HP/mana/position restored to pre-trial snapshot).
- Trial node becomes a regular COMBAT node (the opportunity is gone for this run).

### Trial Failure: State Snapshot

Before entering a trial, capture:
```python
@dataclass(frozen=True)
class PartySnapshot:
    member_states: tuple[MemberSnapshot, ...]

@dataclass(frozen=True)
class MemberSnapshot:
    name: str
    hp: int
    mana: int
    is_alive: bool
    position: Position
```

On failure, restore party to snapshot. On victory, party keeps their current state (they earned it).

---

## System 3C: Secret Boss

### Purpose
The ultimate challenge of a run. Only appears when ALL 4 trials are completed in a single run. Tests everything: speed, survival, teamwork, resource management.

### Unlock Condition

```python
def is_secret_boss_available(tracker: TrialTracker) -> bool:
    return len(tracker.trials_completed) == 4
```

When unlocked, the Secret Boss replaces the normal BOSS node at the end of the dungeon (or appears as an additional node after the normal boss -- design decision to playtest).

**Current design choice**: Secret Boss appears AFTER the normal boss. The normal boss fight still happens. The Secret Boss is a bonus encounter visible on the map only after all 4 trials are done AND the normal boss is beaten.

### Boss Design: "The Arbiter"

**Concept**: A guardian entity that tests whether the party truly mastered all four virtues. Each phase of the fight mirrors one trial.

**Phase 1 -- Speed Phase** (HP 100% to 75%):
- Arbiter has a 4-round enrage timer. If not pushed to 75% in 4 rounds, deals massive party-wide damage.
- Tests burst damage (Speed Trial callback).

**Phase 2 -- Perfection Phase** (HP 75% to 50%):
- Arbiter telegraphs attacks with a 1-turn warning icon. Attacks hit for 80% max HP.
- Players must use barriers, dodges, and position swaps to avoid.
- Tests damage avoidance (Perfection Trial callback).

**Phase 3 -- Synergy Phase** (HP 50% to 25%):
- Arbiter creates 4 shields, each vulnerable to a different damage type (physical, fire, holy, etc.).
- All 4 party members must contribute to break the shields.
- Tests teamwork (Synergy Trial callback).

**Phase 4 -- Greed Phase** (HP 25% to 0%):
- Arbiter drops gold periodically. Collecting gold (automatic) heals the party.
- But Arbiter also has an attack that scales with party gold.
- Players must balance gold accumulation vs. vulnerability.
- Tests resource management (Greed Trial callback).

### Boss Stats

| Variable | Value | Rationale |
|----------|-------|-----------|
| `HP` | 2.5x normal boss HP | [PLACEHOLDER] Needs to survive 4 phases |
| `Phase transitions` | 75%, 50%, 25% | Standard 4-phase design |
| `Base damage` | 1.5x normal boss | [PLACEHOLDER] Should require active mitigation |
| `Enrage (Phase 1)` | 4 rounds | [PLACEHOLDER] Must be achievable by a good party |

### Rewards

| Reward | Description |
|--------|-------------|
| "Arbiter's Seal" (Relic) | +15% all stats. Cosmetic glow on all party members. |
| Gold: 500g | Massive gold dump. |
| Title: "Arbiter's Champion" | Displayed on run completion screen. Persistent unlock. |
| Run Modifier unlock: "Arbiter's Challenge" | New modifier available for future runs: "Trials appear from the start. Secret Boss always available. +50% score." |

---

## System 3D: Trial Condition JSON (`data/dungeon/trials/trial_conditions.json`)

```json
{
  "speed_trial": {
    "name": "Speed Trial",
    "description": "Win 3 combats in 2 rounds or fewer",
    "condition_type": "rounds_to_win_lte",
    "threshold": 2,
    "required_count": 3,
    "unlock_message": "A strange symbol pulses on your map..."
  },
  "perfection_trial": {
    "name": "Perfection Trial",
    "description": "Win a combat with no damage taken by any party member",
    "condition_type": "zero_damage_taken",
    "threshold": 0,
    "required_count": 1,
    "unlock_message": "An ethereal door shimmers into existence..."
  },
  "synergy_trial": {
    "name": "Synergy Trial",
    "description": "All 4 party members use class skills in 2 combats",
    "condition_type": "all_class_skills_used",
    "threshold": 4,
    "required_count": 2,
    "unlock_message": "The bonds between your party glow with power..."
  },
  "greed_trial": {
    "name": "Greed Trial",
    "description": "Accumulate 300+ gold at any point",
    "condition_type": "gold_threshold",
    "threshold": 300,
    "required_count": 1,
    "unlock_message": "Golden light seeps from the walls..."
  }
}
```

### Trial Encounters JSON (`data/dungeon/trials/trial_encounters.json`)

```json
{
  "speed_trial": {
    "name": "Speed Trial: Blitz",
    "round_limit": 3,
    "special_rule": "round_limit",
    "enemies": [
      {"template_id": "speed_trial_guardian", "count": 3}
    ],
    "reward": {
      "relic_id": "swiftblade_emblem",
      "gold": 50
    }
  },
  "perfection_trial": {
    "name": "Perfection Trial: Glass Canon",
    "special_rule": "party_1hp",
    "enemies": [
      {"template_id": "perfection_trial_guardian", "count": 2}
    ],
    "reward": {
      "relic_id": "aegis_of_perfection",
      "gold": 50
    }
  },
  "synergy_trial": {
    "name": "Synergy Trial: Unity",
    "special_rule": "class_skills_only",
    "enemies": [
      {"template_id": "synergy_trial_guardian", "count": 4}
    ],
    "reward": {
      "relic_id": "unity_band",
      "gold": 50
    }
  },
  "greed_trial": {
    "name": "Greed Trial: Midas",
    "special_rule": "gold_is_hp",
    "enemies": [
      {"template_id": "greed_trial_guardian", "count": 1}
    ],
    "reward": {
      "relic_id": "midas_crown",
      "gold": 0
    }
  }
}
```

---

## Integration Points

### Existing Code Modified

| File | Change |
|------|--------|
| `src/dungeon/map/room_type.py` | Add `TRIAL` and `SECRET_BOSS` enum values |
| `src/dungeon/run/run_state.py` | Add `trial_tracker: TrialTracker` field |
| `src/dungeon/run/combat_bridge.py` | After combat victory, call `check_trial_conditions()` |
| `src/dungeon/run/run_orchestrator.py` | Add `SceneRequest.TRIAL` and `SceneRequest.SECRET_BOSS`. Route `RoomType.TRIAL` to trial scene. |
| `src/dungeon/map/map_generator.py` | After generation, hook to inject trial nodes when conditions are met |
| `src/dungeon/run/encounter_builder.py` | Add `_build_trial()` method for trial-specific encounters |

### New Code Created

| File | Purpose |
|------|---------|
| `src/dungeon/trials/__init__.py` | Package init |
| `src/dungeon/trials/trial_condition.py` | `TrialConditionProgress`, `TrialConditionType` enum |
| `src/dungeon/trials/trial_tracker.py` | `TrialTracker` -- progress tracking, condition checking |
| `src/dungeon/trials/trial_checker.py` | Pure functions: `check_speed_condition()`, `check_perfection_condition()`, etc. |
| `src/dungeon/trials/trial_encounter.py` | `TrialEncounterConfig` dataclass, `load_trial_encounters()` |
| `src/dungeon/trials/trial_reward.py` | `resolve_trial_reward()` -- awards relic + gold |
| `src/dungeon/trials/party_snapshot.py` | `PartySnapshot`, `capture_snapshot()`, `restore_snapshot()` |
| `src/dungeon/trials/trial_rules.py` | Combat rule modifiers per trial (round limit, 1HP mode, etc.) |
| `src/dungeon/trials/secret_boss.py` | `ArbiterBoss` template, phase definitions, `is_secret_boss_available()` |
| `src/ui/scenes/trial_scene.py` | Trial room UI scene |
| `data/dungeon/trials/trial_conditions.json` | Condition definitions |
| `data/dungeon/trials/trial_encounters.json` | Trial encounter configs |
| `data/dungeon/trials/trial_relics.json` | Relic reward definitions |

### System Dependencies

```
CombatBridge.after_combat()
  -> TrialTracker.check_conditions(combat_result)
     -> trial_checker.check_speed_condition(rounds)
     -> trial_checker.check_perfection_condition(party_hp_history)
     -> trial_checker.check_synergy_condition(combat_events)
  -> If condition met: TrialTracker.unlock_trial(trial_id)
     -> MapGenerator.inject_trial_node(floor_map, trial_id)

RunOrchestrator.on_scene_complete(TRIAL)
  -> If victory: TrialTracker.complete_trial(trial_id)
     -> trial_reward.resolve_trial_reward()
     -> If all 4 complete: TrialTracker.secret_boss_available = True
  -> If failure: restore_snapshot(party_snapshot)

GoldReward pipeline
  -> TrialTracker.check_greed_condition(current_gold)

EncounterBuilder
  -> _build_trial(trial_id) -> TrialEncounterConfig -> special combat setup
```

---

## Test Cases

### Unit Tests (`tests/dungeon/trials/`)

```
# trial_checker
test_speed_condition_met_when_won_in_2_rounds
test_speed_condition_not_met_when_won_in_3_rounds
test_speed_condition_requires_3_occurrences
test_perfection_condition_met_when_no_hp_lost
test_perfection_condition_not_met_when_healed_back_to_full
test_perfection_condition_not_met_when_barrier_absorbs_and_hp_drops
test_synergy_condition_met_when_all_4_use_class_skills
test_synergy_condition_not_met_when_only_3_use_skills
test_greed_condition_met_at_300_gold
test_greed_condition_not_revoked_when_gold_drops_below_300

# trial_tracker
test_initial_state_no_trials_unlocked
test_unlock_trial_after_condition_met
test_complete_trial_records_in_completed_set
test_secret_boss_available_after_all_4_trials_completed
test_secret_boss_not_available_with_3_trials

# party_snapshot
test_capture_snapshot_records_hp_mana_alive_position
test_restore_snapshot_resets_party_to_captured_state
test_restore_snapshot_revives_members_who_died_in_trial

# trial_rules
test_round_limit_rule_ends_combat_after_3_rounds
test_party_1hp_rule_sets_all_members_to_1hp
test_class_skills_only_blocks_basic_attacks
test_gold_is_hp_rule_deducts_gold_on_damage

# integration
test_win_combat_in_2_rounds_increments_speed_condition
test_accumulate_300_gold_unlocks_greed_trial
test_trial_node_injected_into_map_after_unlock
test_trial_failure_restores_party_snapshot
test_trial_victory_awards_relic
test_all_4_trials_make_secret_boss_available
```

---

## UI Design

### Trial Unlock Notification

When a trial condition is fully met, display a brief notification on the dungeon map:

```
+------------------------------------------+
|  [TRIAL UNLOCKED]                        |
|  "A strange symbol pulses on your map..."  |
|  Speed Trial available on next layer.      |
+------------------------------------------+
```

Notification fades after 3 seconds or on key press.

### Trial Node on Map

The trial node uses a distinct visual: a pulsing diamond shape (vs. circles for normal nodes) with the trial's theme color:
- Speed Trial: Yellow (lightning/speed)
- Perfection Trial: White (purity)
- Synergy Trial: Purple (unity)
- Greed Trial: Gold (wealth)

### Trial Combat UI

Same as normal combat scene but with a header banner showing the trial's special rule:

```
===== SPEED TRIAL: Defeat all enemies in 3 rounds! =====
[Round 2/3]
```

### Secret Boss UI

When the Secret Boss is revealed, the map shows a large, pulsing node after the normal boss node. The label reads "??? - The Arbiter". After entering, a unique intro screen:

```
"You have proven your speed, your precision,
 your unity, and your discipline.

 Now face the final test."

 [ENTER] Begin
```

---

## Implementation Priority (within this system)

| Priority | Component | Effort | Dependencies |
|----------|-----------|--------|--------------|
| P0 | `TrialConditionProgress` + `TrialConditionType` | Small | None |
| P0 | `trial_conditions.json` | Small | None |
| P0 | `trial_checker.py` (pure functions) | Medium | CombatPerformance, CombatEvent |
| P0 | `TrialTracker` | Medium | trial_checker, trial_conditions |
| P1 | `party_snapshot.py` | Small | Character |
| P1 | `combat_bridge.py` integration (condition checking) | Medium | TrialTracker |
| P1 | `RoomType.TRIAL` + map injection | Medium | MapGenerator, RoomType |
| P1 | `RunOrchestrator` routing for TRIAL | Small | SceneRequest |
| P2 | Trial encounter configs + `trial_rules.py` | Large | CombatEngine modifications |
| P2 | Trial scene UI | Medium | PlayableCombatScene adaptation |
| P2 | Trial reward system | Medium | Relic system (depends on item system) |
| P3 | Secret Boss design + implementation | Large | Boss system, phase_handler |
| P3 | Secret Boss UI | Medium | Boss scene |
| P3 | Post-run unlock persistence | Medium | Save system (does not exist yet) |

Build P0 first: the tracker and condition checking are pure logic, fully testable. Then P1: integrate into the run flow. P2-P3 depend on combat engine modifications and the boss system.

---

## Balance Considerations

### Trial Difficulty Curve

Trials should be harder than elite encounters but more forgiving than bosses:
- Speed Trial guardians: ~70% of boss HP each, high regen (forces burst)
- Perfection Trial guardians: ~40% of boss damage, telegraphed patterns
- Synergy Trial guardians: ~50% of boss HP each, elemental resistances
- Greed Trial guardian: ~80% of boss HP, economy-based mechanics

### Secret Boss Tuning

The Arbiter should require:
- 8-12 rounds to defeat (longer than normal boss at 5-8 rounds)
- Active use of all 4 party members (no solo carry)
- Resource management across 4 phases (mana, items, HP)
- Pattern recognition for telegraphed attacks

Expected player outcome on first attempt: ~50% win rate for a well-built party. This is intentionally tough -- it is the ultimate challenge.

### Relic Power Budget

Trial relics are strong but not game-breaking:
- Swiftblade Emblem: +15% speed is significant but not dominant
- Aegis of Perfection: +20% dodge is strong defensive option
- Unity Band: +10% all stats is broadly useful but conditional (all alive)
- Midas Crown: +25% gold is economy-focused, less combat impact
- Arbiter's Seal: +15% all stats is the best relic in the game. Intentional -- it requires beating the hardest content.
