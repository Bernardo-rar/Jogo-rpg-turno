# Adaptive Difficulty -- Design Document

## Design Pillars

1. **The game should feel challenging but fair**: Players who are struggling should get subtle help. Players who are steamrolling should face escalating pressure. Neither group should feel patronized or punished.
2. **Invisible by default**: The system adjusts behind the scenes. The player notices the game "feels right" -- not that numbers are being tweaked. Transparency is opt-in (advanced stats screen).
3. **Gradual rubber banding**: Never more than +-30% adjustment. Changes happen incrementally, not in sudden jumps. The player should never feel a difficulty spike between two consecutive encounters.
4. **Preserves player agency**: Difficulty adjustments affect enemy stats and count, never player abilities. The player's build, strategy, and skill remain the primary determinants of success.

---

## Player Experience Goal

The struggling player should feel: "That last fight was rough, but this next one feels manageable. I can recover." NOT: "The game just gave me a pity win."

The dominant player should feel: "These enemies are putting up a real fight now. I need to stay sharp." NOT: "The game is cheating to punish me for being good."

---

## Performance Tracking

### What We Track (Per Combat)

After each combat resolves, the `CombatBridge.after_combat()` pipeline records:

| Metric | How Measured | Why It Matters |
|--------|-------------|----------------|
| `party_hp_percent` | Average `current_hp / max_hp` across living party members | Core health indicator. Low = struggling, high = dominant. |
| `deaths_this_combat` | Count of party members who died during this combat | Deaths are the strongest signal of difficulty mismatch. |
| `rounds_to_win` | `engine.round_number` at combat end | Fast wins (2-3 rounds) suggest overpower. Slow wins (8+ rounds) suggest struggle. |
| `was_elite` | Boolean | Elites are expected to be harder. Weighted differently. |
| `was_boss` | Boolean | Boss fights excluded from rolling average (they are designed to be hard). |

### What We Do NOT Track

- Individual player decisions (which skills used, targeting choices). Too invasive, too complex.
- Real-time play (how long the player takes to choose). Turn time is a player preference, not a skill signal.
- Consumable usage. Players who use potions are being strategic, not struggling.

---

## Difficulty Score: The Rolling Average

### Data Structure

```python
@dataclass
class CombatPerformance:
    """Snapshot de performance de um combate."""
    party_hp_percent: float      # 0.0 to 1.0
    deaths: int                  # 0 to 4
    rounds_to_win: int           # 1+
    was_elite: bool
    was_boss: bool

@dataclass
class DifficultyTracker:
    """Rastreia performance e calcula scaling de dificuldade."""
    history: list[CombatPerformance]  # Last N combats
    current_scaling: float            # 0.70 to 1.30

    HISTORY_WINDOW: int = 5           # Rolling window size
    SCALING_MIN: float = 0.70         # Floor: -30%
    SCALING_MAX: float = 1.30         # Ceiling: +30%
    SCALING_STEP: float = 0.05        # Each adjustment moves by 5%
```

### Scoring Algorithm

After each non-boss combat, compute a **performance score** from 0.0 (terrible) to 1.0 (dominant):

```
performance = (hp_weight * avg_hp_percent)
            + (death_weight * (1 - deaths / 4))
            + (rounds_weight * rounds_factor)

Where:
  hp_weight     = 0.50  [PLACEHOLDER]
  death_weight  = 0.30  [PLACEHOLDER]
  rounds_weight = 0.20  [PLACEHOLDER]

  rounds_factor = clamp(1.0 - (rounds_to_win - TARGET_ROUNDS) / ROUNDS_RANGE, 0.0, 1.0)
  TARGET_ROUNDS = 5     [PLACEHOLDER] -- expected rounds for a normal combat
  ROUNDS_RANGE  = 6     [PLACEHOLDER] -- range before hitting extremes
```

**Interpretation**:
- Score > 0.70: Party is dominant. Nudge scaling up.
- Score 0.40 - 0.70: Party is in the sweet spot. No change.
- Score < 0.40: Party is struggling. Nudge scaling down.

