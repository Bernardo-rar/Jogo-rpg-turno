# System 3: Talent System

## Design Document

### Design Pillars
1. **Build Customization Layer** -- Talents are the "fine tuning" after class and subclass define the broad strokes.
2. **Pick 1 of 3** -- Every talent choice presents exactly 3 options. No overwhelming walls of text.
3. **No Traps** -- All talents must be viable. No "+2% damage" next to "+50% HP regen."
4. **Cross-Class Synergy** -- Universal talents let any class access niche strategies that their kit does not provide.

---

### Talent Choice Timing

| Level | Talent? | Context |
|-------|---------|---------|
| 3     | Yes     | First talent -- chosen alongside subclass |
| 5     | Yes     | Second talent -- mid-run power spike |
| 7     | Yes     | Third talent -- late-run specialization |
| 9     | Yes     | Fourth talent -- capstone synergy |

At each talent level, the player is offered **3 random talents from a curated pool** (not all talents every time). The pool is filtered by:
1. Talents the character has not already chosen.
2. Talents that are compatible with the character's class/subclass (some are restricted).
3. At least 1 talent from each category (Offensive, Defensive, Utility) per offering.

A typical run reaches level 5-6, so most characters will have 1-2 talents. Aggressive runs reaching level 9 get the full 4 talents -- a reward for seeking out combat.

---

### Talent Categories

**Offensive (O):** Increase damage output, crit performance, or action economy.
**Defensive (D):** Increase survivability, healing, or damage reduction.
**Utility (U):** Provide economy benefits, skill flexibility, or unique mechanics.

---

### Universal Talents (Available to All Classes)

| # | Name | Cat | Effect | Tuning Notes |
|---|------|-----|--------|-------------|
| 1 | Brutal Strikes | O | +15% physical damage | [PLACEHOLDER] test at +10% and +20% |
| 2 | Arcane Potency | O | +15% magical damage | Mirror of Brutal Strikes for casters |
| 3 | Critical Edge | O | +10% crit chance, +0.25x crit multiplier | Strong for Ranger/Rogue/Champion |
| 4 | Relentless | O | After killing an enemy, gain +1 bonus action (1/turn) | Snowball talent, strong in AoE fights |
| 5 | Executioner | O | +25% damage against enemies below 30% HP | Pairs with Assassin, Ranger |
| 6 | Thick Skin | D | +15% max HP | Simple, always useful |
| 7 | Iron Will | D | +15% physical and magical defense | Naming conflict with Fighter passive -- rename to "Fortitude" if needed |
| 8 | Regenerator | D | HP regen doubled (+100% HP regen per turn) | Strong for Barbarian, Paladin |
| 9 | Second Chance | D | Once per combat, survive a fatal hit with 1 HP | Angel Idol effect as a talent |
| 10 | Elemental Shield | D | Reduce elemental damage taken by 20% | Counters Evokers and elemental bosses |
| 11 | Quick Learner | U | +25% XP gained | Only useful early (level 3-5), diminishing returns |
| 12 | Deep Pockets | U | +20% gold from all sources | Economy talent |
| 13 | Resourceful | U | +15% mana regen per turn. Skill cooldowns reduced by 1 | Enables spam builds |
| 14 | Combat Meditation | U | At start of combat, restore 15% mana and remove 1 ailment | Sustain between fights |
| 15 | Versatile Fighter | U | Can equip 1 additional accessory slot | Build diversity |

---

### Class-Restricted Talents (Appear Only for Specific Classes)

| # | Name | Cat | Class(es) | Effect |
|---|------|-----|-----------|--------|
| 16 | Weapon Mastery | O | Fighter, Barbarian, Paladin, Ranger | Basic attack damage +30%, basic attacks generate 50% more class resource |
| 17 | Mana Surge | O | Mage, Sorcerer, Warlock, Cleric, Druid | When casting a spell, 20% chance to refund its mana cost |
| 18 | Shadow Affinity | O | Rogue, Monk, Warlock | +20% damage from stealth/backstab. +10% dodge chance |
| 19 | Holy Fervor | O | Cleric, Paladin | Holy damage +25%. Healing generates +1 of class resource (Holy Power / Divine Favor) |
| 20 | Beast Bond | O | Ranger (Beastmaster), Druid | Summoned creatures deal +30% damage and have +20% HP |
| 21 | Aura Master | D | Paladin, Bard | Aura/buff effects +25% potency. Buff durations +1 turn |
| 22 | Berserker's Vitality | D | Barbarian | While above 50 Fury, regen 3% max HP per turn |
| 23 | Arcane Absorption | D | Mage, Sorcerer, Artificer | When hit by a spell, restore 10% of damage taken as mana |
| 24 | Song of Rest | U | Bard | At the end of each combat, all allies heal 10% max HP |
| 25 | Mechanical Efficiency | U | Artificer | All item/consumable costs (mana/gold) -25% |

