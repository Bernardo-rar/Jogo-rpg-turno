# Accessory System -- Design Document

**Version**: 1.0
**Date**: 2026-03-29
**Status**: Draft -- values marked [PLACEHOLDER] need playtesting

**Compatibility Note**: The JSON file (`data/accessories/accessories.json`) is loadable
with the current codebase (all 3042 tests pass). Accessories that are *designed* to use
CRIT_CHANCE and CRIT_DAMAGE stats have temporary substitute stats (PHYSICAL_ATTACK, SPEED)
until those enum values are added to `ModifiableStat`. Each affected entry has a `_design_note`
field documenting the intended final stats. See Section 3 for implementation steps.

---

## 1. Design Philosophy

### Player Experience Goal
Accessories are the primary vector for **build customization within a run**. Weapons define your damage type, armor defines your survivability profile, but accessories let the player **specialize, synergize, and adapt** to what the dungeon throws at them.

### Core Design Pillars

1. **Meaningful Choice**: No accessory should be universally best. Every equip decision involves a tradeoff -- more offense means less defense, more crit means less sustain. With 2 base slots (expandable via CHA), every slot matters.

2. **Class Synergy Without Class-Locking**: Accessories synergize with specific class archetypes (casters, bruisers, supports, assassins) without being restricted to them. A Barbarian *can* equip a mana regen amulet -- it just won't help much. The design rewards players who understand their build.

3. **Run Narrative**: The accessories you find shape the identity of each run. "This was the run where I stacked crit on my Rogue" vs. "This run I went full tank Paladin with two defense rings." Accessories are the loot that makes each run feel different.

4. **Rarity = Complexity, Not Just Numbers**: Common accessories have one stat. Legendary accessories have stat combinations that create emergent synergies. Higher rarity does not just mean bigger numbers -- it means more interesting decisions.

---

## 2. Accessory Type Identity

Each accessory type has a thematic and mechanical identity that guides what stats appear on it.

### RING -- Offensive Power
**Fantasy**: A ring of concentrated magical or physical energy.
**Stat Focus**: PHYSICAL_ATTACK, MAGICAL_ATTACK, CRIT_CHANCE, CRIT_DAMAGE
**Design Rule**: Rings are for characters who want to hit harder. They should never have defensive stats. A ring is always a greedy choice.

### AMULET -- Magical Resilience & Sustain
**Fantasy**: A pendant that channels protective or restorative energy.
**Stat Focus**: MAGICAL_DEFENSE, MAX_MANA, MANA_REGEN, HEALING_RECEIVED
**Design Rule**: Amulets protect against magical threats and fuel caster sustain. They bridge the gap between "I survive spells" and "I can cast more spells." Good for supports, casters, and anyone facing magic-heavy enemies.

### CLOAK -- Agility & Evasion
**Fantasy**: A garment that makes you harder to pin down.
**Stat Focus**: SPEED, ARMOR_CLASS, PHYSICAL_DEFENSE
**Design Rule**: Cloaks are about not getting hit -- either by going first (SPEED), dodging (ARMOR_CLASS), or absorbing physical blows. They reward positioning-aware players. Front-liners want the defense; back-liners want the speed.

### BRACELET -- Resilience & Vitality
**Fantasy**: A wristguard infused with protective or life-sustaining magic.
**Stat Focus**: MAX_HP, HP_REGEN, PHYSICAL_DEFENSE, HEALING_RECEIVED
**Design Rule**: Bracelets keep you alive. They are the "I need to survive longer" choice. Tanks and bruisers love them. Squishier characters equip them when they keep dying.

---

## 3. Implementation Notes -- System Gaps

### Stats Not Yet in ModifiableStat
The current `ModifiableStat` enum does NOT include:
- `CRIT_CHANCE`
- `CRIT_DAMAGE`

These need to be added to the enum and wired into the damage pipeline. Crit chance currently comes only from DEX thresholds (`crit_chance_pct`). Adding it to ModifiableStat lets accessories, buffs, and debuffs all modify crit through a single pipeline.

**Recommendation**: Add `CRIT_CHANCE` and `CRIT_DAMAGE` to `ModifiableStat`. Then:
- `CRIT_CHANCE`: flat value is additive percentage points (e.g., flat=5 means +5% crit chance on top of base 5%)
- `CRIT_DAMAGE`: flat value is additive to the 2x base crit multiplier (e.g., flat=50 means crit does 2.5x instead of 2.0x, where 50 = +50% of base damage)