### Scaling Update Rule

```python
def update_scaling(tracker: DifficultyTracker, score: float) -> float:
    if score > 0.70:
        new = tracker.current_scaling + SCALING_STEP
    elif score < 0.40:
        new = tracker.current_scaling - SCALING_STEP
    else:
        # Drift back toward 1.0 (regression to mean)
        if tracker.current_scaling > 1.0:
            new = tracker.current_scaling - (SCALING_STEP / 2)
        elif tracker.current_scaling < 1.0:
            new = tracker.current_scaling + (SCALING_STEP / 2)
        else:
            new = 1.0
    return clamp(new, SCALING_MIN, SCALING_MAX)
```

**Key design choice**: When the player is in the sweet spot, scaling drifts back toward 1.0. This prevents permanent easy/hard mode lock-in and ensures the system is always recalibrating.

### Rolling Average

Only the last `HISTORY_WINDOW` (5) combats matter. This means:
- A player who struggled early but is now playing well will see difficulty return to normal within ~3 combats.
- A player who had one lucky fight won't suddenly face a difficulty spike.

Boss fights are recorded but excluded from scoring (they are designed encounters, not baseline difficulty indicators). Elite fights are included but weighted: `elite_penalty = 0.15` is subtracted from the performance threshold comparison to account for expected higher difficulty.

---

## How Scaling Affects Encounters

### What Changes

| Scaling Range | Effect |
|--------------|--------|
| 0.70 - 0.85 (Easy) | Enemy HP: -20% to -10%. Enemy damage: -15% to -10%. No extra enemies. |
| 0.85 - 0.95 (Slight Easy) | Enemy HP: -10% to -5%. Enemy damage: -10% to -5%. |
| 0.95 - 1.05 (Neutral) | No changes. Base encounter as designed. |
| 1.05 - 1.15 (Slight Hard) | Enemy HP: +5% to +10%. Enemy damage: +5% to +10%. |
| 1.15 - 1.30 (Hard) | Enemy HP: +10% to +20%. Enemy damage: +10% to +15%. 30% chance to add 1 extra enemy. |

### Where Applied (Integration Pipeline)

The scaling is applied at the **EncounterBuilder** level, after the encounter template is resolved but before enemies are instantiated:

```
MapNode selected
  -> EncounterBuilder.build(node, rng)
    -> resolve template by difficulty
    -> [NEW] DifficultyScaler.apply(template, scaling_factor)
       -> adjust enemy stats in EnemyTemplate
       -> potentially add/remove slots
    -> EncounterFactory.create(adjusted_template, rng)
    -> return CombatSetup
```

This means:
- Encounter composition (which archetypes) is determined by the template.
- Difficulty scaling adjusts the NUMBERS (HP, damage) and potentially the COUNT.
- The player sees more/fewer enemies or tougher/weaker ones, but the encounter structure stays coherent.

### What Does NOT Change

- Boss encounters. Bosses are hand-designed and should not be auto-scaled.
- Elite encounters. Elites are already scaled by the elite modifier system.
- Room types, map layout, loot tables. Only combat difficulty changes.
- Player stats, abilities, items. The player's power curve is sacred.

---

## Transparency: Hidden vs. Visible

### Default: Hidden

The system runs invisibly. The player never sees "Difficulty: Easy" or "Scaling: 0.85x". The goal is for the game to feel naturally well-paced.

### Optional: Stats Screen (Future)

For players who want to see behind the curtain, an advanced stats screen (accessible from pause menu) could show:

```
Run Stats
  Combats Won: 7
  Deaths: 2
  Average HP After Combat: 62%
  Difficulty Trend: Slightly Harder (+10%)
```

This is P3 priority. Not needed for initial implementation.

### Why Hidden by Default

Showing difficulty scaling creates two negative outcomes:
1. Struggling players feel embarrassed seeing "Easy mode" displayed.
2. Dominant players may intentionally play worse to avoid harder encounters.

Both undermine the system's purpose. Keep it hidden.