Total: **25 talents** (15 universal + 10 class-restricted).

---

### Offering Algorithm

When a character reaches a talent level, the system:

1. Build the **eligible pool**: all talents not yet chosen, not restricted away from this class.
2. Ensure **category diversity**: pick at least 1 from each of the 3 categories present in the pool.
3. Fill remaining slots randomly from the pool.
4. Present exactly 3 choices.

If fewer than 3 eligible talents remain (highly unlikely with 25 options and max 4 picks), show all remaining.

**Pseudocode:**
```
def generate_offering(character, all_talents, chosen_ids):
    eligible = [t for t in all_talents if t.id not in chosen_ids
                and character.class_id in t.allowed_classes]
    by_cat = group_by(eligible, key=lambda t: t.category)
    picks = []
    for cat in [OFFENSIVE, DEFENSIVE, UTILITY]:
        if cat in by_cat and len(picks) < 3:
            picks.append(random.choice(by_cat[cat]))
            by_cat[cat].remove(picks[-1])
    remaining = flatten(by_cat.values())
    while len(picks) < 3 and remaining:
        pick = random.choice(remaining)
        picks.append(pick)
        remaining.remove(pick)
    return picks
```

---

### Talent Effect Implementation

Talents are implemented as **passive modifiers** that are applied once when chosen and persist for the entire run. They hook into the existing `EffectManager` and stat modifier system.

| Effect Type | Implementation |
|------------|---------------|
| Stat % modifier | `StatBuff` with infinite duration applied to character |
| Conditional damage | New `TalentModifier` protocol checked during damage calculation |
| Triggered effect | New hook in combat engine: `on_kill`, `on_crit`, `on_combat_start` |
| Economy modifier | Stored on run state, checked by gold calculator |
| Cooldown reduction | Applied when skill bar is initialized / updated |

---

## Data Structure

