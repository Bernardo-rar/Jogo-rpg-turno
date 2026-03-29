# Death Recovery & Revive Mechanics -- Design Document

## Design Pillars

1. **Death is meaningful**: Losing a party member mid-run should hurt, but never end the run outright unless the entire party falls.
2. **Recovery is costly**: Every revive has a clear resource cost (gold, mana, item slot, action economy). There is no free resurrection.
3. **Revive does not erase the mistake**: The "Weakened" debuff after revive ensures a revived character is operating below full power temporarily, punishing careless play without making the character useless.
4. **Multiple channels, different contexts**: Gold revive at rest rooms (safe, planned), Phoenix Down in combat (emergency, expensive), Cleric skill (class identity, high cost). Each serves a different player moment.

---

## Player Experience Goal

The player who loses a party member should feel: "I can recover, but it will cost me -- and I need to play smarter for the next few encounters." NOT: "Game over, restart." NOT: "Whatever, I'll just revive for free."

---

## System 1A: Gold Revive at Rest Rooms

### Purpose
Safe, deliberate recovery option available between combats. The player pays gold (a universal run resource) to bring back a fallen member.

### Mechanic Specification

**Input**: Player selects a dead party member in the rest room UI and confirms the gold cost.

**Output**: Dead member is revived at 30% max HP. Gold is deducted. "Weakened" debuff applied.

**When Available**: Only during rest room scenes (RoomType.REST). Not available in campfire, shop, or event rooms.

**Costs & Numbers**:

| Variable            | Value  | Min | Max | Rationale                                                |
|---------------------|--------|-----|-----|----------------------------------------------------------|
| `REVIVE_GOLD_COST`  | 50g    | 30  | 80  | ~26% of Floor 1 total income (~190g). Meaningful but not devastating. |
| `REVIVE_HP_PERCENT` | 0.30   | 0.20| 0.50| Already exists in `rest_actions.py` as `REST_REVIVE_HP_PERCENT`. Matches heal amount symmetry. |

**Tuning Rationale**: 50g is roughly the reward from one elite encounter. The player must weigh "do I spend this gold on a shop item, or on reviving my healer?" This creates a meaningful economy decision without locking the player out of recovery.

**Success Condition**: Player can revive any dead member at a rest room by paying 50g. Character returns with 30% HP and Weakened debuff.

**Failure States**:
- Player has insufficient gold: Option shown greyed out with cost displayed. Cannot select.
- No dead members: Revive option hidden entirely.
- Multiple dead members: Player can revive one per rest room (design choice: one action per rest room).

**Edge Cases**:
- Player has exactly 50g and 2 dead members: Can only revive one. Must choose which.
- Revived character already has Weakened from a prior revive: Weakened refreshes (does not stack).
- All 4 members dead: Game Over triggers before reaching rest room.

### UI Integration

Add a third option to the rest room scene:

```
[1] Curar (30% HP)
[2] Meditar (40% Mana)
[3] Reviver (50g) -- Traz 1 membro de volta com 30% HP    [ONLY IF dead members exist AND gold >= 50]
```

If selected, show a sub-menu listing dead party members. Player picks one by number key. Confirmation: "Reviver [Name] por 50g? [Enter] Confirmar / [Esc] Voltar"

---

## System 1B: Phoenix Down (Consumable Item)

### Purpose
Emergency in-combat revive. Extremely valuable. Forces the player to decide: "Do I use my bonus action on offense, or do I spend it to bring back a fallen ally right now?"

### Mechanic Specification

**Input**: Player selects Phoenix Down from item menu during combat, targets a dead party member.

**Output**: Target revived at 25% max HP. Item consumed. Costs the user's bonus action.

**When Available**: During combat, if the user has a Phoenix Down in inventory and a dead ally exists.

**Costs & Numbers**:

| Variable                    | Value   | Min  | Max  | Rationale                                          |
|-----------------------------|---------|------|------|----------------------------------------------------|
| `PHOENIX_HP_PERCENT`        | 0.25    | 0.15 | 0.40 | Lower than rest room revive (risky, mid-combat).   |
| `PHOENIX_ACTION_COST`       | BONUS   | --   | --   | Costs bonus action, not main action. Still a real cost. |
| `PHOENIX_SHOP_PRICE`        | 100g    | 80   | 150  | Very expensive. ~52% of Floor 1 income. Luxury item. |
| `PHOENIX_DROP_WEIGHT`       | 3       | 1    | 5    | Rare drop from elites/bosses. Not farmable.        |

**Tuning Rationale**: 100g shop price means the player sacrifices multiple consumable slots' worth of gold. At 25% HP the revived character is fragile and needs immediate healing -- this creates follow-up decision pressure. Costing bonus action means the reviver cannot move, use a quick skill, or change stance in the same turn.

**Success Condition**: During combat, a living party member uses bonus action + Phoenix Down on a dead ally. Ally returns at 25% HP with Weakened debuff.

**Failure States**:
- No dead allies: Item not selectable as target.
- No bonus action remaining: Item greyed out.
- Inventory empty of Phoenix Down: Option does not appear.