---

## Interaction with Run Modifiers

Run modifiers that affect `damage_taken_mult` and `damage_dealt_mult` are applied AFTER adaptive scaling. The order is:

```
Base enemy stats
  * Adaptive difficulty scaling (0.7x - 1.3x on HP/damage)
  * Run modifier effects (e.g., Frail: +15% damage taken)
= Final encounter stats
```

This means:
- If the player chose a hard modifier AND is struggling, adaptive difficulty still helps.
- If the player chose an easy modifier AND is steamrolling, adaptive difficulty still pushes back.
- The two systems are independent and compose multiplicatively.

---

## Data Structures

### JSON Config (`data/dungeon/difficulty/difficulty_config.json`)

```json
{
  "history_window": 5,
  "scaling_min": 0.70,
  "scaling_max": 1.30,
  "scaling_step": 0.05,
  "neutral_zone": {"low": 0.40, "high": 0.70},
  "weights": {
    "hp_percent": 0.50,
    "deaths": 0.30,
    "rounds": 0.20
  },
  "target_rounds": 5,
  "rounds_range": 6,
  "elite_threshold_penalty": 0.15,
  "scaling_effects": {
    "hp_scale": true,
    "damage_scale": true,
    "extra_enemy_threshold": 1.15,
    "extra_enemy_chance": 0.30
  }
}
```

### Python Dataclasses

```python
# src/dungeon/difficulty/combat_performance.py
@dataclass(frozen=True)
class CombatPerformance:
    party_hp_percent: float
    deaths: int
    rounds_to_win: int
    was_elite: bool
    was_boss: bool

# src/dungeon/difficulty/difficulty_tracker.py
@dataclass
class DifficultyTracker:
    history: list[CombatPerformance] = field(default_factory=list)
    current_scaling: float = 1.0

# src/dungeon/difficulty/difficulty_config.py
@dataclass(frozen=True)
class DifficultyConfig:
    history_window: int
    scaling_min: float
    scaling_max: float
    scaling_step: float
    neutral_low: float
    neutral_high: float
    hp_weight: float
    death_weight: float
    rounds_weight: float
    target_rounds: int
    rounds_range: int
    elite_threshold_penalty: float
    extra_enemy_threshold: float
    extra_enemy_chance: float
```

---

## Integration Points

### Existing Code Modified

| File | Change |
|------|--------|
| `src/dungeon/run/run_state.py` | Add `difficulty_tracker: DifficultyTracker` field |
| `src/dungeon/run/combat_bridge.py` | After combat, call `record_combat_performance()` and `update_scaling()` |
| `src/dungeon/run/encounter_builder.py` | Pass `current_scaling` to a new `DifficultyScaler` before `EncounterFactory.create()` |

### New Code Created

| File | Purpose |
|------|---------|
| `src/dungeon/difficulty/__init__.py` | Package init |
| `src/dungeon/difficulty/combat_performance.py` | `CombatPerformance` frozen dataclass |
| `src/dungeon/difficulty/difficulty_config.py` | `DifficultyConfig` dataclass + `load_difficulty_config()` |
| `src/dungeon/difficulty/difficulty_tracker.py` | `DifficultyTracker` + `record_performance()` + `update_scaling()` |
| `src/dungeon/difficulty/difficulty_scaler.py` | `apply_scaling()` -- adjusts EnemyTemplate stats |
| `src/dungeon/difficulty/performance_scorer.py` | `score_performance()` -- pure function, CombatPerformance -> float |
| `data/dungeon/difficulty/difficulty_config.json` | Config values |

### System Dependencies

```
CombatBridge.after_combat()
  -> DifficultyTracker.record_performance(CombatPerformance)
  -> DifficultyTracker.update_scaling()

EncounterBuilder.build()
  -> DifficultyScaler.apply_scaling(template, tracker.current_scaling)
  -> EncounterFactory.create(scaled_template)

RunState
  -> DifficultyTracker (composition)
```

---

## Test Cases

### Unit Tests (`tests/dungeon/difficulty/`)