### `data/progression/talents.json`
```json
{
  "brutal_strikes": {
    "talent_id": "brutal_strikes",
    "name": "Brutal Strikes",
    "description": "+15% physical damage dealt",
    "category": "OFFENSIVE",
    "allowed_classes": ["ALL"],
    "effects": [
      {"type": "STAT_MODIFIER", "stat": "PHYSICAL_ATTACK", "modifier_type": "PERCENT", "value": 15}
    ],
    "icon": "sword_red"
  },
  "arcane_potency": {
    "talent_id": "arcane_potency",
    "name": "Arcane Potency",
    "description": "+15% magical damage dealt",
    "category": "OFFENSIVE",
    "allowed_classes": ["ALL"],
    "effects": [
      {"type": "STAT_MODIFIER", "stat": "MAGICAL_ATTACK", "modifier_type": "PERCENT", "value": 15}
    ],
    "icon": "orb_blue"
  },
  "critical_edge": {
    "talent_id": "critical_edge",
    "name": "Critical Edge",
    "description": "+10% crit chance, +0.25x crit multiplier",
    "category": "OFFENSIVE",
    "allowed_classes": ["ALL"],
    "effects": [
      {"type": "CRIT_MODIFIER", "crit_chance_bonus": 0.10, "crit_mult_bonus": 0.25}
    ],
    "icon": "dagger_gold"
  },
  "relentless": {
    "talent_id": "relentless",
    "name": "Relentless",
    "description": "After killing an enemy, gain +1 bonus action (1/turn)",
    "category": "OFFENSIVE",
    "allowed_classes": ["ALL"],
    "effects": [
      {"type": "ON_KILL_TRIGGER", "grant": "BONUS_ACTION", "limit_per_turn": 1}
    ],
    "icon": "skull_red"
  },
  "executioner": {
    "talent_id": "executioner",
    "name": "Executioner",
    "description": "+25% damage against enemies below 30% HP",
    "category": "OFFENSIVE",
    "allowed_classes": ["ALL"],
    "effects": [
      {"type": "CONDITIONAL_DAMAGE", "condition": "TARGET_BELOW_HP_PCT", "threshold": 0.30, "damage_bonus_pct": 25}
    ],
    "icon": "axe_red"
  },
  "thick_skin": {
    "talent_id": "thick_skin",
    "name": "Thick Skin",
    "description": "+15% max HP",
    "category": "DEFENSIVE",
    "allowed_classes": ["ALL"],
    "effects": [
      {"type": "STAT_MODIFIER", "stat": "MAX_HP", "modifier_type": "PERCENT", "value": 15}
    ],
    "icon": "shield_green"
  },
  "fortitude": {
    "talent_id": "fortitude",
    "name": "Fortitude",
    "description": "+15% physical and magical defense",
    "category": "DEFENSIVE",
    "allowed_classes": ["ALL"],
    "effects": [
      {"type": "STAT_MODIFIER", "stat": "PHYSICAL_DEFENSE", "modifier_type": "PERCENT", "value": 15},
      {"type": "STAT_MODIFIER", "stat": "MAGICAL_DEFENSE", "modifier_type": "PERCENT", "value": 15}
    ],
    "icon": "armor_green"
  },
  "regenerator": {
    "talent_id": "regenerator",
    "name": "Regenerator",
    "description": "HP regen per turn doubled",
    "category": "DEFENSIVE",
    "allowed_classes": ["ALL"],
    "effects": [
      {"type": "STAT_MODIFIER", "stat": "HP_REGEN", "modifier_type": "PERCENT", "value": 100}
    ],
    "icon": "heart_green"
  },
  "second_chance": {
    "talent_id": "second_chance",
    "name": "Second Chance",
    "description": "Once per combat, survive a fatal hit with 1 HP",
    "category": "DEFENSIVE",
    "allowed_classes": ["ALL"],
    "effects": [
      {"type": "DEATH_PREVENTION", "uses_per_combat": 1, "hp_after": 1}
    ],
    "icon": "angel_green"
  },
  "elemental_shield": {
    "talent_id": "elemental_shield",
    "name": "Elemental Shield",
    "description": "Reduce elemental damage taken by 20%",
    "category": "DEFENSIVE",
    "allowed_classes": ["ALL"],
    "effects": [
      {"type": "DAMAGE_REDUCTION", "damage_category": "ELEMENTAL", "reduction_pct": 20}
    ],
    "icon": "crystal_green"
  },
  "quick_learner": {
    "talent_id": "quick_learner",
    "name": "Quick Learner",
    "description": "+25% XP gained",
    "category": "UTILITY",
    "allowed_classes": ["ALL"],
    "effects": [
      {"type": "XP_MODIFIER", "bonus_pct": 25}
    ],
    "icon": "book_yellow"
  },
  "deep_pockets": {
    "talent_id": "deep_pockets",
    "name": "Deep Pockets",
    "description": "+20% gold from all sources",
    "category": "UTILITY",
    "allowed_classes": ["ALL"],
    "effects": [
      {"type": "GOLD_MODIFIER", "bonus_pct": 20}
    ],
    "icon": "coin_yellow"
  },
  "resourceful": {
    "talent_id": "resourceful",
    "name": "Resourceful",
    "description": "+15% mana regen. All cooldowns reduced by 1 turn",
    "category": "UTILITY",
    "allowed_classes": ["ALL"],
    "effects": [
      {"type": "STAT_MODIFIER", "stat": "MANA_REGEN", "modifier_type": "PERCENT", "value": 15},
      {"type": "COOLDOWN_REDUCTION", "flat": 1}
    ],
    "icon": "gem_yellow"
  },
  "combat_meditation": {
    "talent_id": "combat_meditation",
    "name": "Combat Meditation",
    "description": "At combat start, restore 15% mana and remove 1 ailment",
    "category": "UTILITY",
    "allowed_classes": ["ALL"],
    "effects": [
      {"type": "ON_COMBAT_START", "restore_mana_pct": 15, "cleanse_count": 1}
    ],
    "icon": "lotus_yellow"
  },
  "versatile_fighter": {
    "talent_id": "versatile_fighter",
    "name": "Versatile Fighter",
    "description": "Can equip 1 additional accessory",
    "category": "UTILITY",
    "allowed_classes": ["ALL"],
    "effects": [
      {"type": "EQUIPMENT_SLOT", "slot_type": "ACCESSORY", "bonus_slots": 1}
    ],
    "icon": "ring_yellow"
  },
  "weapon_mastery": {
    "talent_id": "weapon_mastery",
    "name": "Weapon Mastery",
    "description": "Basic attack +30% damage, generates 50% more class resource",
    "category": "OFFENSIVE",
    "allowed_classes": ["fighter", "barbarian", "paladin", "ranger"],
    "effects": [
      {"type": "BASIC_ATTACK_MODIFIER", "damage_bonus_pct": 30, "resource_gen_bonus_pct": 50}
    ],
    "icon": "sword_gold"
  },
  "mana_surge": {
    "talent_id": "mana_surge",
    "name": "Mana Surge",
    "description": "20% chance to refund spell mana cost after casting",
    "category": "OFFENSIVE",
    "allowed_classes": ["mage", "sorcerer", "warlock", "cleric", "druid"],
    "effects": [
      {"type": "ON_CAST_TRIGGER", "chance": 0.20, "refund_mana_pct": 100}
    ],
    "icon": "mana_gold"
  },
  "shadow_affinity": {
    "talent_id": "shadow_affinity",
    "name": "Shadow Affinity",
    "description": "+20% stealth/backstab damage. +10% dodge",
    "category": "OFFENSIVE",
    "allowed_classes": ["rogue", "monk", "warlock"],
    "effects": [
      {"type": "CONDITIONAL_DAMAGE", "condition": "FROM_STEALTH", "damage_bonus_pct": 20},
      {"type": "STAT_MODIFIER", "stat": "DODGE", "modifier_type": "FLAT", "value": 10}
    ],
    "icon": "shadow_purple"
  },
  "holy_fervor": {
    "talent_id": "holy_fervor",
    "name": "Holy Fervor",
    "description": "Holy damage +25%. Healing generates +1 class resource",
    "category": "OFFENSIVE",
    "allowed_classes": ["cleric", "paladin"],
    "effects": [
      {"type": "ELEMENTAL_DAMAGE_BONUS", "element": "HOLY", "bonus_pct": 25},
      {"type": "ON_HEAL_TRIGGER", "resource_gain": 1}
    ],
    "icon": "holy_gold"
  },
  "beast_bond": {
    "talent_id": "beast_bond",
    "name": "Beast Bond",
    "description": "Summons deal +30% damage and have +20% HP",
    "category": "OFFENSIVE",
    "allowed_classes": ["ranger", "druid"],
    "effects": [
      {"type": "SUMMON_MODIFIER", "damage_bonus_pct": 30, "hp_bonus_pct": 20}
    ],
    "icon": "paw_gold"
  },
  "aura_master": {
    "talent_id": "aura_master",
    "name": "Aura Master",
    "description": "Aura/buff effects +25% potency. Buff durations +1 turn",
    "category": "DEFENSIVE",
    "allowed_classes": ["paladin", "bard"],
    "effects": [
      {"type": "BUFF_MODIFIER", "potency_bonus_pct": 25, "duration_bonus": 1}
    ],
    "icon": "aura_blue"
  },
  "berserkers_vitality": {
    "talent_id": "berserkers_vitality",
    "name": "Berserker's Vitality",
    "description": "While above 50 Fury, regen 3% max HP per turn",
    "category": "DEFENSIVE",
    "allowed_classes": ["barbarian"],
    "effects": [
      {"type": "CONDITIONAL_REGEN", "condition": "RESOURCE_ABOVE", "resource": "fury_bar", "threshold": 50, "regen_pct": 3}
    ],
    "icon": "heart_red"
  },
  "arcane_absorption": {
    "talent_id": "arcane_absorption",
    "name": "Arcane Absorption",
    "description": "When hit by a spell, restore 10% of damage taken as mana",
    "category": "DEFENSIVE",
    "allowed_classes": ["mage", "sorcerer", "artificer"],
    "effects": [
      {"type": "ON_MAGIC_HIT", "mana_restore_pct_of_damage": 10}
    ],
    "icon": "crystal_blue"
  },
  "song_of_rest": {
    "talent_id": "song_of_rest",
    "name": "Song of Rest",
    "description": "At end of combat, all allies heal 10% max HP",
    "category": "UTILITY",
    "allowed_classes": ["bard"],
    "effects": [
      {"type": "ON_COMBAT_END", "heal_party_pct": 10}
    ],
    "icon": "music_yellow"
  },
  "mechanical_efficiency": {
    "talent_id": "mechanical_efficiency",
    "name": "Mechanical Efficiency",
    "description": "All item/consumable costs -25%",
    "category": "UTILITY",
    "allowed_classes": ["artificer"],
    "effects": [
      {"type": "COST_REDUCTION", "target": "CONSUMABLES", "reduction_pct": 25}
    ],
    "icon": "gear_yellow"
  }
}
```