**Edge Cases**:
- Revived character dies again the same round before their turn: They are dead again. No special protection.
- Last living member uses Phoenix Down: Valid. Now two members alive.
- Using Phoenix Down on a character who died from a DoT tick this round: Valid. DoT already resolved.

### Economy Impact

Phoenix Down at 100g is priced to be a deliberate purchase decision. Expected availability per run:
- Shop: 0-1 available (not guaranteed in every shop inventory)
- Drops: 0-1 from elite/boss loot tables (weight 3 out of ~total 50-80)
- Total per run: 0-2 Phoenix Downs on average

This scarcity is intentional. Phoenix Down is a "break glass in case of emergency" item, not a routine consumable.

---

## System 1C: Cleric Resurrection Skill

### Purpose
Class identity mechanic. The Cleric is the dedicated healer; being the only class that can resurrect in combat reinforces that role. High mana cost and cooldown prevent it from trivializing death.

### Mechanic Specification

**Input**: Cleric selects Resurrection from skill bar, targets a dead party member.

**Output**: Target revived at 50% max HP. Mana deducted. Skill goes on cooldown. Weakened debuff applied to target.

**When Available**: In combat, when the Cleric has sufficient mana and the skill is off cooldown.

**Costs & Numbers**:

| Variable                   | Value     | Min   | Max   | Rationale                                      |
|----------------------------|-----------|-------|-------|-------------------------------------------------|
| `RESURRECT_HP_PERCENT`     | 0.50      | 0.30  | 0.60  | Best revive method -- class reward.             |
| `RESURRECT_MANA_COST`      | 80        | 50    | 120   | ~40-50% of Cleric's mana pool at mid-game. Huge commitment. |
| `RESURRECT_COOLDOWN`       | 5 turns   | 3     | 8     | Cannot spam. One res per fight in most cases.   |
| `RESURRECT_ACTION_COST`    | ACTION    | --    | --    | Costs main action. Cleric cannot heal AND revive same turn. |

**Tuning Rationale**: 50% HP revive is the best available, rewarding parties that include a Cleric. But 80 mana means the Cleric cannot heal for several turns after, and 5 turn cooldown means one resurrection per fight maximum in practice. The main action cost forces a choice: "Do I heal the living, or bring back the dead?"

**Success Condition**: Cleric uses main action + mana to revive a dead ally at 50% HP. Skill enters 5-turn cooldown.

**Failure States**:
- Insufficient mana: Skill greyed out with "Not enough mana" tooltip.
- Skill on cooldown: Show remaining turns "Resurrect (3 turns)".
- No dead allies: Skill not targetable.

**Edge Cases**:
- Cleric under Amnesia ailment (blocks mana skills): Cannot use Resurrection.
- Cleric revives then dies same round: Revived ally stays alive.
- Multiple Clerics in party (future): Each has independent cooldown. Intentional -- comp diversity payoff.

---

## System 1D: Weakened Debuff (Post-Revive Penalty)

### Purpose
Makes revive feel consequential. The revived character is not immediately at full power. Creates a window of vulnerability that rewards the player for protecting the weakened ally.

### Mechanic Specification

**Effect**: -10% to all derived stats (physical attack, magical attack, physical defense, magical defense, speed). Lasts 2 combats (not turns -- persists across encounters).

**Data Structure**:

```
stacking_key: "weakened_revive"
category: DEBUFF
duration_type: COMBAT_COUNT (not turn count)
duration: 2 combats
modifiers:
  - PHYSICAL_ATTACK: percent = -0.10
  - MAGICAL_ATTACK: percent = -0.10
  - PHYSICAL_DEFENSE: percent = -0.10
  - MAGICAL_DEFENSE: percent = -0.10
  - SPEED: percent = -0.10
stacking: REFRESH (re-revive resets counter, does not stack to -20%)
```

**Numbers**:

| Variable                | Value  | Min  | Max  | Rationale                                         |
|-------------------------|--------|------|------|----------------------------------------------------|
| `WEAKENED_STAT_PENALTY`  | -0.10  | -0.05| -0.20| 10% is noticeable without making the character useless. |
| `WEAKENED_COMBAT_COUNT` | 2      | 1    | 3    | 2 combats means ~2-4 rooms of penalty. Feels fair. |

**Tuning Rationale**: -10% all stats is approximately equivalent to being 1 level lower. This is enough to make the player adjust their tactics (protect the weakened member, avoid putting them in front line) without making them a liability.

**Implementation Note**: This is a new type of Effect that counts combats, not turns. The EffectManager currently counts turns; we need a `CombatCountEffect` subclass or a `RunState`-level tracker.

**Edge Cases**:
- Weakened + another debuff (e.g., Cold): Both apply. Weakened stacks multiplicatively with other debuffs.
- Character revived twice in quick succession: Weakened refreshes to 2 combats, does not stack to -20%.
- Weakened character enters boss fight: They have the debuff. This is the intended penalty.

---