```
# performance_scorer
test_perfect_combat_scores_near_1
test_all_dead_combat_scores_near_0
test_high_hp_fast_win_scores_above_0_7
test_low_hp_slow_win_deaths_scores_below_0_4
test_elite_combat_applies_threshold_penalty
test_boss_combat_excluded_from_scoring

# difficulty_tracker
test_initial_scaling_is_1_0
test_dominant_performance_increases_scaling
test_struggling_performance_decreases_scaling
test_neutral_performance_drifts_toward_1_0
test_scaling_never_exceeds_1_3
test_scaling_never_below_0_7
test_history_window_only_keeps_last_5
test_single_bad_combat_does_not_cause_big_swing

# difficulty_scaler
test_scaling_1_0_no_changes_to_template
test_scaling_0_8_reduces_enemy_hp_and_damage
test_scaling_1_2_increases_enemy_hp_and_damage
test_scaling_above_1_15_may_add_extra_enemy
test_boss_encounters_never_scaled

# integration
test_full_flow_5_easy_wins_then_scaling_increases
test_full_flow_3_near_wipes_then_scaling_decreases
test_modifiers_compose_with_scaling_multiplicatively
```

---

## Worked Example: A Struggling Player

1. **Combat 1**: Party wins with 35% avg HP, 1 death, 7 rounds.
   - Score: 0.50 * 0.35 + 0.30 * 0.75 + 0.20 * 0.33 = 0.175 + 0.225 + 0.066 = **0.466** (neutral zone, no change)

2. **Combat 2**: Party wins with 25% avg HP, 2 deaths, 9 rounds.
   - Score: 0.50 * 0.25 + 0.30 * 0.50 + 0.20 * 0.17 = 0.125 + 0.150 + 0.034 = **0.309** (below 0.40, scaling -= 0.05)
   - Scaling: 1.00 -> **0.95**

3. **Combat 3**: Party wins with 30% avg HP, 1 death, 8 rounds.
   - Score: 0.50 * 0.30 + 0.30 * 0.75 + 0.20 * 0.25 = 0.150 + 0.225 + 0.050 = **0.425** (neutral zone, drift toward 1.0)
   - Scaling: 0.95 -> **0.975** (drift +0.025)

4. **Combat 4** (with scaling 0.975): Enemies have -2.5% HP/damage. Party wins with 50% avg HP, 0 deaths.
   - Score: **0.65** (neutral, drift toward 1.0)
   - Scaling: 0.975 -> **1.0**

The system detected struggle, gave a small assist, player recovered, system returned to neutral.

---

## Worked Example: A Dominant Player

1. **Combat 1**: 85% HP, 0 deaths, 3 rounds. Score: **0.85** -> scaling 1.0 -> **1.05**
2. **Combat 2**: 80% HP, 0 deaths, 3 rounds. Score: **0.82** -> scaling 1.05 -> **1.10**
3. **Combat 3** (scaling 1.10: +10% enemy stats): 65% HP, 0 deaths, 5 rounds. Score: **0.58** (neutral, drift)
4. **Combat 4**: Scaling 1.10 -> **1.075** (drift back toward 1.0)

The system detected dominance, pushed back, player found a challenge, system stabilized.

---

## Implementation Priority (within this system)

| Priority | Component | Effort | Dependencies |
|----------|-----------|--------|--------------|
| P0 | `CombatPerformance` dataclass | Small | None |
| P0 | `DifficultyConfig` + JSON | Small | None |
| P0 | `performance_scorer.py` | Medium | CombatPerformance |
| P0 | `DifficultyTracker` | Medium | performance_scorer, DifficultyConfig |
| P1 | `difficulty_scaler.py` | Medium | EnemyTemplate |
| P1 | `combat_bridge.py` integration | Small | DifficultyTracker, CombatPerformance |
| P1 | `encounter_builder.py` integration | Medium | DifficultyScaler |
| P2 | Run modifier interaction | Small | ModifierEffect |
| P3 | Stats screen UI | Medium | UI system |