---

## Implementation Steps

### Step 1: Talent Data
- Create `data/progression/talents.json` with all 25 talent definitions.
- Create `src/core/progression/talent_definition.py` -- frozen dataclass + loader.
- Test: all 25 talents load; class filtering works correctly.

### Step 2: Talent Effect Types
- Create `src/core/progression/talent_effect.py` -- enum `TalentEffectType` with all effect types (STAT_MODIFIER, CRIT_MODIFIER, ON_KILL_TRIGGER, CONDITIONAL_DAMAGE, DEATH_PREVENTION, etc.).
- Create `src/core/progression/talent_effect_applier.py` -- applies a talent's effects to a character.
- Test: each effect type applies correctly.

### Step 3: Talent Offering System
- Create `src/core/progression/talent_offering.py` -- generates 3 choices per character per talent level.
- Ensure category diversity (1 from each category when possible).
- Test: `test_offering_has_category_diversity`, `test_no_duplicate_talents`, `test_class_filtering`.

### Step 4: Talent Tracker
- Create `src/core/progression/talent_tracker.py` -- tracks which talents each character has chosen.
- Method: `choose_talent(character, talent_id) -> bool`.
- Method: `get_chosen_talents(character) -> list[TalentDefinition]`.
- Test: `test_choose_talent`, `test_cannot_choose_same_twice`, `test_max_4_talents`.