## System 1E: Permadeath Modifier (Optional)

### Purpose
Challenge modifier for experienced players. Disables all revive mechanics for a harder run with increased rewards. Appeals to roguelite masochists.

### Mechanic Specification

**Implementation**: New `RunModifier` entry in `data/dungeon/modifiers/modifiers.json`.

```json
{
  "permadeath": {
    "name": "Permadeath",
    "description": "No revives allowed. Dead is dead. +30% gold, +25% score.",
    "category": "RESTRICTION",
    "effect": {
      "gold_mult": 1.30,
      "score_mult": 1.25
    }
  }
}
```

**Behavior**: When active:
- Rest room revive option: Hidden
- Phoenix Down: Cannot be used (greyed out with "Permadeath active" tooltip)
- Cleric Resurrection: Skill disabled
- `RunState.has_permadeath` flag checked by all revive code paths

**Tuning Rationale**: +30% gold and +25% score compensate for the massive difficulty increase. This is the highest risk/reward modifier in the game.

---

## Integration Points

### Existing Code Modified

| File | Change |
|------|--------|
| `src/dungeon/run/rest_actions.py` | Add `apply_rest_revive_for_gold()` function (currently `apply_rest_revive()` exists but costs no gold) |
| `src/dungeon/run/run_state.py` | Add `has_permadeath` property, add `weakened_tracker: dict[str, int]` for combat-counted debuffs |
| `src/ui/scenes/rest_room_scene.py` | Add revive option [3] with gold cost display, sub-menu for target selection |
| `data/dungeon/modifiers/modifiers.json` | Add `permadeath` entry |

### New Code Created

| File | Purpose |
|------|---------|
| `src/dungeon/run/revive_actions.py` | Core revive logic: `revive_at_rest_room()`, `revive_in_combat()`, `can_revive()` |
| `src/core/effects/weakened_effect.py` | `WeakenedEffect` subclass -- multi-stat percent debuff with combat-count duration |
| `data/dungeon/revive/revive_config.json` | All revive costs, HP percentages, cooldowns |

### System Dependencies

```
revive_actions.py
  -> RunState (gold, party, has_permadeath)
  -> Character.revive() (already exists)
  -> WeakenedEffect -> EffectManager.add_effect()
  -> revive_config.json (data-driven costs)

rest_room_scene.py
  -> revive_actions.can_revive_at_rest()
  -> revive_actions.revive_at_rest_room()

playable_combat_scene.py (Phoenix Down path)
  -> item_use_actions.py -> revive_actions.revive_in_combat()

cleric.py (future Resurrection skill)
  -> revive_actions.revive_in_combat()
```

---

## Test Cases

### Unit Tests (`tests/dungeon/run/test_revive_actions.py`)

```
test_revive_at_rest_deducts_gold_and_revives_at_30_percent_hp
test_revive_at_rest_fails_if_gold_insufficient
test_revive_at_rest_fails_if_no_dead_members
test_revive_at_rest_applies_weakened_debuff
test_revive_at_rest_blocked_by_permadeath_modifier
test_revive_in_combat_with_phoenix_down_revives_at_25_percent_hp
test_revive_in_combat_consumes_phoenix_down_item
test_revive_in_combat_applies_weakened_debuff
test_revive_in_combat_blocked_by_permadeath
test_weakened_debuff_reduces_all_stats_by_10_percent
test_weakened_debuff_refreshes_on_second_revive_not_stacks
test_weakened_debuff_lasts_2_combats
test_weakened_debuff_removed_after_2_combats
test_cleric_resurrect_revives_at_50_percent_hp
test_cleric_resurrect_costs_80_mana
test_cleric_resurrect_enters_5_turn_cooldown
test_cleric_resurrect_blocked_by_amnesia
test_cleric_resurrect_blocked_by_permadeath
```

### Integration Tests

```
test_rest_room_shows_revive_option_when_dead_member_exists
test_rest_room_hides_revive_when_no_dead_members
test_rest_room_hides_revive_when_permadeath_active
test_combat_phoenix_down_uses_bonus_action
test_full_flow_revive_then_weakened_then_2_combats_then_cleared
```

---

## Implementation Priority (within this system)

| Priority | Component | Effort | Dependencies |
|----------|-----------|--------|--------------|
| P0 | `revive_config.json` | Small | None |
| P0 | `WeakenedEffect` class | Medium | Effect ABC, ModifiableStat |
| P0 | `revive_actions.py` (gold revive at rest) | Medium | RunState, Character.revive(), WeakenedEffect |
| P1 | Rest room UI integration | Medium | revive_actions, rest_room_scene |
| P1 | Permadeath modifier | Small | modifiers.json, RunState |
| P2 | Phoenix Down item integration | Medium | item system, inventory, combat scene |
| P3 | Cleric Resurrection skill | Large | skill system, cooldown tracker, Cleric class |

Build P0 first. Test in isolation. Then integrate into UI (P1). Phoenix Down and Cleric skill depend on systems not fully built yet (item use in combat, skill system), so they are lower priority.