### Accessory Bonuses Not Fully Wired
Currently `_total_accessory_flat()` is only called for:
- SPEED
- PHYSICAL_DEFENSE
- MAGICAL_DEFENSE

The following stats need wiring in `combat_stats_mixin.py`:
- MAX_HP (in `max_hp` property)
- MAX_MANA (in `max_mana` property)
- PHYSICAL_ATTACK (in `physical_attack` property)
- MAGICAL_ATTACK (in `magical_attack` property)
- HP_REGEN (in `hp_regen` property)
- MANA_REGEN (in `mana_regen` property)
- HEALING_RECEIVED (in `receive_healing` method)
- ARMOR_CLASS (in `armor_class` property)
- CRIT_CHANCE (new -- in damage resolution)
- CRIT_DAMAGE (new -- in damage resolution)

### Elemental Accessories
The current accessory data model (`StatBonus` with `ModifiableStat`) cannot express per-element bonuses like "resist 20% fire damage" or "deal +15% ice damage." Two options:

**Option A (Recommended)**: Add an optional `elemental_resistances` field to the `Accessory` dataclass:
```python
elemental_resistances: dict[ElementType, float] = field(default_factory=dict)
```
These multiply with the character's existing `ElementalProfile`. For example, `{"FIRE": 0.8}` means the character takes 80% of fire damage they would otherwise take (20% fire resist).

**Option B**: Encode elemental bonuses as new ModifiableStat entries (FIRE_RESISTANCE, ICE_RESISTANCE, etc.) -- this adds 10+ enum values and is harder to scale.

For now, the JSON includes a `description` field on elemental accessories noting the intended effect, and the `stat_bonuses` use MAGICAL_DEFENSE or PHYSICAL_DEFENSE as a general-purpose approximation. When elemental resistance is implemented, these can be upgraded.

---

## 4. Balance Framework

### Stat Value Budget by Rarity

Each rarity has a "budget" of stat points it can spend. This keeps accessories comparable within the same rarity tier.

| Rarity    | Stat Count | Flat Range | Percent Range | Budget* | CHA Req |
|-----------|-----------|------------|---------------|---------|---------|
| COMMON    | 1         | +2 to +5   | --            | 5       | 0       |
| UNCOMMON  | 1-2       | +5 to +10  | +5% to +10%   | 12      | 12      |
| RARE      | 2-3       | +8 to +15  | +10% to +20%  | 25      | 18      |
| LEGENDARY | 2-3       | +12 to +25 | +15% to +30%  | 40      | 22      |

*Budget is an approximate total when normalizing: 1 flat ~ 1 point, 1% ~ 0.5 points. Not a hard cap -- used as a guideline to prevent outliers.

### Stat Weight (Relative Power)

Not all stats are created equal. +5 SPEED is worth more than +5 MAX_HP because SPEED determines turn order which is a high-leverage mechanic in a 3-8 round combat.

| Stat              | Weight | Rationale                                        |
|-------------------|--------|--------------------------------------------------|
| SPEED             | 3.0    | Turn order is the highest-leverage stat           |
| CRIT_CHANCE       | 2.5    | Multiplicative with all damage                    |
| CRIT_DAMAGE       | 2.0    | Only procs on crit, but scales hard               |
| PHYSICAL_ATTACK   | 1.5    | Direct damage increase                            |
| MAGICAL_ATTACK    | 1.5    | Direct damage increase                            |
| PHYSICAL_DEFENSE  | 1.0    | Linear mitigation                                 |
| MAGICAL_DEFENSE   | 1.0    | Linear mitigation                                 |
| ARMOR_CLASS       | 1.5    | Reduces all physical damage taken                 |
| MAX_HP            | 0.8    | Effective only when you take damage                |
| MAX_MANA          | 0.8    | Only useful for casters                            |
| HP_REGEN          | 0.7    | Slow value over many turns                         |
| MANA_REGEN        | 0.7    | Slow value, caster-only                            |
| HEALING_RECEIVED  | 1.2    | Multiplies healer efficiency, needs a healer       |

These weights inform pricing and ensure a +3 SPEED ring is treated as more valuable than a +3 HP_REGEN ring.