### Step 5: Wire into Level Up Flow
- In `LevelUpSystem`, when level is 3/5/7/9 and talents exist, include `talent_offering` in the `LevelUpResult`.
- Extend `LevelUpResult` with `talent_offering: list[TalentDefinition] | None`.

### Step 6: Talent UI
- Create `src/ui/scenes/talent_choice_scene.py`.
- Show 3 cards with talent name, description, icon placeholder.
- Player picks one, confirmation, applied immediately.

### Step 7: Hook Talent Effects into Combat
- For `STAT_MODIFIER`: apply as permanent buff via EffectManager.
- For `ON_KILL_TRIGGER`, `ON_COMBAT_START`, `ON_CAST_TRIGGER`: create hooks in combat engine that check talent tracker.
- For `DEATH_PREVENTION`: hook into `Character.take_damage()`.
- For economy modifiers (`XP_MODIFIER`, `GOLD_MODIFIER`): check in XP/gold calculators.

---

## Files to Create/Modify

### Create
- `data/progression/talents.json`
- `src/core/progression/talent_definition.py`
- `src/core/progression/talent_effect.py`
- `src/core/progression/talent_effect_applier.py`
- `src/core/progression/talent_offering.py`
- `src/core/progression/talent_tracker.py`
- `src/ui/scenes/talent_choice_scene.py`
- `tests/core/test_progression/test_talent_definition.py`
- `tests/core/test_progression/test_talent_offering.py`
- `tests/core/test_progression/test_talent_tracker.py`
- `tests/core/test_progression/test_talent_effects.py`

### Modify
- `src/core/progression/level_up_result.py` -- add `talent_offering` field
- `src/core/progression/level_up_system.py` -- generate offerings at talent levels
- `src/core/combat/` -- add hooks for talent triggers
- `src/core/characters/character.py` -- add `talent_ids: list[str]` field
- `src/dungeon/run/run_orchestrator.py` -- add `TALENT_CHOICE` scene transition

---

## Test Strategy

| Test Category | What to Verify |
|--------------|----------------|
| Data Loading | All 25 talents parse; class restrictions correct |
| Offering | Exactly 3 choices; category diversity; no repeats; class filter applied |
| Application | Stat modifiers change combat stats; economy modifiers change gold/XP |
| Triggered | ON_KILL grants bonus action; DEATH_PREVENTION prevents death once |
| Stacking | Multiple stat talents stack correctly (additive, not multiplicative) |
| Edge Cases | Character with all 4 talents cannot pick a 5th; pool exhaustion handled |

---

## Balance Notes

**Power Budget:** A character with 4 talents should be approximately 40-50% more effective than a level-1 character (not counting level-up stat gains). Each talent contributes roughly 10-15% of total power budget.

**Tuning Levers:**
- Number values (15% damage, 20% defense) are all `[PLACEHOLDER]` -- test in playtest.
- If one talent dominates, reduce its value or add a downside.
- If talents feel irrelevant, increase all values by 5-10%.
- The offering of 3 options prevents "always pick X" if the pool is well-balanced.
