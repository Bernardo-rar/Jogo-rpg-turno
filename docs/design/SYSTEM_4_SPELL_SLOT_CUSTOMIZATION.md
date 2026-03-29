# System 4: Spell Slot Customization

## Design Document

### Design Pillars
1. **Build Expression** -- The spell loadout is how the player expresses their strategy before combat begins. It is the pre-combat decision that matters most.
2. **Budget, Not Quantity** -- Slots have a cost budget, not a count limit. A player can fill one slot with a single powerful skill OR multiple weaker skills.
3. **Respect the Run** -- In a roguelite, re-customization opportunities are limited. Players think carefully about loadouts.
4. **Progressive Unlock** -- Not all skills are available from level 1. Higher-level skills unlock as the party levels up, rewarding progression.

---

### How the Spell Slot System Works

Each character has a **Skill Bar** composed of **Spell Slots**. Each slot has a **cost budget** (max_cost). Skills have a **slot_cost**. The player fills slots by placing skills whose total slot_cost does not exceed the slot's max_cost.

**Current system (already implemented):**
- `SpellSlot(max_cost=N)` -- a slot with budget N.
- `Skill.slot_cost` -- how much budget a skill consumes.
- `fits_in_slot()` / `add_skill_to_slot()` -- pure functions for validation.
- `SkillBar(slots=...)` -- aggregates slots.
- `SkillSlotsCalculator` -- determines number of slots from INT thresholds.

**What is missing:**
1. A UI and flow for the player to customize skill loadouts.
2. Rules for when customization is allowed.
3. Progressive unlock of skills based on level.
4. Slot budget scaling with level.
5. Separation of class skills, subclass skills, and universal skills in the skill pool.

---

### Slot Count and Budget

**Number of Slots:** BASE_SKILL_SLOTS (3) + INT threshold bonuses (currently implemented).

| INT Threshold | Bonus Slots |
|--------------|-------------|
| 18           | +1          |
| 22           | +1          |
| 26           | +1          |

So a character can have 3 to 6 skill slots depending on INT.

**Slot Budget per Slot (scales with level):**

| Level | Budget per Slot | Total Budget (3 slots) | Total Budget (6 slots) |
|-------|----------------|----------------------|----------------------|
| 1     | 8              | 24                   | 48                   |
| 2     | 9              | 27                   | 54                   |
| 3     | 10             | 30                   | 60                   |
| 4     | 11             | 33                   | 66                   |
| 5     | 12             | 36                   | 72                   |
| 6     | 13             | 39                   | 78                   |
| 7     | 14             | 42                   | 84                   |
| 8     | 15             | 45                   | 90                   |
| 9     | 16             | 48                   | 96                   |
| 10    | 18             | 54                   | 108                  |

**Formula:**
```
slot_budget = 8 + (level - 1) + (1 if level >= 10 else 0)
```

This means a level 1 character with 3 slots has 24 total budget. A level 10 character with 6 slots has 108 total budget. The growth is significant but not exponential.

**Design rationale:** Budget scaling lets players equip higher slot_cost skills as they level, matching the intended progression from RF06.2 (early: basic attacks, mid: AoE, late: devastating skills).

---

### Skill Pool Composition

A character's available skill pool is the union of:

1. **Universal Skills** -- from `data/skills/skills.json` (fireball, ice_bolt, minor_heal, etc.). Available to all classes.
2. **Class Skills** -- from `data/skills/<class_id>.json`. Only available to that class.
3. **Subclass Skills** -- from `data/subclasses/skills/<subclass_id>.json`. Only available after choosing that subclass (level 3+).

**Level Restriction:** A skill is only available if `character.level >= skill.required_level`.

**Pool at each stage:**

| Stage | Available Skills |
|-------|-----------------|
| Level 1 (start) | Universal (req_level <= 1) + Class (req_level <= 1) |
| Level 2 | Universal (req_level <= 2) + Class (req_level <= 2) |
| Level 3+ (subclass chosen) | Universal + Class + Subclass (all req_level <= current) |
| Level 5+ | Full pool including high-level skills |

