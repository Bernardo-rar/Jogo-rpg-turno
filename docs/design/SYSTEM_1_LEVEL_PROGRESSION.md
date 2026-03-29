# System 1: Level Progression (1-10)

## Design Document

### Design Pillars
1. **Compressed Power Fantasy** -- Levels 1-10 in a roguelite run of 8-12 rooms means every level must feel impactful.
2. **Party Cohesion** -- The whole party levels together. Roguelites do not benefit from individually tracking XP per character.
3. **Meaningful Choice** -- Attribute points force the player to decide: shore up weaknesses or double down on strengths.
4. **Never Invisible** -- Every level up must produce a tangible, felt change in combat performance.

---

### Core Decision: Party-Wide XP

**The entire party shares one XP pool.** Rationale:
- In a roguelite, managing 4 separate XP tracks is friction with no strategic depth.
- Keeping the party at the same level simplifies encounter tuning (all enemies balanced against one party level).
- The player already makes per-character decisions via attribute point distribution.

---

### XP Table (Revised for Roguelite Pacing)

The current XP table `data/progression/xp_table.json` has thresholds designed for a long RPG, not a roguelite. In a run of 8-12 rooms (approximately 5-7 combats, 1-2 elites, 1 boss), the party should reach **level 5-7** on a typical run.

| Level | Total XP Required | XP to Next | Expected Room |
|-------|------------------|------------|---------------|
| 1     | 0                | 0          | Start         |
| 2     | 30               | 30         | Room 1-2      |
| 3     | 80               | 50         | Room 2-3      |
| 4     | 160              | 80         | Room 4-5      |
| 5     | 280              | 120        | Room 5-6      |
| 6     | 440              | 160        | Room 7-8      |
| 7     | 660              | 220        | Room 8-9      |
| 8     | 940              | 280        | Room 10-11    |
| 9     | 1300             | 360        | Room 12+      |
| 10    | 1750             | 450        | Extended runs  |

**Design rationale:**
- Level 2 comes after the first combat (tutorial pacing -- immediate reward).
- Level 3 (subclass choice) comes after 2-3 combats (early enough to define build identity).
- Levels 5-7 are the "sweet spot" for a typical run length.
- Levels 8-10 are aspirational -- achieved only by fighting every combat and elite on longer paths.

---

### XP Gain Per Combat

XP is based on encounter difficulty, not individual enemy kills. This prevents AoE classes from "stealing" XP and simplifies the calculation.

| Encounter Type      | Base XP | Notes                                         |
|---------------------|---------|-----------------------------------------------|
| Normal T1 (3 mobs)  | 25      | Rooms 1-3                                     |
| Normal T2 (3-4 mobs)| 45      | Rooms 4-7                                     |
| Normal T3 (4-5 mobs)| 70      | Rooms 8-12                                    |
| Elite T1             | 50      | 2x normal                                     |
| Elite T2             | 90      | 2x normal                                     |
| Elite T3             | 140     | 2x normal                                     |
| Boss Floor 1         | 80      | Includes XP for sub-encounters                |
| Boss Floor 2         | 150     | --                                            |
| Boss Floor 3         | 250     | --                                            |

**Modifiers applied to base XP:**
- `[PLACEHOLDER] Overkill bonus`: +10% XP if combat won without any party member dying.
- `[PLACEHOLDER] Speed bonus`: +15% XP if combat won in <= 5 rounds.
- Run modifiers can multiply/reduce XP (e.g., "Scholar" modifier: +25% XP, -10% gold).

**Formula:**
```
final_xp = floor(base_xp * overkill_mult * speed_mult * run_modifier_xp_mult)
```

---

### Level Up Rewards

Every level grants automatic stat scaling (HP/Mana from existing formulas) plus attribute points on even levels and milestone events on odd levels.

| Level | Reward                                        | Physical Pts | Mental Pts |
|-------|-----------------------------------------------|-------------|------------|
| 2     | Attribute points                              | 2           | 1          |
| 3     | **Subclass choice** + 1 talent                | 0           | 0          |
| 4     | Attribute points (big)                        | 3           | 2          |
| 5     | 1 talent + new skill tier unlocked            | 0           | 0          |
| 6     | Attribute points                              | 3           | 2          |
| 7     | 1 talent                                      | 0           | 0          |
| 8     | Attribute points (big)                        | 3           | 2          |
| 9     | 1 talent                                      | 0           | 0          |
| 10    | Attribute points (capstone)                   | 4           | 3          |

**Total attribute points across a full run:**
- Physical: 2 + 3 + 3 + 3 + 4 = **15 points**
- Mental: 1 + 2 + 2 + 2 + 3 = **10 points**
- Total: **25 points** distributed over 5 level-ups

**Physical attributes** (STR, DEX, CON): Player picks how to split physical points among these 3.
**Mental attributes** (INT, WIS, CHA, MIND): Player picks how to split mental points among these 4.

This separation prevents a STR Fighter from also maxing INT, preserving class identity while allowing build variety.

---

### When Does Level Up Happen?