---

## 5. Full Accessory Roster (30 accessories)

### Naming Convention
- COMMON: Simple material + type (Iron Ring, Leather Cloak)
- UNCOMMON: Descriptive adjective + type (Stalwart Bracelet, Swift Cloak)
- RARE: Evocative name with power word (Voidward Amulet, Serpent's Fang Ring)
- LEGENDARY: Named items with lore weight (Crown of the Undying, Veil of the Pale Moon)

### Distribution
- COMMON: 8 (2 per type)
- UNCOMMON: 10 (2-3 per type)
- RARE: 8 (2 per type)
- LEGENDARY: 4 (1 per type)
- **Total: 30**

See `data/accessories/accessories.json` for the full data file.

---

## 6. Class Synergy Map

This table shows which accessories naturally synergize with each class archetype. Players are NOT restricted -- this documents the intended "best fits."

### Melee DPS (Fighter, Barbarian, Monk)
- **Primary wants**: PHYSICAL_ATTACK, CRIT_CHANCE, CRIT_DAMAGE
- **Best types**: RING (offense), BRACELET (survive front line)
- **Dream combo**: Bloodstone Ring (crit) + Ironhide Bracelet (HP/defense)

### Caster DPS (Mage, Warlock, Artificer)
- **Primary wants**: MAGICAL_ATTACK, MAX_MANA, MANA_REGEN
- **Best types**: RING (magic damage), AMULET (mana sustain)
- **Dream combo**: Arcane Signet Ring (magic atk) + Starweave Amulet (mana + mana regen)

### Healer/Support (Cleric, Bard, Druid)
- **Primary wants**: HEALING_RECEIVED, MANA_REGEN, MAGICAL_DEFENSE
- **Best types**: AMULET (mana + heal), BRACELET (survive)
- **Dream combo**: Lifeward Amulet (heal + mag def) + Oakheart Bracelet (HP regen + HP)

### Tank (Paladin, Fighter with defensive build)
- **Primary wants**: PHYSICAL_DEFENSE, ARMOR_CLASS, MAX_HP
- **Best types**: CLOAK (AC + phys def), BRACELET (HP + HP regen)
- **Dream combo**: Sentinel's Cloak (AC + phys def) + Guardian Bracelet (HP + phys def)

### Assassin (Rogue, Ranger)
- **Primary wants**: SPEED, CRIT_CHANCE, CRIT_DAMAGE, PHYSICAL_ATTACK
- **Best types**: RING (crit), CLOAK (speed)
- **Dream combo**: Shadowfang Ring (crit chance + crit dmg) + Windrunner Cloak (speed + speed)

### Necromancer
- **Primary wants**: MAGICAL_ATTACK, MAX_HP, HP_REGEN (self-sustain theme)
- **Best types**: RING (magic atk), BRACELET (HP sustain)
- **Dream combo**: Voidstone Ring (magic atk) + Bloodbound Bracelet (HP + HP regen)

---

## 7. Drop Tier Distribution

### Regular Combat (Tier 1)
| Rarity    | Drop Weight |
|-----------|-------------|
| COMMON    | 70%         |
| UNCOMMON  | 25%         |
| RARE      | 5%          |
| LEGENDARY | 0%          |

### Elite Combat
| Rarity    | Drop Weight |
|-----------|-------------|
| COMMON    | 20%         |
| UNCOMMON  | 55%         |
| RARE      | 20%         |
| LEGENDARY | 5%          |

### Boss
| Rarity    | Drop Weight |
|-----------|-------------|
| COMMON    | 0%          |
| UNCOMMON  | 25%         |
| RARE      | 55%         |
| LEGENDARY | 20%         |

### Treasure Room
| Rarity    | Drop Weight |
|-----------|-------------|
| COMMON    | 10%         |
| UNCOMMON  | 45%         |
| RARE      | 35%         |
| LEGENDARY | 10%         |

### Shop Availability
- Tier 1 shops: COMMON + UNCOMMON
- Tier 2 shops: UNCOMMON + RARE
- Tier 3 shops: RARE + LEGENDARY

---

## 8. Shop Pricing

Anchored to the existing economy (Health Potion = 15g, Smoke Bomb = 35g, boss gold = 100-300g).

| Rarity    | Base Price | Price Range  | Sell Value (50%) |
|-----------|-----------|--------------|-----------------|
| COMMON    | 20g       | 15-25g       | 10g              |
| UNCOMMON  | 50g       | 40-65g       | 25g              |
| RARE      | 120g      | 100-150g     | 60g              |
| LEGENDARY | 250g      | 200-300g     | 125g             |

**Rationale**:
- A COMMON accessory costs slightly more than a Health Potion (15g) because it provides permanent value for the run
- An UNCOMMON accessory costs ~1 boss kill of gold (Tier 1 boss = 100g), making it a significant early investment
- A RARE accessory costs more than a boss but less than two bosses -- the player must have been saving
- A LEGENDARY requires most of a Tier 3 boss's gold (300g) and represents a major purchase decision
- Sell value at 50% matches the existing `sell_multiplier` in shop_inventory.json

---

## 9. Elemental Accessories (Future)

When elemental resistance is implemented on accessories, the following themed accessories should be added. They are NOT in the current JSON because the data model does not support per-element bonuses yet.

### Planned Elemental Accessories (8 items)
1. **Ember Ward Amulet** (UNCOMMON) -- 20% fire resistance
2. **Frostguard Cloak** (UNCOMMON) -- 20% ice resistance
3. **Stormbreaker Ring** (UNCOMMON) -- +10% lightning damage dealt
4. **Earthen Bracelet** (UNCOMMON) -- 20% earth resistance
5. **Tidewalker Amulet** (RARE) -- 30% water resistance, +5 MANA_REGEN
6. **Radiant Seal Ring** (RARE) -- +15% holy damage dealt, +5 HEALING_RECEIVED
7. **Voidcloak** (RARE) -- 30% darkness resistance, +8 MAGICAL_DEFENSE
8. **Serpent Fang Bracelet** (RARE) -- +15% poison damage dealt, +8 PHYSICAL_ATTACK

These require either:
- New `elemental_resistances` / `elemental_damage_bonus` fields on `Accessory`
- Or new per-element entries in `ModifiableStat`

I recommend Option A (fields on Accessory) -- see Section 3.

---

## 10. Tuning Levers

These are the variables that control the feel and balance of the accessory system. All values are [PLACEHOLDER] until playtested.

| Lever                          | Current Value | Notes                                    |
|--------------------------------|---------------|------------------------------------------|
| Base accessory slots           | 2             | From accessory_slots.py                  |
| CHA threshold bonus per tier   | +1 slot       | At CHA 18, 22, 26, 30, 32               |
| Max theoretical slots          | 7             | 2 base + 5 CHA thresholds               |
| Common stat range              | +2 to +5      | [PLACEHOLDER]                            |
| Uncommon stat range            | +5 to +10     | [PLACEHOLDER]                            |
| Rare stat range                | +8 to +15     | [PLACEHOLDER]                            |
| Legendary stat range           | +12 to +25    | [PLACEHOLDER]                            |
| Shop price common              | 20g           | [PLACEHOLDER]                            |
| Shop price uncommon            | 50g           | [PLACEHOLDER]                            |
| Shop price rare                | 120g          | [PLACEHOLDER]                            |
| Shop price legendary           | 250g          | [PLACEHOLDER]                            |
| Accessory drop chance (combat) | ~10%          | Weight in drop_tables.json               |
| Percent bonus effectiveness    | 1% = 0.5 budget| Keeps % bonuses from outscaling flat     |

---

## 11. Success Criteria

The accessory system is working correctly when:

1. **No dominant strategy**: No single accessory is equipped on every character in every run
2. **Type identity holds**: Players learn to associate RINGs with offense, AMULETs with magic/sustain, CLOAKs with agility, BRACELETs with tankiness
3. **Rarity excitement scales**: Finding a LEGENDARY feels meaningfully different from finding a COMMON
4. **2-slot tension**: With only 2 base slots, players agonize over which two accessories to equip -- this is the sign of good design
5. **Class diversity**: Different classes gravitate toward different accessories, not all toward the same "best" one
6. **Economy integration**: Accessories are priced such that buying one in a shop feels like a meaningful investment, not a trivial purchase or an impossible luxury

---

## Changelog
- v1.0 (2026-03-29): Initial design. 30 accessories across 4 types and 4 rarities. Elemental accessories deferred pending data model extension.