---

### When Can Players Customize?

Spell loadout customization is available at these specific moments:

1. **Before the run starts** (Party Selection screen) -- initial loadout.
2. **At Campfire rooms** -- one of the campfire options is "Retune Skills."
3. **At Rest rooms** -- if the player chooses the "Meditate" option, they can also retune.
4. **After level up** -- the level up screen offers an optional "Retune Skills" step after attribute/talent distribution.

Customization is **not** available:
- During combat.
- At shop rooms (shop is for items, not skills).
- At event rooms (events are narrative, not build).
- Between individual combats (too frequent, slows pacing).

**Design rationale:** Limited customization windows make the initial loadout decision important. The player cannot trivially swap to the "correct" build for each fight. Campfire and rest rooms become more valuable as retune points.

---

### UI Flow: Skill Loadout Screen

```
+------------------------------------------------------+
|  SKILL LOADOUT - [Character Name] (Level X)          |
|------------------------------------------------------|
|                                                      |
|  SLOT 1 [Budget: 8/10]        SLOT 2 [Budget: 6/10] |
|  +------------------+         +------------------+   |
|  | Fire Bolt (3)    |         | Backstab (4)     |   |
|  | Ice Lance (3)    |         | Cheap Shot (3)   |   |
|  | [+ Add Skill]    |         | [+ Add Skill]    |   |
|  +------------------+         +------------------+   |
|                                                      |
|  SLOT 3 [Budget: 3/10]        (SLOT 4 locked-INT 18) |
|  +------------------+         +------------------+   |
|  | Vanish (3)       |         |     [LOCKED]     |   |
|  | [+ Add Skill]    |         |                  |   |
|  +------------------+         +------------------+   |
|                                                      |
|  AVAILABLE SKILLS                                    |
|  +------------------------------------------------+  |
|  | [Class Skills]                                  |  |
|  |   Power Strike (4) | Second Wind (3) | ...     |  |
|  | [Universal Skills]                              |  |
|  |   Fireball (5)  | Minor Heal (3) | ...         |  |
|  | [Subclass Skills]  (unlocked at level 3)        |  |
|  |   Assassinate (6) | Shadow Step (2) | ...      |  |
|  +------------------------------------------------+  |
|                                                      |
|  [Confirm]  [Reset to Default]  [Auto-Fill]          |
+------------------------------------------------------+
```

**Interactions:**
1. Select a slot to edit.
2. From available skills list, click a skill to add it to the selected slot (if budget allows).
3. Click a skill in a slot to remove it.
4. "Reset to Default" restores the pre-built loadout for that class/level.
5. "Auto-Fill" uses a heuristic to fill all slots optimally.
6. "Confirm" saves the loadout.

**Keyboard shortcuts** (consistent with RF10.3):
- Number keys 1-6 to select a slot.
- Arrow keys to browse available skills.
- Enter to add/remove.
- Esc to cancel.

---

### Default Loadouts

Each class has a **default loadout** defined in JSON that is used when:
- The run starts (initial loadout).
- The player clicks "Reset to Default."

Default loadouts are tuned per level tier so the game is playable without manual customization.

---

### Reaction Skills and Passive Skills

**Reactions** and **Passives** occupy a special slot:
- Each character has **1 Reaction Slot** (always available, not tied to INT).
- Passives are **always active** once placed and do not consume a slot budget -- they are equipped separately.

This separates the decision space:
- Main slots: offensive and support skills (actions + bonus actions).
- Reaction slot: defensive/counter skills.
- Passive slot: always-on effects.

**Reaction slot budget:** same as a regular slot (scales with level).
**Passive limit:** 2 passives max (prevents stacking too many passives).

---

### Auto-Fill Heuristic

For players who do not want to manually customize, the auto-fill algorithm:

1. Start with the class's default loadout for the character's current level.
2. If subclass is chosen, replace lowest-priority skills with subclass skills.
3. Fill remaining budget with highest slot_cost skills that fit (greedy).
4. Always place at least one healing skill if available (for Cleric/Paladin/Druid).
5. Always equip a reaction skill in the reaction slot.