**Combat Reward Screen.** After winning a combat, the reward screen shows:
1. Gold earned
2. XP earned
3. Loot drops
4. **If level up occurred**: level up fanfare, then attribute distribution UI

This is consistent with the existing `SceneRequest.COMBAT_REWARD` flow. The `_on_combat_reward` handler will check if the XP gain triggered a level up and include the `LevelUpResult` in the transition data.

If a level up grants a **subclass choice** (level 3) or **talent choice** (levels 3/5/7/9), the reward screen flows into the appropriate selection screen before returning to the dungeon map.

**Flow:**
```
Combat Victory
  -> Combat Reward Scene (gold, XP, loot)
    -> [If level up] Level Up Overlay (stats gained, attribute distribution)
      -> [If level 3] Subclass Choice Scene
      -> [If talent level] Talent Choice Scene
    -> Dungeon Map
```

---

### Auto-Distribution Option

For players who do not want to manually distribute attribute points every time, offer a "Recommended" button that distributes points according to the class's `preferred_attack_type`:

- **Physical class** (Fighter, Barbarian, Paladin, Ranger, Monk, Rogue): STR/DEX/CON based on class priority.
- **Magical class** (Mage, Sorcerer, Cleric, Warlock, Druid, Bard, Artificer): INT/WIS/CHA/MIND based on class priority.

This data can be stored per class in JSON as `recommended_attributes`.

---

## Data Structures

### `data/progression/xp_table.json` (revised)
```json
{
  "xp_thresholds": [0, 30, 80, 160, 280, 440, 660, 940, 1300, 1750]
}
```

### `data/progression/attribute_points.json` (unchanged -- already correct)
```json
{
  "2":  {"physical": 2, "mental": 1},
  "3":  {"physical": 0, "mental": 0},
  "4":  {"physical": 3, "mental": 2},
  "5":  {"physical": 0, "mental": 0},
  "6":  {"physical": 3, "mental": 2},
  "7":  {"physical": 0, "mental": 0},
  "8":  {"physical": 3, "mental": 2},
  "9":  {"physical": 0, "mental": 0},
  "10": {"physical": 4, "mental": 3}
}
```

### `data/progression/xp_rewards.json` (NEW)
```json
{
  "encounter_xp": {
    "normal": {"1": 25, "2": 45, "3": 70},
    "elite":  {"1": 50, "2": 90, "3": 140},
    "boss":   {"1": 80, "2": 150, "3": 250}
  },
  "bonuses": {
    "no_death": 1.10,
    "fast_clear_rounds": 5,
    "fast_clear_mult": 1.15
  }
}
```

### `data/progression/recommended_attributes.json` (NEW)
```json
{
  "fighter":   {"physical_priority": ["STRENGTH", "CONSTITUTION", "DEXTERITY"],
                "mental_priority": ["MIND", "WISDOM", "CHARISMA", "INTELLIGENCE"]},
  "barbarian": {"physical_priority": ["STRENGTH", "CONSTITUTION", "DEXTERITY"],
                "mental_priority": ["MIND", "CHARISMA", "WISDOM", "INTELLIGENCE"]},
  "mage":      {"physical_priority": ["CONSTITUTION", "DEXTERITY", "STRENGTH"],
                "mental_priority": ["INTELLIGENCE", "MIND", "WISDOM", "CHARISMA"]},
  "cleric":    {"physical_priority": ["CONSTITUTION", "STRENGTH", "DEXTERITY"],
                "mental_priority": ["WISDOM", "MIND", "CHARISMA", "INTELLIGENCE"]},
  "paladin":   {"physical_priority": ["STRENGTH", "CONSTITUTION", "DEXTERITY"],
                "mental_priority": ["CHARISMA", "WISDOM", "MIND", "INTELLIGENCE"]},
  "rogue":     {"physical_priority": ["DEXTERITY", "CONSTITUTION", "STRENGTH"],
                "mental_priority": ["MIND", "INTELLIGENCE", "WISDOM", "CHARISMA"]},
  "ranger":    {"physical_priority": ["DEXTERITY", "STRENGTH", "CONSTITUTION"],
                "mental_priority": ["MIND", "WISDOM", "INTELLIGENCE", "CHARISMA"]},
  "bard":      {"physical_priority": ["DEXTERITY", "CONSTITUTION", "STRENGTH"],
                "mental_priority": ["CHARISMA", "WISDOM", "MIND", "INTELLIGENCE"]},
  "monk":      {"physical_priority": ["DEXTERITY", "STRENGTH", "CONSTITUTION"],
                "mental_priority": ["WISDOM", "MIND", "INTELLIGENCE", "CHARISMA"]},
  "druid":     {"physical_priority": ["CONSTITUTION", "DEXTERITY", "STRENGTH"],
                "mental_priority": ["WISDOM", "INTELLIGENCE", "MIND", "CHARISMA"]},
  "sorcerer":  {"physical_priority": ["CONSTITUTION", "DEXTERITY", "STRENGTH"],
                "mental_priority": ["MIND", "INTELLIGENCE", "CHARISMA", "WISDOM"]},
  "warlock":   {"physical_priority": ["CONSTITUTION", "DEXTERITY", "STRENGTH"],
                "mental_priority": ["CHARISMA", "MIND", "INTELLIGENCE", "WISDOM"]},
  "artificer": {"physical_priority": ["CONSTITUTION", "INTELLIGENCE", "DEXTERITY"],
                "mental_priority": ["INTELLIGENCE", "MIND", "WISDOM", "CHARISMA"]}
}
```