---

## Data Structures

### `data/progression/slot_config.json` (NEW)
```json
{
  "base_slot_budget": 8,
  "budget_per_level": 1,
  "level_10_bonus": 1,
  "base_slot_count": 3,
  "max_slot_count": 6,
  "reaction_slots": 1,
  "passive_limit": 2,
  "budget_formula_description": "slot_budget = base_slot_budget + (level - 1) * budget_per_level + (level_10_bonus if level >= 10)"
}
```

### `data/skills/default_loadouts.json` (NEW)
```json
{
  "fighter": {
    "level_1": {
      "slots": [
        ["power_strike", "second_wind"],
        ["stance_offensive"],
        ["action_surge"]
      ],
      "reaction": ["parry"],
      "passives": ["iron_will"]
    },
    "level_3": {
      "slots": [
        ["power_strike", "second_wind"],
        ["stance_offensive", "action_surge"],
        ["mighty_blow"]
      ],
      "reaction": ["parry"],
      "passives": ["iron_will", "improved_critical"]
    }
  },
  "mage": {
    "level_1": {
      "slots": [
        ["fire_bolt", "ice_lance"],
        ["arcane_barrier"],
        ["overcharge_toggle"]
      ],
      "reaction": ["mana_shield"],
      "passives": []
    }
  },
  "cleric": {
    "level_1": {
      "slots": [
        ["holy_heal", "blessing"],
        ["divine_smite"],
        ["channel_divinity"]
      ],
      "reaction": ["divine_shield"],
      "passives": []
    }
  }
}
```

(Entries for all 13 classes, with level_1 and level_3 variants at minimum.)

### Extended `Skill` Fields (already exists, no change needed)
The existing `Skill` dataclass already has all needed fields:
- `slot_cost`, `required_level`, `class_id`, `action_type`, `reaction_trigger`, `reaction_mode`

---

## Implementation Steps

### Step 1: Slot Config
- Create `data/progression/slot_config.json`.
- Create `src/core/skills/slot_config.py` -- frozen dataclass + loader.
- Create `src/core/skills/slot_budget_calculator.py` -- pure function: `(level, config) -> budget_per_slot`.
- Test: budget at levels 1, 5, 10 matches expected values.

### Step 2: Skill Pool Builder
- Create `src/core/skills/skill_pool_builder.py`:
  - `build_skill_pool(class_id, subclass_id, level) -> list[Skill]`
  - Loads universal + class + subclass skills, filters by required_level.
- Test: pool grows with level; subclass skills only appear after subclass chosen.

### Step 3: Loadout Manager
- Create `src/core/skills/loadout_manager.py`:
  - `LoadoutManager` class with methods:
    - `add_skill_to_slot(slot_index, skill) -> bool`
    - `remove_skill_from_slot(slot_index, skill_id) -> bool`
    - `set_reaction(skill) -> bool`
    - `add_passive(skill) -> bool`
    - `validate_loadout() -> list[str]` (returns list of errors)
    - `get_loadout() -> SkillBar`
  - Validates: budget constraints, class restrictions, level requirements, no duplicate skills across slots.
- Test: budget overflow rejected; class skill on wrong class rejected; duplicate rejected.

### Step 4: Default Loadout Loader
- Create `data/skills/default_loadouts.json` with entries for all 13 classes.
- Create `src/core/skills/default_loadout_loader.py`.
- Test: default loadout for each class is valid (passes validate_loadout).

### Step 5: Auto-Fill
- Create `src/core/skills/auto_fill.py`:
  - `auto_fill_loadout(pool, slot_count, budget, subclass_skills) -> SkillBar`
- Test: auto-fill produces valid loadout; includes healing for support classes.

### Step 6: UI -- Loadout Screen
- Create `src/ui/scenes/loadout_scene.py`:
  - Grid layout showing slots, available skills, and controls.
  - Keyboard-first navigation (slot selection by number, skill browsing by arrows).
- Wire into: party select scene (initial loadout), campfire actions, rest actions, level up flow.

### Step 7: Wire Customization Points
- Modify `src/dungeon/run/campfire_actions.py` -- add "Retune Skills" option.
- Modify `src/dungeon/run/rest_actions.py` -- add "Meditate (Retune)" option.
- Modify level-up flow -- after attribute/talent distribution, offer optional retune.
- Add `SceneRequest.LOADOUT` to `RunOrchestrator`.

### Step 8: Save/Load Loadout State
- Loadout state must persist through the run (it is part of run state, not global state).
- Store as part of `RunState` (or equivalent data structure for the dungeon run).

---

## Files to Create/Modify

### Create
- `data/progression/slot_config.json`
- `data/skills/default_loadouts.json`
- `src/core/skills/slot_config.py`
- `src/core/skills/slot_budget_calculator.py`
- `src/core/skills/skill_pool_builder.py`
- `src/core/skills/loadout_manager.py`
- `src/core/skills/default_loadout_loader.py`
- `src/core/skills/auto_fill.py`
- `src/ui/scenes/loadout_scene.py`
- `tests/core/test_skills/test_slot_budget_calculator.py`
- `tests/core/test_skills/test_skill_pool_builder.py`
- `tests/core/test_skills/test_loadout_manager.py`
- `tests/core/test_skills/test_auto_fill.py`

### Modify
- `src/core/skills/skill_bar.py` -- add reaction slot and passive slots
- `src/core/skills/spell_slot.py` -- no changes needed (already correct)
- `src/dungeon/run/campfire_actions.py` -- add retune option
- `src/dungeon/run/rest_actions.py` -- add retune option
- `src/dungeon/run/run_orchestrator.py` -- add `LOADOUT` scene transition
- `src/ui/scenes/combat_reward_scene.py` -- optional retune after level up

---

## Test Strategy

| Test Category | What to Verify |
|--------------|----------------|
| Budget Calculator | Budget scales correctly with level; level 10 bonus applies |
| Skill Pool | Correct skills in pool per class/level; subclass skills absent pre-level 3 |
| Loadout Manager | Budget overflow rejected; class mismatch rejected; duplicates rejected |
| Default Loadout | Every class's default loadout passes validation |
| Auto-Fill | Produces valid loadout; prioritizes higher slot_cost skills; includes reaction |
| Reaction/Passive | Only 1 reaction; max 2 passives; separate from main slots |
| Integration | Loadout changes at campfire persist into next combat |

---

## Balance Notes

### Slot Cost Distribution of Existing Skills

| Slot Cost | Count | Examples |
|-----------|-------|---------|
| 2         | 5     | Stance toggles, Meditate, Lullaby |
| 3         | 28    | Most basic attacks, buffs, reactions |
| 4         | 18    | Mid-tier attacks, heals, class mechanics |
| 5         | 10    | Strong AoE, Haste, key class skills |
| 6         | 6     | Chain Lightning, Dragon Breath, Inferno |
| 7         | 3     | Channel Divinity, Glimpse of Glory, Spell Surge |
| 8         | 6     | Legend, Blood Frenzy, Grand Finale, Hundred Fists |
| 12        | 1     | Revive |

**At level 1 (budget 8 per slot, 3 slots):**
- A slot can hold: 1 cost-8 skill, or 2 cost-4 skills, or 1 cost-5 + 1 cost-3, etc.
- Total budget: 24. Enough for approximately 6-8 skills across 3 slots.
- Cannot equip Revive (cost 12) at level 1 -- slot budget too small. This is intentional.

**At level 5 (budget 12 per slot, 3-4 slots):**
- Can now equip Revive in a slot.
- Total budget: 36-48. Can equip 9-12 skills.
- Full build diversity opens up.

**At level 10 (budget 18 per slot, 3-6 slots):**
- Total budget: 54-108. The player has vastly more options than they can use.
- This is the "spam" phase from RF06.2.

### Why Budget Per Slot, Not Total Budget?

A single global budget would let the player stack all expensive skills into one "nuke slot" and leave others empty. Per-slot budgets force distribution across multiple slots, which means multiple combat options -- encouraging varied play rather than one-button strategies.