---

## Implementation Steps

### Step 1: Revise XP Table JSON
- Update `data/progression/xp_table.json` with roguelite-compressed thresholds.
- Write test: `test_revised_xp_table_reaches_level_5_after_typical_run`.

### Step 2: Create XP Rewards Config
- Create `data/progression/xp_rewards.json`.
- Create `src/core/progression/xp_reward_config.py` -- frozen dataclass + loader.
- Write test: `test_load_xp_rewards_from_json`.

### Step 3: Create XP Calculator
- Create `src/core/progression/xp_calculator.py` -- pure function that takes encounter type, tier, round count, deaths, and run modifiers, returns final XP.
- Write tests: `test_normal_t1_xp`, `test_elite_t2_xp`, `test_boss_xp`, `test_no_death_bonus`, `test_fast_clear_bonus`, `test_run_modifier_multiplier`.

### Step 4: Party-Level XP Tracker
- Modify `LevelUpSystem` to track a single party XP pool instead of per-character `id()`.
- New method: `gain_party_xp(party: list[Character], amount: int) -> list[LevelUpResult]`.
- Each character gets `_set_level` called. Returns list of results (one per character, all same level).
- Write tests: `test_party_levels_together`, `test_multi_level_up`.

### Step 5: Wire XP into Combat Reward
- In `src/dungeon/run/combat_bridge.py` (or a new `xp_bridge.py`), calculate XP after combat victory and call `gain_party_xp`.
- Pass `LevelUpResult` into the `SceneTransition.data` for `COMBAT_REWARD`.

### Step 6: Attribute Distribution in Reward Screen
- Extend `src/ui/scenes/combat_reward_scene.py` to show attribute distribution when `LevelUpResult` is present.
- Create `src/ui/scenes/level_up_scene.py` for the attribute distribution overlay.

### Step 7: Auto-Distribution
- Create `src/core/progression/recommended_distribution.py` -- loads priorities from JSON, distributes points greedily.
- Write test: `test_recommended_distribution_physical_fighter`.

---

## Files to Create/Modify

### Create
- `data/progression/xp_rewards.json`
- `data/progression/recommended_attributes.json`
- `src/core/progression/xp_reward_config.py`
- `src/core/progression/xp_calculator.py`
- `src/core/progression/recommended_distribution.py`
- `src/ui/scenes/level_up_scene.py`
- `tests/core/test_progression/test_xp_calculator.py`
- `tests/core/test_progression/test_party_level_up.py`
- `tests/core/test_progression/test_recommended_distribution.py`

### Modify
- `data/progression/xp_table.json` -- new thresholds
- `src/core/progression/level_up_system.py` -- add `gain_party_xp`
- `src/dungeon/run/combat_bridge.py` -- wire XP gain after combat
- `src/dungeon/run/run_orchestrator.py` -- pass level up data through transitions
- `src/ui/scenes/combat_reward_scene.py` -- show level up UI
- `tests/core/test_progression/test_level_up_system.py` -- update tests

---

## Test Strategy

| Test Category | What to Verify |
|--------------|----------------|
| XP Table     | Thresholds parse correctly; `level_for_xp` returns correct level at boundaries |
| XP Calculator| Each encounter type/tier returns expected XP; bonuses apply multiplicatively |
| Party XP     | All party members gain same level; multi-level-up works; dead members still level |
| Attribute Distribution | Physical points cannot go to mental attributes and vice versa; total matches budget |
| Auto-Distribution | Points go to highest priority attributes; remainder distributed correctly |
| Edge Cases   | 0 XP gain returns None; max level does not overflow; XP beyond level 10 is capped |

---

## Balance Simulation: Typical Run

**Scenario: 10-room run (Floor 1 only)**
- Rooms: 5 normal combats, 2 elites, 1 event, 1 rest, 1 boss
- XP: (5 x 25) + (2 x 50) + (1 x 80) = 125 + 100 + 80 = **305 XP**
- With no-death bonus on 3 fights: 305 * ~1.03 average = ~314 XP
- Level reached: **Level 4** (280 threshold, next at 440)

**Scenario: 12-room aggressive run**
- Rooms: 6 normal combats, 3 elites, 1 event, 1 campfire, 1 boss
- XP: (6 x 25) + (3 x 50) + (1 x 80) = 150 + 150 + 80 = **380 XP**
- With bonuses: ~400 XP
- Level reached: **Level 5** (280 threshold, 440 is close)

This feels right: a typical run gets to level 4-5, an aggressive run pushes to 5-6, and only multi-floor extended runs reach 7+.
