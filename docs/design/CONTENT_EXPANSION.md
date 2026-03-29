# Content Expansion -- Enemies, Bosses, Consumables, Legendaries, Events

> Version 1.0 -- 2026-03-29
> Author: GameDesigner Agent
> Status: DESIGN DOCUMENT (all numerical values are [PLACEHOLDER] until playtested)

---

## Table of Contents

1. [Design Pillars](#1-design-pillars)
2. [Enemy Expansion (20 new enemies)](#2-enemy-expansion)
3. [Boss Expansion (9 new bosses)](#3-boss-expansion)
4. [Advanced Consumables (15 new items)](#4-advanced-consumables)
5. [Legendary Weapons and Armor (8 items)](#5-legendary-weapons-and-armor)
6. [Complex Events (10 new events)](#6-complex-events)
7. [Balance Framework](#7-balance-framework)
8. [Drop and Spawn Distribution](#8-drop-and-spawn-distribution)
9. [Implementation Priority](#9-implementation-priority)

---

## 1. Design Pillars

Every piece of content in this expansion must satisfy at least one of these pillars:

1. **Tactical Diversity** -- Each enemy composition forces a different player strategy. No "always focus the backline" autopilot.
2. **Readable Threat** -- Within 1 turn the player must understand what an enemy does and why it is dangerous.
3. **Risk/Reward Tension** -- Every boss phase, every event choice, every consumable use is a meaningful decision with a tradeoff.
4. **Elemental Relevance** -- The 10-element system must feel like a real strategic layer, not a damage number multiplier.
5. **Economy Pressure** -- New items must create interesting spending decisions without inflating the gold curve.

---

## 2. Enemy Expansion

### 2.1 Balance Rationale

Enemy stats are derived from the existing tier 1 baselines. The formulas for HP use:
`HP = ((hit_dice + CON + mod_hp_flat) * 2) * mod_hp_mult`

For reference, existing tier 1 enemies produce:
- Goblin: ((6 + 6 + 0) * 2) * 3 = 72 HP
- Skeleton: ((8 + 8 + 0) * 2) * 4 = 128 HP
- Slime: ((10 + 14 + 2) * 2) * 5 = 260 HP (tanky)

**Tier scaling targets:**
- Tier 1 (floors 1-3): HP ~60-260, ATK mod 2-5, DEF mod 1-4
- Tier 2 (floors 4-6): HP ~150-450, ATK mod 5-8, DEF mod 3-7
- Tier 3 (floors 7-9): HP ~300-700, ATK mod 7-12, DEF mod 5-10

**Design constraint**: Player party HP ~200-500, Player ATK ~50-150. Combat should last 3-8 rounds. An encounter of 3 tier-1 enemies should be clearable in 4-5 rounds. A tier 3 encounter should feel dangerous even to a well-equipped party.

---

### 2.2 Tier 1 -- 5 New Enemies (Floors 1-3)

---

#### 2.2.1 Kobold Trapper

**Design Purpose**: Introduce positional disruption. Forces the player to think about front/back positioning from floor 1.

| Field | Value |
|-------|-------|
| enemy_id | `kobold_trapper` |
| Name | Kobold Trapper |
| Tier | 1 |
| Archetype | CONTROLLER |
| Position | BACK |
| Attack Type | PHYSICAL |
| Element Affinity | EARTH |
| Weakness | FIRE 1.5x, HOLY 1.5x |
| Resistance | EARTH 0.5x |
| Description | Cunning lizard-like creature that sets traps and throws nets from the backline. Disrupts positioning and slows the party's frontline. |

**Class Modifiers:**
```
hit_dice: 5, mod_hp_flat: 0, mod_hp_mult: 3, mana_multiplier: 2
mod_atk_physical: 3, mod_atk_magical: 2
mod_def_physical: 2, mod_def_magical: 2
regen_hp_mod: 1, regen_mana_mod: 1
preferred_attack_type: PHYSICAL
```

**Base Attributes:** STR 6, DEX 12, CON 6, INT 8, WIS 6, CHA 3, MIND 4

**Estimated HP:** ((5 + 6 + 0) * 2) * 3 = 66 [PLACEHOLDER]

**Skills:**
- `trap_net` -- ACTION, SINGLE_ENEMY: Apply SLOW ailment 2 turns + reduce PHYSICAL_DEFENSE by 5 for 2 turns

**Special Traits:** `trap_setter` -- 30% chance to apply SLOW to frontline attacker when hit

---

#### 2.2.2 Cave Bat

**Design Purpose**: Fast glass cannon that punishes parties without AoE. High speed means it acts first.

| Field | Value |
|-------|-------|
| enemy_id | `cave_bat` |
| Name | Cave Bat |
| Tier | 1 |
| Archetype | DPS |
| Position | BACK |
| Attack Type | PHYSICAL |
| Element Affinity | DARKNESS |
| Weakness | FIRE 1.5x, LIGHTNING 1.5x |
| Resistance | DARKNESS 0.5x |
| Description | Swoops from the shadows with lightning-fast strikes. Fragile but extremely fast -- often acts before the player's party. |

**Class Modifiers:**
```
hit_dice: 4, mod_hp_flat: 0, mod_hp_mult: 2, mana_multiplier: 0
mod_atk_physical: 4, mod_atk_magical: 1
mod_def_physical: 1, mod_def_magical: 1
regen_hp_mod: 0, regen_mana_mod: 0
preferred_attack_type: PHYSICAL
```

**Base Attributes:** STR 6, DEX 18, CON 4, INT 2, WIS 6, CHA 2, MIND 1

**Estimated HP:** ((4 + 4 + 0) * 2) * 2 = 32 [PLACEHOLDER]

**Skills:**
- `sonic_screech` -- ACTION, ALL_ENEMIES: Damage base_power 4 + apply CONFUSION 1 turn (25% chance)

**Special Traits:** `evasive` -- High DEX gives natural dodge chance

---

#### 2.2.3 Vine Creeper

**Design Purpose**: Healer archetype for tier 1. Teaches the player that they need to prioritize kill order early.

| Field | Value |
|-------|-------|
| enemy_id | `vine_creeper` |
| Name | Vine Creeper |
| Tier | 1 |
| Archetype | HEALER |
| Position | BACK |
| Attack Type | MAGICAL |
| Element Affinity | EARTH |
| Weakness | FIRE 2.0x, ICE 1.5x |
| Resistance | EARTH 0.5x, WATER 0.5x |
| Description | A parasitic plant that heals allies by draining nutrients from the ground. Kill it first or the fight never ends. |

**Class Modifiers:**
```
hit_dice: 6, mod_hp_flat: 1, mod_hp_mult: 3, mana_multiplier: 3
mod_atk_physical: 1, mod_atk_magical: 3
mod_def_physical: 2, mod_def_magical: 3
regen_hp_mod: 2, regen_mana_mod: 2
preferred_attack_type: MAGICAL
```

**Base Attributes:** STR 4, DEX 4, CON 8, INT 6, WIS 10, CHA 2, MIND 5

**Estimated HP:** ((6 + 8 + 1) * 2) * 3 = 90 [PLACEHOLDER]

**Skills:**
- `vine_heal` -- ACTION, SINGLE_ALLY: Heal base_power 12
- `root_bind` -- BONUS_ACTION, SINGLE_ENEMY: Apply SLOW 2 turns

**Special Traits:** `regenerative` -- Heals self 5% max HP per turn

---

#### 2.2.4 Fire Imp

**Design Purpose**: First elemental-focused DPS. Teaches the player about elemental weaknesses and resistances. Burns deal sustained damage.

| Field | Value |
|-------|-------|
| enemy_id | `fire_imp` |
| Name | Fire Imp |
| Tier | 1 |
| Archetype | DPS |
| Position | BACK |
| Attack Type | MAGICAL |
| Element Affinity | FIRE |
| Weakness | WATER 1.5x, ICE 1.5x |
| Resistance | FIRE 0.0x (immune) |
| Description | A mischievous fiend that hurls fireballs and leaves the battlefield burning. Immune to its own element. |

**Class Modifiers:**
```
hit_dice: 5, mod_hp_flat: 0, mod_hp_mult: 2, mana_multiplier: 4
mod_atk_physical: 1, mod_atk_magical: 5
mod_def_physical: 1, mod_def_magical: 3
regen_hp_mod: 0, regen_mana_mod: 2
preferred_attack_type: MAGICAL
```

**Base Attributes:** STR 4, DEX 10, CON 5, INT 12, WIS 6, CHA 4, MIND 6

**Estimated HP:** ((5 + 5 + 0) * 2) * 2 = 40 [PLACEHOLDER]

**Skills:**
- `fireball` -- ACTION, SINGLE_ENEMY: Damage base_power 10, element FIRE, apply BURN (5 dmg/tick, 3 turns)

**Special Traits:** `fire_aura` -- Melee attackers take 3 FIRE damage per hit

---

#### 2.2.5 Armored Beetle

**Design Purpose**: A pure physical wall. Forces the player to use magic or elemental attacks. Teaches that some enemies resist physical and must be handled differently.

| Field | Value |
|-------|-------|
| enemy_id | `armored_beetle` |
| Name | Armored Beetle |
| Tier | 1 |
| Archetype | TANK |
| Position | FRONT |
| Attack Type | PHYSICAL |
| Element Affinity | EARTH |
| Weakness | LIGHTNING 1.5x, FIRE 1.5x |
| Resistance | EARTH 0.5x |
| Description | A massive insect with a nearly impenetrable carapace. Physical attacks bounce off. Slow but hits hard when it connects. |

**Class Modifiers:**
```
hit_dice: 10, mod_hp_flat: 2, mod_hp_mult: 5, mana_multiplier: 0
mod_atk_physical: 3, mod_atk_magical: 0
mod_def_physical: 5, mod_def_magical: 1
regen_hp_mod: 1, regen_mana_mod: 0
preferred_attack_type: PHYSICAL
```

**Base Attributes:** STR 12, DEX 3, CON 14, INT 2, WIS 4, CHA 2, MIND 1

**Estimated HP:** ((10 + 14 + 2) * 2) * 5 = 260 [PLACEHOLDER]

**Skills:** (none -- pure auto-attacker)

**Special Traits:** `armored_shell` -- Takes 25% less physical damage

---

### 2.3 Tier 2 -- 8 New Enemies (Floors 4-6)

---

#### 2.3.1 Orc Warrior

**Design Purpose**: Classic frontline bruiser. Introduces the taunt/intercept dynamic -- the player cannot freely target the backline.

| Field | Value |
|-------|-------|
| enemy_id | `orc_warrior` |
| Name | Orc Warrior |
| Tier | 2 |
| Archetype | TANK |
| Position | FRONT |
| Attack Type | PHYSICAL |
| Element Affinity | None (neutral) |
| Weakness | PSYCHIC 1.5x |
| Resistance | None |
| Description | Heavily armored orc that forces attention with war cries and intercepts attacks meant for allies. When alone, goes berserk. |

**Class Modifiers:**
```
hit_dice: 12, mod_hp_flat: 3, mod_hp_mult: 5, mana_multiplier: 0
mod_atk_physical: 6, mod_atk_magical: 1
mod_def_physical: 6, mod_def_magical: 3
regen_hp_mod: 2, regen_mana_mod: 0
preferred_attack_type: PHYSICAL
```

**Base Attributes:** STR 14, DEX 6, CON 14, INT 4, WIS 6, CHA 6, MIND 3

**Estimated HP:** ((12 + 14 + 3) * 2) * 5 = 290 [PLACEHOLDER]

**Skills:**
- `orc_taunt` -- BONUS_ACTION, SELF: Forces enemies to target self for 2 turns
- `battle_rage` -- BONUS_ACTION, SELF: +10 PHYSICAL_ATTACK for 3 turns (cooldown 4)

**Special Traits:** `last_stand` -- When last ally dies, gains +50% ATK and +30% SPEED for the rest of combat

---

#### 2.3.2 Wraith

**Design Purpose**: Anti-mage enemy. Forces the party's casters to conserve mana or risk running dry.

| Field | Value |
|-------|-------|
| enemy_id | `wraith` |
| Name | Wraith |
| Tier | 2 |
| Archetype | CONTROLLER |
| Position | BACK |
| Attack Type | MAGICAL |
| Element Affinity | DARKNESS |
| Weakness | HOLY 2.0x, FIRE 1.5x |
| Resistance | DARKNESS 0.0x (immune), PSYCHIC 0.5x |
| Description | An incorporeal specter that drains mana and silences spellcasters. Physical attacks pass through it without elemental enchantment. |

**Class Modifiers:**
```
hit_dice: 8, mod_hp_flat: 2, mod_hp_mult: 4, mana_multiplier: 4
mod_atk_physical: 1, mod_atk_magical: 7
mod_def_physical: 2, mod_def_magical: 6
regen_hp_mod: 1, regen_mana_mod: 2
preferred_attack_type: MAGICAL
```

**Base Attributes:** STR 3, DEX 10, CON 8, INT 14, WIS 12, CHA 6, MIND 10

**Estimated HP:** ((8 + 8 + 2) * 2) * 4 = 144 [PLACEHOLDER]

**Skills:**
- `mana_drain` -- ACTION, SINGLE_ENEMY: Damage base_power 8, steals 15 mana from target
- `silence_touch` -- BONUS_ACTION, SINGLE_ENEMY: Apply SILENCE 2 turns (cooldown 3)

**Special Traits:** `incorporeal` -- 50% physical damage reduction (unless attacker has elemental weapon)

---

#### 2.3.3 Harpy

**Design Purpose**: Evasive backline DPS that cannot be hit by ground-based effects. Introduces the concept of flying immunity.

| Field | Value |
|-------|-------|
| enemy_id | `harpy` |
| Name | Harpy |
| Tier | 2 |
| Archetype | DPS |
| Position | BACK |
| Attack Type | PHYSICAL (mixed) |
| Element Affinity | FORCE |
| Weakness | ICE 1.5x, LIGHTNING 1.5x |
| Resistance | EARTH 0.0x (immune, flying) |
| Description | A shrieking bird-woman that dives from above. Immune to earth effects while airborne. Sonic attacks debuff the entire party. |

**Class Modifiers:**
```
hit_dice: 8, mod_hp_flat: 0, mod_hp_mult: 3, mana_multiplier: 2
mod_atk_physical: 6, mod_atk_magical: 4
mod_def_physical: 3, mod_def_magical: 3
regen_hp_mod: 1, regen_mana_mod: 1
preferred_attack_type: PHYSICAL
```

**Base Attributes:** STR 8, DEX 16, CON 6, INT 6, WIS 8, CHA 6, MIND 4

**Estimated HP:** ((8 + 6 + 0) * 2) * 3 = 84 [PLACEHOLDER]

**Skills:**
- `dive_attack` -- ACTION, SINGLE_ENEMY: Damage base_power 14
- `sonic_screech_harpy` -- BONUS_ACTION, ALL_ENEMIES: Debuff PHYSICAL_DEFENSE -8 for 2 turns (cooldown 3)

**Special Traits:** `flying` -- Immune to EARTH element, high evasion

---

#### 2.3.4 Goblin Shaman

**Design Purpose**: First real enemy healer at tier 2. The "kill me first" target that transforms encounter priority. Teaches aggressive target selection.

| Field | Value |
|-------|-------|
| enemy_id | `goblin_shaman` |
| Name | Goblin Shaman |
| Tier | 2 |
| Archetype | HEALER |
| Position | BACK |
| Attack Type | MAGICAL |
| Element Affinity | EARTH |
| Weakness | FORCE 1.5x, FIRE 1.5x |
| Resistance | EARTH 0.5x |
| Description | A wizened goblin that channels earth magic to mend wounds and bolster allies. Left unchecked, it keeps the whole enemy party alive. |

**Class Modifiers:**
```
hit_dice: 6, mod_hp_flat: 1, mod_hp_mult: 3, mana_multiplier: 4
mod_atk_physical: 1, mod_atk_magical: 5
mod_def_physical: 2, mod_def_magical: 4
regen_hp_mod: 1, regen_mana_mod: 2
preferred_attack_type: MAGICAL
```

**Base Attributes:** STR 4, DEX 8, CON 6, INT 12, WIS 14, CHA 6, MIND 8

**Estimated HP:** ((6 + 6 + 1) * 2) * 3 = 78 [PLACEHOLDER]

**Skills:**
- `earth_mend` -- ACTION, SINGLE_ALLY: Heal base_power 20
- `rally_totem` -- BONUS_ACTION, ALL_ALLIES: Buff PHYSICAL_ATTACK +6 for 2 turns (cooldown 3)

**Special Traits:** `desperate_caster` -- When alone, switches to offensive magic

---

#### 2.3.5 Dark Mage

**Design Purpose**: Magical glass cannon with debuffs. Creates urgency: kill it fast or the party's defenses crumble.

| Field | Value |
|-------|-------|
| enemy_id | `dark_mage` |
| Name | Dark Mage |
| Tier | 2 |
| Archetype | DPS |
| Position | BACK |
| Attack Type | MAGICAL |
| Element Affinity | DARKNESS |
| Weakness | FORCE 1.5x, HOLY 1.5x |
| Resistance | DARKNESS 0.5x |
| Description | A robed sorcerer channeling dark energy. Alternates between devastating single-target bolts and defense-shredding curses. |

**Class Modifiers:**
```
hit_dice: 6, mod_hp_flat: 0, mod_hp_mult: 3, mana_multiplier: 5
mod_atk_physical: 1, mod_atk_magical: 8
mod_def_physical: 2, mod_def_magical: 5
regen_hp_mod: 0, regen_mana_mod: 2
preferred_attack_type: MAGICAL
```

**Base Attributes:** STR 4, DEX 6, CON 6, INT 16, WIS 10, CHA 4, MIND 10

**Estimated HP:** ((6 + 6 + 0) * 2) * 3 = 72 [PLACEHOLDER]

**Skills:**
- `dark_bolt_mage` -- ACTION, SINGLE_ENEMY: Damage base_power 16, element DARKNESS
- `hex_curse` -- BONUS_ACTION, SINGLE_ENEMY: Debuff MAGICAL_DEFENSE -10 for 3 turns (cooldown 3)

**Special Traits:** `desperation_aoe` -- When HP < 30%, casts AoE dark blast on all enemies

---

#### 2.3.6 Stone Guardian

**Design Purpose**: Tier 2 construct tank. Introduces damage immunity until a specific condition is met (core exposed).

| Field | Value |
|-------|-------|
| enemy_id | `stone_guardian` |
| Name | Stone Guardian |
| Tier | 2 |
| Archetype | TANK |
| Position | FRONT |
| Attack Type | PHYSICAL |
| Element Affinity | EARTH |
| Weakness | LIGHTNING 1.5x, WATER 1.5x |
| Resistance | EARTH 0.5x, PSYCHIC 0.0x (immune -- no mind) |
| Description | An animated stone sentinel guarding dungeon corridors. Its stone shell absorbs punishment until cracks appear. |

**Class Modifiers:**
```
hit_dice: 14, mod_hp_flat: 5, mod_hp_mult: 5, mana_multiplier: 0
mod_atk_physical: 5, mod_atk_magical: 1
mod_def_physical: 8, mod_def_magical: 4
regen_hp_mod: 1, regen_mana_mod: 0
preferred_attack_type: PHYSICAL
```

**Base Attributes:** STR 16, DEX 4, CON 16, INT 2, WIS 4, CHA 2, MIND 2

**Estimated HP:** ((14 + 16 + 5) * 2) * 5 = 350 [PLACEHOLDER]

**Skills:**
- `stone_slam` -- ACTION, SINGLE_ENEMY: Damage base_power 12

**Special Traits:** `stone_shell` -- Takes 30% less physical damage. `construct` -- Immune to PSYCHIC and POISON.

---

#### 2.3.7 Plague Rat

**Design Purpose**: Tier 2 evolution of the rat swarm concept. Applies stacking poison and disease, creating a ticking clock.

| Field | Value |
|-------|-------|
| enemy_id | `plague_rat` |
| Name | Plague Rat |
| Tier | 2 |
| Archetype | CONTROLLER |
| Position | FRONT |
| Attack Type | PHYSICAL |
| Element Affinity | DARKNESS |
| Weakness | FIRE 1.5x, HOLY 1.5x |
| Resistance | DARKNESS 0.5x |
| Description | A disease-ridden vermin that infects the party with stacking ailments. Each bite adds another layer of poison. Antidotes are precious. |

**Class Modifiers:**
```
hit_dice: 6, mod_hp_flat: 1, mod_hp_mult: 3, mana_multiplier: 0
mod_atk_physical: 5, mod_atk_magical: 2
mod_def_physical: 3, mod_def_magical: 2
regen_hp_mod: 1, regen_mana_mod: 0
preferred_attack_type: PHYSICAL
```

**Base Attributes:** STR 8, DEX 14, CON 8, INT 4, WIS 6, CHA 2, MIND 3

**Estimated HP:** ((6 + 8 + 1) * 2) * 3 = 90 [PLACEHOLDER]

**Skills:**
- `plague_bite` -- ACTION, SINGLE_ENEMY: Damage base_power 8, apply POISON (6 dmg/tick, 4 turns)
- `infectious_spray` -- BONUS_ACTION, ALL_ENEMIES: Apply POISON (3 dmg/tick, 2 turns) -- cooldown 4

**Special Traits:** `disease_carrier` -- Poison applied by this enemy cannot be cleansed for the first turn

---

#### 2.3.8 Shadow Assassin

**Design Purpose**: High-burst DPS that targets the backline. Punishes parties that leave casters unprotected. Creates a "protect your healer" dynamic.

| Field | Value |
|-------|-------|
| enemy_id | `shadow_assassin` |
| Name | Shadow Assassin |
| Tier | 2 |
| Archetype | DPS |
| Position | FRONT |
| Attack Type | PHYSICAL |
| Element Affinity | DARKNESS |
| Weakness | HOLY 1.5x, FIRE 1.5x |
| Resistance | DARKNESS 0.5x |
| Description | A cloaked figure that bypasses the frontline to strike at vulnerable targets. Deals massive damage to the backline on its first hit. |

**Class Modifiers:**
```
hit_dice: 8, mod_hp_flat: 0, mod_hp_mult: 3, mana_multiplier: 0
mod_atk_physical: 7, mod_atk_magical: 2
mod_def_physical: 3, mod_def_magical: 3
regen_hp_mod: 0, regen_mana_mod: 0
preferred_attack_type: PHYSICAL
```

**Base Attributes:** STR 10, DEX 16, CON 8, INT 6, WIS 8, CHA 4, MIND 4

**Estimated HP:** ((8 + 8 + 0) * 2) * 3 = 96 [PLACEHOLDER]

**Skills:**
- `backstab` -- ACTION, SINGLE_ENEMY: Damage base_power 18 (targets BACK position preferentially)
- `vanish` -- BONUS_ACTION, SELF: Buff PHYSICAL_DEFENSE +12 for 1 turn (dodge/stealth) -- cooldown 3

**Special Traits:** `ambush` -- First attack in combat deals +50% damage

---

### 2.4 Tier 3 -- 7 New Enemies (Floors 7-9)

---

#### 2.4.1 Mimic

**Design Purpose**: Surprise enemy that breaks expectations. Appears as a treasure chest, then attacks. Forces risk assessment of treasure rooms.

| Field | Value |
|-------|-------|
| enemy_id | `mimic` |
| Name | Mimic |
| Tier | 3 |
| Archetype | DPS |
| Position | FRONT |
| Attack Type | PHYSICAL (mixed) |
| Element Affinity | None (neutral) |
| Weakness | FORCE 1.5x |
| Resistance | Changes every 3 turns |
| Description | A shapeshifting predator disguised as a treasure chest. Ambushes the party and devours those who get too close. Extremely rewarding to kill. |

**Class Modifiers:**
```
hit_dice: 12, mod_hp_flat: 4, mod_hp_mult: 5, mana_multiplier: 0
mod_atk_physical: 9, mod_atk_magical: 4
mod_def_physical: 6, mod_def_magical: 4
regen_hp_mod: 2, regen_mana_mod: 0
preferred_attack_type: PHYSICAL
```

**Base Attributes:** STR 16, DEX 10, CON 14, INT 6, WIS 8, CHA 4, MIND 4

**Estimated HP:** ((12 + 14 + 4) * 2) * 5 = 300 [PLACEHOLDER]

**Skills:**
- `chomp` -- ACTION, SINGLE_ENEMY: Damage base_power 22
- `devour` -- ACTION, SINGLE_ENEMY: Damage base_power 12, apply STUN 1 turn (cooldown 4)

**Special Traits:** `surprise_round` -- Party cannot act on turn 1. `shifting_resistance` -- Changes elemental resistance every 3 turns.

---

#### 2.4.2 Basilisk

**Design Purpose**: Petrification threat creates extreme urgency. The player must either kill it fast or have WIS-based saves.

| Field | Value |
|-------|-------|
| enemy_id | `basilisk` |
| Name | Basilisk |
| Tier | 3 |
| Archetype | CONTROLLER |
| Position | FRONT |
| Attack Type | MAGICAL |
| Element Affinity | EARTH |
| Weakness | ICE 1.5x |
| Resistance | EARTH 0.0x (immune), POISON 0.0x (immune) |
| Description | A six-legged serpentine beast whose gaze turns flesh to stone. Its venom is lethal and its hide is armored with crystalline scales. |

**Class Modifiers:**
```
hit_dice: 14, mod_hp_flat: 5, mod_hp_mult: 5, mana_multiplier: 3
mod_atk_physical: 6, mod_atk_magical: 8
mod_def_physical: 7, mod_def_magical: 5
regen_hp_mod: 2, regen_mana_mod: 1
preferred_attack_type: MAGICAL
```

**Base Attributes:** STR 14, DEX 6, CON 16, INT 8, WIS 12, CHA 4, MIND 6

**Estimated HP:** ((14 + 16 + 5) * 2) * 5 = 350 [PLACEHOLDER]

**Skills:**
- `petrifying_gaze` -- ACTION, SINGLE_ENEMY: Apply STUN 2 turns (WIS save to reduce to 1 turn) -- cooldown 4
- `toxic_bite` -- ACTION, SINGLE_ENEMY: Damage base_power 14, apply POISON (8 dmg/tick, 4 turns)

**Special Traits:** `crystalline_scales` -- 20% physical damage reduction

---

#### 2.4.3 Vampire

**Design Purpose**: Sustain DPS that heals from damage. Creates a DPS race: the party must outdamage its lifesteal.

| Field | Value |
|-------|-------|
| enemy_id | `vampire` |
| Name | Vampire |
| Tier | 3 |
| Archetype | DPS |
| Position | FRONT |
| Attack Type | PHYSICAL (mixed) |
| Element Affinity | DARKNESS |
| Weakness | HOLY 2.0x, FIRE 1.5x |
| Resistance | DARKNESS 0.0x (immune) |
| Description | An ancient predator that grows stronger with each drop of blood drained. Holy damage is devastating, but getting close means feeding it. |

**Class Modifiers:**
```
hit_dice: 12, mod_hp_flat: 3, mod_hp_mult: 5, mana_multiplier: 2
mod_atk_physical: 9, mod_atk_magical: 5
mod_def_physical: 5, mod_def_magical: 5
regen_hp_mod: 3, regen_mana_mod: 1
preferred_attack_type: PHYSICAL
```

**Base Attributes:** STR 14, DEX 14, CON 12, INT 10, WIS 8, CHA 12, MIND 6

**Estimated HP:** ((12 + 12 + 3) * 2) * 5 = 270 [PLACEHOLDER]

**Skills:**
- `blood_drain` -- ACTION, SINGLE_ENEMY: Damage base_power 16, heals self for 30% of damage dealt
- `charm_gaze` -- BONUS_ACTION, SINGLE_ENEMY: Apply CONFUSION 2 turns (cooldown 4)

**Special Traits:** `lifesteal` -- 30% of all damage dealt heals self. `blood_frenzy` -- Each successful attack grants stacking +5% ATK (max 25%).

---

#### 2.4.4 Lich Acolyte

**Design Purpose**: Necromantic healer that resurrects fallen enemies. Creates a "kill the healer or fight forever" puzzle.

| Field | Value |
|-------|-------|
| enemy_id | `lich_acolyte` |
| Name | Lich Acolyte |
| Tier | 3 |
| Archetype | HEALER |
| Position | BACK |
| Attack Type | MAGICAL |
| Element Affinity | DARKNESS |
| Weakness | HOLY 2.0x, FORCE 1.5x |
| Resistance | DARKNESS 0.0x (immune), POISON 0.0x (immune) |
| Description | A disciple of the Lich Lord that channels necrotic energy to mend undead allies and raise the fallen. The most dangerous support in the dungeon. |

**Class Modifiers:**
```
hit_dice: 8, mod_hp_flat: 2, mod_hp_mult: 4, mana_multiplier: 5
mod_atk_physical: 1, mod_atk_magical: 7
mod_def_physical: 3, mod_def_magical: 7
regen_hp_mod: 1, regen_mana_mod: 3
preferred_attack_type: MAGICAL
```

**Base Attributes:** STR 4, DEX 6, CON 8, INT 16, WIS 14, CHA 8, MIND 14

**Estimated HP:** ((8 + 8 + 2) * 2) * 4 = 144 [PLACEHOLDER]

**Skills:**
- `necrotic_mend` -- ACTION, SINGLE_ALLY: Heal base_power 25
- `raise_undead` -- ACTION, special: Revive 1 dead ally at 40% HP (cooldown 5)
- `dark_bolt_acolyte` -- BONUS_ACTION, SINGLE_ENEMY: Damage base_power 10, element DARKNESS

**Special Traits:** `undead` -- Immune to POISON and BLEED. `desperate_caster` -- When alone, focuses on offensive magic + self-heal.

---

#### 2.4.5 Elemental (Shifting)

**Design Purpose**: Puzzle enemy. Forces the player to read the current element and respond with the correct counter-element each cycle.

| Field | Value |
|-------|-------|
| enemy_id | `elemental_shifter` |
| Name | Elemental |
| Tier | 3 |
| Archetype | CONTROLLER |
| Position | FRONT |
| Attack Type | MAGICAL |
| Element Affinity | Cycles: FIRE -> ICE -> LIGHTNING -> EARTH |
| Weakness | Opposite of current element |
| Resistance | Immune to current element |
| Description | A being of pure elemental energy that shifts its nature every 2 turns. Hit it with the wrong element and it absorbs the damage. |

**Class Modifiers:**
```
hit_dice: 12, mod_hp_flat: 4, mod_hp_mult: 5, mana_multiplier: 5
mod_atk_physical: 2, mod_atk_magical: 10
mod_def_physical: 5, mod_def_magical: 8
regen_hp_mod: 2, regen_mana_mod: 2
preferred_attack_type: MAGICAL
```

**Base Attributes:** STR 6, DEX 8, CON 12, INT 18, WIS 14, CHA 6, MIND 12

**Estimated HP:** ((12 + 12 + 4) * 2) * 5 = 280 [PLACEHOLDER]

**Skills:**
- `elemental_blast` -- ACTION, ALL_ENEMIES: Damage base_power 14, element = current element
- `phase_shift` -- Passive: Changes element every 2 turns with a burst of AoE damage (base_power 8)

**Special Traits:** `elemental_cycle` -- Rotates FIRE -> ICE -> LIGHTNING -> EARTH every 2 turns. Immune to current element, 2x weak to opposite.

---

#### 2.4.6 Demon Knight

**Design Purpose**: Tier 3 elite-style frontliner. High threat that demands focus. The party must decide: burn resources to kill it fast or endure its sustained pressure.

| Field | Value |
|-------|-------|
| enemy_id | `demon_knight` |
| Name | Demon Knight |
| Tier | 3 |
| Archetype | TANK |
| Position | FRONT |
| Attack Type | PHYSICAL |
| Element Affinity | FIRE |
| Weakness | HOLY 1.5x, ICE 1.5x |
| Resistance | FIRE 0.0x (immune), DARKNESS 0.5x |
| Description | An armored demon that burns with hellfire. Its attacks carry fire damage and its presence weakens nearby enemies' defenses. |

**Class Modifiers:**
```
hit_dice: 16, mod_hp_flat: 6, mod_hp_mult: 5, mana_multiplier: 1
mod_atk_physical: 8, mod_atk_magical: 4
mod_def_physical: 9, mod_def_magical: 6
regen_hp_mod: 2, regen_mana_mod: 0
preferred_attack_type: PHYSICAL
```

**Base Attributes:** STR 18, DEX 8, CON 16, INT 6, WIS 8, CHA 8, MIND 4

**Estimated HP:** ((16 + 16 + 6) * 2) * 5 = 380 [PLACEHOLDER]

**Skills:**
- `hellfire_slash` -- ACTION, SINGLE_ENEMY: Damage base_power 18, element FIRE, apply BURN (6 dmg/tick, 3 turns)
- `infernal_presence` -- BONUS_ACTION, ALL_ENEMIES: Debuff PHYSICAL_DEFENSE -8 for 2 turns (cooldown 4)

**Special Traits:** `fire_aura_t3` -- Melee attackers take 8 FIRE damage per hit. `demonic_resilience` -- Takes 15% less magic damage.

---

#### 2.4.7 Mind Flayer

**Design Purpose**: Psychic horror that disables the party's strongest member. Forces adaptation when your best character is confused or silenced.

| Field | Value |
|-------|-------|
| enemy_id | `mind_flayer` |
| Name | Mind Flayer |
| Tier | 3 |
| Archetype | CONTROLLER |
| Position | BACK |
| Attack Type | MAGICAL |
| Element Affinity | PSYCHIC |
| Weakness | FORCE 1.5x |
| Resistance | PSYCHIC 0.0x (immune), DARKNESS 0.5x |
| Description | A tentacled aberration that devours thoughts. Its psychic attacks bypass physical defenses entirely and target the mind directly. |

**Class Modifiers:**
```
hit_dice: 10, mod_hp_flat: 3, mod_hp_mult: 4, mana_multiplier: 6
mod_atk_physical: 2, mod_atk_magical: 10
mod_def_physical: 4, mod_def_magical: 8
regen_hp_mod: 1, regen_mana_mod: 3
preferred_attack_type: MAGICAL
```

**Base Attributes:** STR 6, DEX 8, CON 10, INT 20, WIS 16, CHA 10, MIND 16

**Estimated HP:** ((10 + 10 + 3) * 2) * 4 = 184 [PLACEHOLDER]

**Skills:**
- `mind_blast` -- ACTION, ALL_ENEMIES: Damage base_power 12, element PSYCHIC, 30% chance CONFUSION 2 turns
- `dominate` -- ACTION, SINGLE_ENEMY: Apply CONFUSION 3 turns (targets highest ATK enemy) -- cooldown 5
- `psychic_drain` -- BONUS_ACTION, SINGLE_ENEMY: Damage base_power 8, steals 20 mana

**Special Traits:** `telepathic_shield` -- Immune to CONFUSION and SILENCE. `mind_reader` -- Always targets the party member with the highest damage potential.

---

### 2.5 Enemy Roster Summary Table

| Tier | Enemy ID | Archetype | Position | Element | Key Threat |
|------|----------|-----------|----------|---------|------------|
| 1 | kobold_trapper | CONTROLLER | BACK | EARTH | Position disruption |
| 1 | cave_bat | DPS | BACK | DARKNESS | Speed + confusion |
| 1 | vine_creeper | HEALER | BACK | EARTH | Sustain healing |
| 1 | fire_imp | DPS | BACK | FIRE | Burn DoTs |
| 1 | armored_beetle | TANK | FRONT | EARTH | Physical wall |
| 2 | orc_warrior | TANK | FRONT | Neutral | Taunt + intercept |
| 2 | wraith | CONTROLLER | BACK | DARKNESS | Mana drain + silence |
| 2 | harpy | DPS | BACK | FORCE | Flying + screech debuff |
| 2 | goblin_shaman | HEALER | BACK | EARTH | Enemy healing |
| 2 | dark_mage | DPS | BACK | DARKNESS | Magical burst + curse |
| 2 | stone_guardian | TANK | FRONT | EARTH | Construct immunity |
| 2 | plague_rat | CONTROLLER | FRONT | DARKNESS | Stacking poison |
| 2 | shadow_assassin | DPS | FRONT | DARKNESS | Backline targeting |
| 3 | mimic | DPS | FRONT | Neutral | Surprise + burst |
| 3 | basilisk | CONTROLLER | FRONT | EARTH | Petrification |
| 3 | vampire | DPS | FRONT | DARKNESS | Lifesteal sustain |
| 3 | lich_acolyte | HEALER | BACK | DARKNESS | Resurrect dead enemies |
| 3 | elemental_shifter | CONTROLLER | FRONT | Cycles | Element puzzle |
| 3 | demon_knight | TANK | FRONT | FIRE | Fire aura + tankiness |
| 3 | mind_flayer | CONTROLLER | BACK | PSYCHIC | Mind control + disable |

**Archetype Distribution:**
- DPS: 7 (35%) -- T1: 2, T2: 3, T3: 2
- TANK: 5 (25%) -- T1: 1, T2: 2, T3: 2 (includes demon_knight as T3 tank)
- CONTROLLER: 6 (30%) -- T1: 1, T2: 2, T3: 3
- HEALER: 3 (15%) -- T1: 1, T2: 1, T3: 1

This gives 1 HEALER per tier to serve as priority targets, enough TANKs and CONTROLLERs to create varied encounter compositions, and enough DPS to keep pressure on the player.

---

## 3. Boss Expansion

### 3.1 Design Philosophy

Every boss follows these rules:
1. **2-3 phases** with HP thresholds (readable power spikes)
2. **Unique mechanic** that cannot be brute-forced (requires strategy)
3. **Battle cry** on transition (dramatic moment, gives the player a beat to react)
4. **Loot table** tied to the boss theme
5. **No adds on phase 1** (let the player learn the boss's patterns first)

Boss HP is significantly higher than normal enemies. Using the existing Goblin King as a baseline:
- Goblin King HP: ((12 + 12 + 5) * 2) * 5 = 290
- Tier 1 bosses: ~250-400 HP
- Tier 2 bosses: ~400-650 HP
- Tier 3 bosses: ~600-1000 HP

---

### 3.2 Tier 1 Bosses (End of Floors 1-3)

The existing Goblin King remains as boss #1. These are 3 alternative tier 1 bosses. Each run randomly selects one.

---

#### 3.2.1 Broodmother (Giant Spider Queen)

**Theme**: Swarm pressure + poison. The longer the fight goes, the more spiderlings appear.

| Field | Value |
|-------|-------|
| enemy_id | `broodmother` |
| Name | Broodmother |
| Tier | 1 |
| Archetype | CONTROLLER |
| Position | FRONT |
| Element | DARKNESS |
| Weakness | FIRE 2.0x |
| Resistance | DARKNESS 0.5x, POISON 0.0x (immune) |

**Class Modifiers:**
```
hit_dice: 10, mod_hp_flat: 4, mod_hp_mult: 5, mana_multiplier: 2
mod_atk_physical: 6, mod_atk_magical: 5
mod_def_physical: 5, mod_def_magical: 4
regen_hp_mod: 2, regen_mana_mod: 1
preferred_attack_type: PHYSICAL
```

**Base Attributes:** STR 12, DEX 10, CON 14, INT 8, WIS 10, CHA 6, MIND 6

**Estimated HP:** ((10 + 14 + 4) * 2) * 5 = 280 [PLACEHOLDER]

**Phase 1 (100% - 50% HP):**
- handler_key: `broodmother_p1`
- Skills: `web_trap` (ACTION, SINGLE_ENEMY: apply SLOW 2 turns + POISON 3 dmg/tick 3 turns)
- Behavior: Single target control. Webs the party's DPS to reduce incoming damage.

**Phase 2 (50% - 0% HP):**
- handler_key: `broodmother_p2`
- Transition: "The Broodmother shrieks! Eggs hatch across the chamber!"
- Self-buffs: SPEED +20% (duration 999)
- Skills: `venom_spray` (ACTION, ALL_ENEMIES: Damage base_power 10, apply POISON 5 dmg/tick 4 turns), `spawn_spiderlings` (summon 2 cave_bat-tier minions every 3 turns)
- Behavior: AoE pressure. Spiderlings distract while boss poisons.

**Unique Mechanic:** Spiderlings spawned in phase 2 have only 25 HP each but deal 8 damage per hit. Killing them before they act is critical. Fire AoE trivializes this -- intentional design to reward elemental preparation.

**Loot Table:**
- Guaranteed: 1 consumable (antidote or health potion)
- Pool: spider_fang_dagger (uncommon weapon, DARKNESS + poison on-hit), web_armor (light armor +3 PHYSICAL_DEF), venom_vial (consumable: apply poison to weapon for 1 combat)

---

#### 3.2.2 Frost Warden

**Theme**: Attrition boss. Slowly freezes the party's actions. The player races against the clock before everyone is frozen.

| Field | Value |
|-------|-------|
| enemy_id | `frost_warden` |
| Name | Frost Warden |
| Tier | 1 |
| Archetype | TANK |
| Position | FRONT |
| Element | ICE |
| Weakness | FIRE 2.0x, LIGHTNING 1.5x |
| Resistance | ICE 0.0x (immune), WATER 0.5x |

**Class Modifiers:**
```
hit_dice: 14, mod_hp_flat: 5, mod_hp_mult: 5, mana_multiplier: 2
mod_atk_physical: 5, mod_atk_magical: 5
mod_def_physical: 7, mod_def_magical: 5
regen_hp_mod: 2, regen_mana_mod: 1
preferred_attack_type: PHYSICAL
```

**Base Attributes:** STR 14, DEX 6, CON 16, INT 8, WIS 10, CHA 4, MIND 6

**Estimated HP:** ((14 + 16 + 5) * 2) * 5 = 350 [PLACEHOLDER]

**Phase 1 (100% - 50% HP):**
- handler_key: `frost_warden_p1`
- Skills: `frost_slash` (ACTION, SINGLE_ENEMY: Damage base_power 12, element ICE, apply COLD 2 turns)
- Behavior: Focuses frontline. Applies COLD to slow the party.

**Phase 2 (50% - 0% HP):**
- handler_key: `frost_warden_p2`
- Transition: "The Frost Warden's core erupts with glacial energy!"
- Self-buffs: PHYSICAL_DEFENSE +25% (duration 999), MAGICAL_DEFENSE +25% (duration 999)
- Skills: `blizzard_breath` (ACTION, ALL_ENEMIES: Damage base_power 10, element ICE, apply COLD 3 turns + FREEZE 1 turn on 30% chance), `ice_armor` (BONUS_ACTION, SELF: Heal 10% max HP, cooldown 3)
- Behavior: AoE freeze + self-sustain. Becomes extremely defensive.

**Unique Mechanic:** Accumulating COLD debuffs stack. At 3 stacks, target is FROZEN for 1 turn (cannot act). Fire damage removes 1 stack of COLD per hit. Party must manage COLD stacks or lose actions.

**Loot Table:**
- Guaranteed: 1 weapon or armor
- Pool: frost_blade (uncommon sword, ICE element), ice_ward_shield (armor +5 MAGICAL_DEF), frost_crystal (consumable: ICE resistance 1 combat)

---

#### 3.2.3 Bandit Warlord

**Theme**: Action economy boss. Brings 2 bandit lieutenants. Killing lieutenants makes the warlord stronger but reduces enemy action count.

| Field | Value |
|-------|-------|
| enemy_id | `bandit_warlord` |
| Name | Bandit Warlord |
| Tier | 1 |
| Archetype | DPS |
| Position | FRONT |
| Element | Neutral |
| Weakness | HOLY 1.5x |
| Resistance | None |

**Class Modifiers:**
```
hit_dice: 12, mod_hp_flat: 3, mod_hp_mult: 5, mana_multiplier: 0
mod_atk_physical: 7, mod_atk_magical: 2
mod_def_physical: 5, mod_def_magical: 3
regen_hp_mod: 2, regen_mana_mod: 0
preferred_attack_type: PHYSICAL
```

**Base Attributes:** STR 14, DEX 12, CON 12, INT 6, WIS 8, CHA 10, MIND 4

**Estimated HP:** ((12 + 12 + 3) * 2) * 5 = 270 [PLACEHOLDER]

**Phase 1 (100% - 40% HP):**
- handler_key: `bandit_warlord_p1`
- Skills: `command_strike` (BONUS_ACTION, ALL_ALLIES: Buff PHYSICAL_ATTACK +8 for 2 turns, cooldown 3)
- Behavior: Buffs lieutenants and attacks frontline. Lieutenants are 2x goblin-tier bandits (50 HP each).
- **Starts with 2 Bandit Lieutenants** (tier 1 DPS, 50 HP each)

**Phase 2 (40% - 0% HP):**
- handler_key: `bandit_warlord_p2`
- Transition: "The Warlord draws a second blade! 'Fine, I'll do it myself!'"
- Self-buffs: PHYSICAL_ATTACK +30% (duration 999), SPEED +20% (duration 999)
- Skills: `dual_strike` (ACTION, SINGLE_ENEMY: 2 hits of base_power 12 each), `intimidating_shout` (BONUS_ACTION, ALL_ENEMIES: Debuff PHYSICAL_ATTACK -6 for 2 turns, cooldown 4)
- Behavior: Pure aggression. Double attacks per turn.

**Unique Mechanic:** Each dead lieutenant gives the Warlord +15% ATK permanently (stacks). Killing both lieutenants gives +30% ATK to the Warlord but removes 2 enemy actions per turn. The player chooses: fight 3 enemies with normal warlord, or 1 enraged warlord.

**Loot Table:**
- Guaranteed: 1 weapon
- Pool: warlord_blade (uncommon longsword, high weapon_die 10), bandit_cloak (cloak +4 SPEED, +3 PHYSICAL_DEF), stolen_gold_pouch (bonus 50 gold)

---

### 3.3 Tier 2 Bosses (End of Floors 4-6)

The existing Ancient Golem remains as one option. These are 3 additional tier 2 bosses.

---

#### 3.3.1 Hydra

**Theme**: Multi-head boss. Each head acts independently. Cutting a head spawns two more (up to a cap). The player must find the body's weak point.

| Field | Value |
|-------|-------|
| enemy_id | `hydra` |
| Name | Hydra |
| Tier | 2 |
| Archetype | DPS |
| Position | FRONT |
| Element | WATER |
| Weakness | FIRE 1.5x (cauterizes stumps), LIGHTNING 1.5x |
| Resistance | WATER 0.0x (immune), ICE 0.5x |

**Class Modifiers:**
```
hit_dice: 14, mod_hp_flat: 6, mod_hp_mult: 6, mana_multiplier: 1
mod_atk_physical: 8, mod_atk_magical: 4
mod_def_physical: 6, mod_def_magical: 4
regen_hp_mod: 3, regen_mana_mod: 0
preferred_attack_type: PHYSICAL
```

**Base Attributes:** STR 16, DEX 8, CON 18, INT 4, WIS 6, CHA 4, MIND 3

**Estimated HP:** ((14 + 18 + 6) * 2) * 6 = 456 [PLACEHOLDER]

**Phase 1 (100% - 60% HP) -- 3 Heads:**
- handler_key: `hydra_p1`
- Skills: `triple_bite` (ACTION, 3 random enemies: Damage base_power 10 each), `regenerate` (passive: heals 5% max HP per turn)
- Behavior: Attacks 3 targets per turn. Regen keeps it topped up.

**Phase 2 (60% - 25% HP) -- 5 Heads:**
- handler_key: `hydra_p2`
- Transition: "Two heads sprout where one was severed!"
- Self-buffs: SPEED +15% (duration 999)
- Skills: `multi_bite` (ACTION, ALL_ENEMIES: Damage base_power 8 to each enemy), `acid_spray` (BONUS_ACTION, ALL_ENEMIES: Damage base_power 6, apply BURN 4 dmg/tick 3 turns, cooldown 3)
- Behavior: Full party pressure. Regen accelerates to 8% per turn.

**Phase 3 (25% - 0% HP) -- Weakened Core:**
- handler_key: `hydra_p3`
- Transition: "The Hydra thrashes wildly, its core exposed!"
- Self-buffs: PHYSICAL_DEFENSE -20% (duration 999)
- Skills: `death_thrash` (ACTION, ALL_ENEMIES: Damage base_power 14)
- Behavior: Desperate AoE. Regen stops. Defense drops. Race to finish.

**Unique Mechanic:** FIRE damage prevents regen for 2 turns. Without fire, the hydra out-heals most parties. Intentionally hard counter: bring fire or prepare for a long fight.

**Loot Table:**
- Guaranteed: 2 items
- Pool: hydra_fang (rare dagger, WATER + high crit), scale_mail_of_regeneration (rare armor, HP_REGEN +5), hydra_blood (consumable: full HP heal, single use)

---

#### 3.3.2 Shadow Matriarch

**Theme**: Summon boss that creates shadow clones. Only the real one takes damage. Wrong target = wasted turns.

| Field | Value |
|-------|-------|
| enemy_id | `shadow_matriarch` |
| Name | Shadow Matriarch |
| Tier | 2 |
| Archetype | CONTROLLER |
| Position | BACK |
| Element | DARKNESS |
| Weakness | HOLY 2.0x, LIGHT-based damage reveals real form |
| Resistance | DARKNESS 0.0x (immune), PSYCHIC 0.5x |

**Class Modifiers:**
```
hit_dice: 10, mod_hp_flat: 4, mod_hp_mult: 5, mana_multiplier: 5
mod_atk_physical: 3, mod_atk_magical: 9
mod_def_physical: 4, mod_def_magical: 7
regen_hp_mod: 1, regen_mana_mod: 3
preferred_attack_type: MAGICAL
```

**Base Attributes:** STR 4, DEX 12, CON 10, INT 18, WIS 14, CHA 12, MIND 14

**Estimated HP:** ((10 + 10 + 4) * 2) * 5 = 240 [PLACEHOLDER] (lower HP because hard to hit)

**Phase 1 (100% - 50% HP):**
- handler_key: `shadow_matriarch_p1`
- Skills: `shadow_bolt` (ACTION, SINGLE_ENEMY: Damage base_power 16, element DARKNESS), `nightmare` (BONUS_ACTION, SINGLE_ENEMY: Apply CONFUSION 2 turns, cooldown 3)
- Behavior: Standard backline caster. Debuffs and damages.

**Phase 2 (50% - 0% HP):**
- handler_key: `shadow_matriarch_p2`
- Transition: "The Matriarch dissolves into shadow! Three figures appear!"
- Self-buffs: MAGICAL_ATTACK +20% (duration 999)
- Skills: `shadow_storm` (ACTION, ALL_ENEMIES: Damage base_power 12, element DARKNESS), `create_decoy` (creates 2 shadow clones with 1 HP each that look identical)
- Behavior: Hides among clones. Only the real one takes meaningful damage.

**Unique Mechanic:** In phase 2, the boss creates 2 shadow clones with identical appearance. Clones have 1 HP but only take damage from HOLY or FORCE attacks. Hitting a clone with normal attacks does nothing. The player must use detection (WIS check or HOLY damage) to find the real one. HOLY AoE trivializes this mechanic -- intentional design to reward elemental preparation.

**Loot Table:**
- Guaranteed: 1 accessory
- Pool: shadow_veil (rare cloak, SPEED +5, MAGICAL_DEFENSE +6), dark_scepter (rare staff, DARKNESS element, high base_power), shadow_essence (consumable: invisibility 1 turn in combat)

---

#### 3.3.3 War Golem Mk-II

**Theme**: Mechanical boss that charges devastating attacks. The player can see the charge coming and must decide: burst it down, or brace for impact.

| Field | Value |
|-------|-------|
| enemy_id | `war_golem_mk2` |
| Name | War Golem Mk-II |
| Tier | 2 |
| Archetype | TANK |
| Position | FRONT |
| Element | LIGHTNING |
| Weakness | WATER 1.5x, EARTH 1.5x |
| Resistance | LIGHTNING 0.0x (immune), PSYCHIC 0.0x (immune -- construct) |

**Class Modifiers:**
```
hit_dice: 16, mod_hp_flat: 8, mod_hp_mult: 6, mana_multiplier: 0
mod_atk_physical: 7, mod_atk_magical: 3
mod_def_physical: 10, mod_def_magical: 5
regen_hp_mod: 2, regen_mana_mod: 0
preferred_attack_type: PHYSICAL
```

**Base Attributes:** STR 20, DEX 4, CON 20, INT 2, WIS 4, CHA 2, MIND 2

**Estimated HP:** ((16 + 20 + 8) * 2) * 6 = 528 [PLACEHOLDER]

**Phase 1 (100% - 40% HP):**
- handler_key: `war_golem_p1`
- Skills: `tesla_punch` (ACTION, SINGLE_ENEMY: Damage base_power 14, element LIGHTNING), `charge_cannon` (BONUS_ACTION, SELF: Spends turn "charging" -- next turn fires `cannon_blast`)
- `cannon_blast` (ACTION, ALL_ENEMIES: Damage base_power 22 -- only fires after charging)
- Behavior: Alternates between punches and charging. Charge is telegraphed -- player has 1 turn to prepare.

**Phase 2 (40% - 0% HP):**
- handler_key: `war_golem_p2`
- Transition: "Steam erupts from the Golem's core! Overcharge protocol activated!"
- Self-buffs: PHYSICAL_ATTACK +25% (duration 999), SPEED +30% (duration 999)
- Skills: `overcharge_slam` (ACTION, ALL_ENEMIES: Damage base_power 18), `tesla_field` (BONUS_ACTION, ALL_ENEMIES: Damage base_power 6, element LIGHTNING, apply PARALYSIS 1 turn -- cooldown 4)
- Behavior: No more charging -- attacks every turn. Faster and more dangerous.

**Unique Mechanic:** During the `charge_cannon` turn in phase 1, the golem's defenses drop by 50%. This is the optimal DPS window. Observant players exploit this. In phase 2, there are no more charge turns, making it a pure DPS race.

**Loot Table:**
- Guaranteed: 1 weapon or armor
- Pool: golem_core (rare accessory, +12 PHYSICAL_ATTACK, +8 MAX_HP), tesla_gauntlet (rare weapon, LIGHTNING element, weapon_die 12), reinforced_plate (rare heavy armor, +8 CA, +40 HP)

---

### 3.4 Tier 3 Bosses (End of Floors 7-9)

The existing Lich Lord remains as one option. These are 3 additional tier 3 bosses.

---

#### 3.4.1 Dragon (Inferno Wyrm)

**Theme**: Classic final boss. Overwhelming power with a flight phase where it is untargetable by melee. Tests the party's full kit.

| Field | Value |
|-------|-------|
| enemy_id | `inferno_wyrm` |
| Name | Inferno Wyrm |
| Tier | 3 |
| Archetype | DPS |
| Position | FRONT |
| Element | FIRE |
| Weakness | ICE 1.5x, WATER 1.5x |
| Resistance | FIRE 0.0x (immune), EARTH 0.5x |

**Class Modifiers:**
```
hit_dice: 18, mod_hp_flat: 10, mod_hp_mult: 6, mana_multiplier: 3
mod_atk_physical: 10, mod_atk_magical: 8
mod_def_physical: 8, mod_def_magical: 6
regen_hp_mod: 3, regen_mana_mod: 1
preferred_attack_type: PHYSICAL
```

**Base Attributes:** STR 20, DEX 10, CON 20, INT 12, WIS 10, CHA 14, MIND 8

**Estimated HP:** ((18 + 20 + 10) * 2) * 6 = 576 [PLACEHOLDER]

**Phase 1 (100% - 60% HP) -- Grounded:**
- handler_key: `inferno_wyrm_p1`
- Skills: `claw_rend` (ACTION, SINGLE_ENEMY: Damage base_power 20), `fire_breath` (ACTION, ALL_ENEMIES: Damage base_power 14, element FIRE, apply BURN 8 dmg/tick 3 turns -- cooldown 3)
- Behavior: Melee + periodic fire breath. Targets frontline.

**Phase 2 (60% - 30% HP) -- Airborne:**
- handler_key: `inferno_wyrm_p2`
- Transition: "The Wyrm takes flight! Its scales glow with molten fury!"
- Self-buffs: PHYSICAL_DEFENSE +30% (duration until next phase)
- Skills: `aerial_flame_rain` (ACTION, ALL_ENEMIES: Damage base_power 16, element FIRE), `dive_bomb` (ACTION, SINGLE_ENEMY: Damage base_power 24, returns to air -- cooldown 4)
- Behavior: Only ranged attacks can hit it. Melee characters must use skills or items. Periodically dives for massive single-target damage.

**Phase 3 (30% - 0% HP) -- Desperate Fury:**
- handler_key: `inferno_wyrm_p3`
- Transition: "The Wyrm crashes down, wounded and enraged!"
- Self-buffs: PHYSICAL_ATTACK +40% (duration 999), PHYSICAL_DEFENSE -30% (duration 999)
- Skills: `inferno_nova` (ACTION, ALL_ENEMIES: Damage base_power 22, element FIRE, apply BURN 10 dmg/tick 3 turns), `tail_sweep` (BONUS_ACTION, ALL_ENEMIES: Damage base_power 10)
- Behavior: Glass cannon. Massive damage but much lower defense. The final DPS race.

**Unique Mechanic:** Phase 2 airborne state makes the dragon immune to melee basic attacks. Only ranged weapons, magic, and consumables can hit it. ICE damage forces it to land 1 turn early. This tests party composition diversity.

**Loot Table:**
- Guaranteed: 2 items, 1 guaranteed rare+
- Pool: dragon_fang_blade (legendary sword, FIRE element, weapon_die 14), wyrm_scale_armor (legendary heavy armor, +10 CA, +50 HP, FIRE resistance), inferno_heart (legendary accessory, +15 PHYSICAL_ATTACK, FIRE immunity)

---

#### 3.4.2 The Forgotten King (Undead Sovereign)

**Theme**: Undead boss that commands the dead. Each round, the battlefield fills with more undead. Holy damage is critical.

| Field | Value |
|-------|-------|
| enemy_id | `forgotten_king` |
| Name | The Forgotten King |
| Tier | 3 |
| Archetype | CONTROLLER |
| Position | BACK |
| Element | DARKNESS |
| Weakness | HOLY 2.0x, FIRE 1.5x |
| Resistance | DARKNESS 0.0x (immune), POISON 0.0x (immune) |

**Class Modifiers:**
```
hit_dice: 12, mod_hp_flat: 6, mod_hp_mult: 5, mana_multiplier: 6
mod_atk_physical: 4, mod_atk_magical: 11
mod_def_physical: 6, mod_def_magical: 9
regen_hp_mod: 2, regen_mana_mod: 3
preferred_attack_type: MAGICAL
```

**Base Attributes:** STR 8, DEX 6, CON 14, INT 20, WIS 18, CHA 16, MIND 16

**Estimated HP:** ((12 + 14 + 6) * 2) * 5 = 320 [PLACEHOLDER] (lower HP, compensated by summons)

**Phase 1 (100% - 60% HP) -- The Court Assembles:**
- handler_key: `forgotten_king_p1`
- Skills: `death_decree` (ACTION, SINGLE_ENEMY: Damage base_power 18, element DARKNESS), `raise_guard` (BONUS_ACTION: Summon 1 skeleton at 80% stats, cooldown 3)
- Behavior: Summons skeletons while dealing moderate damage. Max 2 summons at a time.

**Phase 2 (60% - 25% HP) -- The Court Rages:**
- handler_key: `forgotten_king_p2`
- Transition: "The Forgotten King raises his scepter! The dead answer his call!"
- Self-buffs: MAGICAL_ATTACK +30% (duration 999)
- Skills: `necrotic_wave` (ACTION, ALL_ENEMIES: Damage base_power 16, element DARKNESS, apply debuff -8 MAGICAL_DEFENSE 3 turns), `mass_raise` (summon 2 skeletons at once, cooldown 4)
- Behavior: Aggressive summoning + AoE. Max 3 summons at a time.

**Phase 3 (25% - 0% HP) -- Last Rites:**
- handler_key: `forgotten_king_p3`
- Transition: "With a scream of rage, the King sacrifices his court!"
- Self-buffs: All living summons die, King heals 15% HP per summon killed, MAGICAL_ATTACK +50% (duration 999)
- Skills: `soul_reap` (ACTION, ALL_ENEMIES: Damage base_power 24, element DARKNESS), `death_touch` (BONUS_ACTION, SINGLE_ENEMY: Damage base_power 14, apply POISON 10 dmg/tick 3 turns, cooldown 3)
- Behavior: No more summoning. Pure magical devastation.

**Unique Mechanic:** Killing summoned undead heals the King for 5% max HP each. The player must choose: kill the summons to reduce incoming damage (but heal the boss), or ignore them and focus the King (but take more hits). In phase 3, the King sacrifices all remaining summons for a massive heal, punishing players who left too many alive.

**Loot Table:**
- Guaranteed: 2 items, 1 legendary chance (20%)
- Pool: crown_of_the_damned (legendary accessory, +15 MAGICAL_ATTACK, +10 MAGICAL_DEFENSE, DARKNESS element on all attacks), soulreaper_staff (legendary staff, DARKNESS element, weapon_die 14, lifesteal 10%), royal_plate (rare armor, +8 CA, +30 HP, HOLY resistance)

---

#### 3.4.3 The Warden of Adnos

**Theme**: True final boss. Tests everything the player has learned. Multi-element, multi-phase, with mechanics from every previous boss tier.

| Field | Value |
|-------|-------|
| enemy_id | `warden_of_adnos` |
| Name | The Warden of Adnos |
| Tier | 3 |
| Archetype | TANK (shifts) |
| Position | FRONT |
| Element | Cycles all elements |
| Weakness | Changes per phase |
| Resistance | Changes per phase |

**Class Modifiers:**
```
hit_dice: 18, mod_hp_flat: 10, mod_hp_mult: 6, mana_multiplier: 4
mod_atk_physical: 9, mod_atk_magical: 9
mod_def_physical: 8, mod_def_magical: 8
regen_hp_mod: 3, regen_mana_mod: 2
preferred_attack_type: PHYSICAL
```

**Base Attributes:** STR 18, DEX 12, CON 20, INT 16, WIS 16, CHA 14, MIND 14

**Estimated HP:** ((18 + 20 + 10) * 2) * 6 = 576 [PLACEHOLDER]

**Phase 1 (100% - 65% HP) -- Physical Form:**
- handler_key: `warden_p1`
- Element: Neutral
- Weakness: None
- Skills: `warden_slash` (ACTION, SINGLE_ENEMY: Damage base_power 20), `guardian_stance` (BONUS_ACTION, SELF: Buff +15 PHYSICAL_DEFENSE 2 turns, cooldown 3)
- Behavior: Pure physical tank. Tests the party's sustained DPS.

**Phase 2 (65% - 35% HP) -- Elemental Form:**
- handler_key: `warden_p2`
- Transition: "The Warden channels the elements of Adnos!"
- Element: Cycles FIRE/ICE/LIGHTNING/EARTH every 2 turns
- Weakness: Opposite of current element
- Self-buffs: MAGICAL_ATTACK +30% (duration 999)
- Skills: `elemental_judgment` (ACTION, ALL_ENEMIES: Damage base_power 16, element = current), `elemental_barrier` (passive: immune to current element)
- Behavior: Tests elemental knowledge. Player must exploit weakness windows.

**Phase 3 (35% - 0% HP) -- Transcendent Form:**
- handler_key: `warden_p3`
- Transition: "The Warden transcends! All elements converge!"
- Element: ALL (attacks with random element each turn)
- Weakness: FORCE 1.5x (the only constant weakness)
- Self-buffs: PHYSICAL_ATTACK +30%, MAGICAL_ATTACK +30%, SPEED +30% (all duration 999), PHYSICAL_DEFENSE -20%, MAGICAL_DEFENSE -20% (all duration 999)
- Skills: `convergence_blast` (ACTION, ALL_ENEMIES: Damage base_power 20, random element), `reality_tear` (BONUS_ACTION, SINGLE_ENEMY: Damage base_power 14, apply random ailment 2 turns, cooldown 3), `warden_heal` (passive: heals 3% max HP per turn)
- Behavior: Everything at once. Glass cannon with regen. Tests resource management.

**Unique Mechanic:** In phase 3, the Warden's element is random each turn. The player cannot predict and must react. FORCE damage is always effective (1.5x) -- the reward for finding force weapons/skills throughout the run. This is the final knowledge check.

**Loot Table:**
- Guaranteed: 3 items, 1 guaranteed legendary
- Pool: warden_blade (legendary sword, changes element each hit, weapon_die 14), aegis_of_adnos (legendary armor, +12 CA, +60 HP, all element resistance 0.75x), warden_signet (legendary ring, +12 all ATK, +8 all DEF)

---

### 3.5 Boss Roster Summary

| Boss | Tier | Archetype | Element | Key Mechanic | Phase Count |
|------|------|-----------|---------|--------------|-------------|
| Goblin King (existing) | 1 | DPS | Neutral | Summon goblins, enrage | 2 |
| Broodmother | 1 | CONTROLLER | DARKNESS | Spiderling swarm, poison AoE | 2 |
| Frost Warden | 1 | TANK | ICE | Freeze stacking, COLD management | 2 |
| Bandit Warlord | 1 | DPS | Neutral | Lieutenant sacrifice tradeoff | 2 |
| Ancient Golem (existing) | 2 | TANK | Neutral | Core exposed window, split | 2 |
| Hydra | 2 | DPS | WATER | Multi-head, regen vs fire | 3 |
| Shadow Matriarch | 2 | CONTROLLER | DARKNESS | Clone deception, HOLY reveal | 2 |
| War Golem Mk-II | 2 | TANK | LIGHTNING | Charge telegraph, DPS window | 2 |
| Lich Lord (existing) | 3 | CONTROLLER | DARKNESS | Phylactery, undead revive | 2 |
| Inferno Wyrm | 3 | DPS | FIRE | Flight phase, ICE ground | 3 |
| Forgotten King | 3 | CONTROLLER | DARKNESS | Summon sacrifice tradeoff | 3 |
| Warden of Adnos | 3 | TANK (shifts) | All | Element cycle, final test | 3 |

---

## 4. Advanced Consumables

### 4.1 Design Rationale

Current consumables are tier 1 only. The expansion adds:
- **Tier 2 potions**: ~2x strength of tier 1, appropriate for floors 4-6 economy
- **Tier 3 potions**: ~3-4x strength, rare and expensive
- **Utility items**: Strategic tools that open new combat options
- **Elemental items**: Exploit the elemental system through consumables

**Pricing follows the economy doc**: Tier 1 potions cost 10-25g, tier 2 cost 25-60g, tier 3 cost 60-150g. Player gold per floor averages 190/450/840, so a tier 3 potion represents ~10-18% of a floor's income.

---

### 4.2 Tier 2 Consumables (6 items)

#### 4.2.1 Medium Health Potion
```json
{
  "health_potion_medium": {
    "name": "Medium Health Potion",
    "category": "HEALING",
    "mana_cost": 0,
    "target_type": "SELF",
    "effects": [{"effect_type": "HEAL_HP", "base_power": 120}],
    "max_stack": 5,
    "description": "Restaura 120 HP",
    "usable_outside_combat": true,
    "price": 30,
    "tier": 2
  }
}
```
**Balance note**: 2.4x the small potion. Costs 2x. Slightly more gold-efficient to reward progression.

#### 4.2.2 Medium Mana Potion
```json
{
  "mana_potion_medium": {
    "name": "Medium Mana Potion",
    "category": "HEALING",
    "mana_cost": 0,
    "target_type": "SELF",
    "effects": [{"effect_type": "HEAL_MANA", "base_power": 80}],
    "max_stack": 5,
    "description": "Restaura 80 Mana",
    "usable_outside_combat": true,
    "price": 30,
    "tier": 2
  }
}
```

#### 4.2.3 Elixir of Iron (Attack Buff)
```json
{
  "elixir_of_iron": {
    "name": "Elixir of Iron",
    "category": "BUFF",
    "mana_cost": 0,
    "target_type": "SINGLE_ALLY",
    "effects": [{"effect_type": "BUFF", "base_power": 12, "stat": "PHYSICAL_ATTACK", "duration": 4}],
    "max_stack": 3,
    "description": "+12 Ataque Fisico por 4 turnos",
    "usable_outside_combat": false,
    "price": 35,
    "tier": 2
  }
}
```
**Balance note**: +12 ATK for 4 turns is ~8-10% damage boost for a tier 2 character. Valuable but not fight-warping.

#### 4.2.4 Arcane Incense (Magic Buff)
```json
{
  "arcane_incense": {
    "name": "Arcane Incense",
    "category": "BUFF",
    "mana_cost": 0,
    "target_type": "SINGLE_ALLY",
    "effects": [{"effect_type": "BUFF", "base_power": 12, "stat": "MAGICAL_ATTACK", "duration": 4}],
    "max_stack": 3,
    "description": "+12 Ataque Magico por 4 turnos",
    "usable_outside_combat": false,
    "price": 35,
    "tier": 2
  }
}
```

#### 4.2.5 Holy Water
```json
{
  "holy_water": {
    "name": "Holy Water",
    "category": "OFFENSIVE",
    "mana_cost": 0,
    "target_type": "SINGLE_ENEMY",
    "effects": [
      {"effect_type": "DAMAGE", "base_power": 60, "element": "HOLY"},
      {"effect_type": "CLEANSE_ALLY", "note": "removes 1 debuff from user"}
    ],
    "max_stack": 3,
    "description": "Dano HOLY a um inimigo + limpa 1 debuff de si mesmo",
    "usable_outside_combat": false,
    "price": 40,
    "tier": 2
  }
}
```
**Balance note**: 60 HOLY damage is devastating to undead (2x = 120). Priced high enough to not trivialize undead encounters.

#### 4.2.6 Elemental Bomb (Fire/Ice/Lightning variants)
```json
{
  "fire_bomb": {
    "name": "Fire Bomb",
    "category": "OFFENSIVE",
    "mana_cost": 0,
    "target_type": "ALL_ENEMIES",
    "effects": [
      {"effect_type": "DAMAGE", "base_power": 50, "element": "FIRE"},
      {"effect_type": "APPLY_AILMENT", "ailment_id": "burn", "base_power": 6, "duration": 2}
    ],
    "max_stack": 3,
    "description": "Dano FIRE a todos os inimigos + BURN 2 turnos",
    "usable_outside_combat": false,
    "price": 45,
    "tier": 2
  }
}
```
**Balance note**: Same template for `ice_bomb` (COLD ailment, FREEZE 20% chance) and `lightning_bomb` (PARALYSIS 1 turn, 30% chance). AoE 50 base + ailment. Expensive but fight-swinging.

---

### 4.3 Tier 3 Consumables (5 items)

#### 4.3.1 Large Health Potion
```json
{
  "health_potion_large": {
    "name": "Large Health Potion",
    "category": "HEALING",
    "mana_cost": 0,
    "target_type": "SELF",
    "effects": [{"effect_type": "HEAL_HP", "base_power": 250}],
    "max_stack": 3,
    "description": "Restaura 250 HP",
    "usable_outside_combat": true,
    "price": 60,
    "tier": 3
  }
}
```

#### 4.3.2 Large Mana Potion
```json
{
  "mana_potion_large": {
    "name": "Large Mana Potion",
    "category": "HEALING",
    "mana_cost": 0,
    "target_type": "SELF",
    "effects": [{"effect_type": "HEAL_MANA", "base_power": 150}],
    "max_stack": 3,
    "description": "Restaura 150 Mana",
    "usable_outside_combat": true,
    "price": 60,
    "tier": 3
  }
}
```

#### 4.3.3 Full Elixir
```json
{
  "full_elixir": {
    "name": "Full Elixir",
    "category": "HEALING",
    "mana_cost": 0,
    "target_type": "SELF",
    "effects": [
      {"effect_type": "HEAL_HP", "base_power": 200},
      {"effect_type": "HEAL_MANA", "base_power": 100},
      {"effect_type": "CLEANSE"}
    ],
    "max_stack": 2,
    "description": "Restaura 200 HP + 100 Mana + limpa todos os ailments",
    "usable_outside_combat": true,
    "price": 100,
    "tier": 3
  }
}
```
**Balance note**: The "panic button". Heals, restores mana, AND cleanses. Very expensive. Max stack 2 prevents hoarding.

#### 4.3.4 Revive Totem
```json
{
  "revive_totem": {
    "name": "Revive Totem",
    "category": "REVIVE",
    "mana_cost": 0,
    "target_type": "SINGLE_ALLY",
    "effects": [
      {"effect_type": "REVIVE", "base_power": 30, "note": "revive at 30% HP"}
    ],
    "max_stack": 1,
    "description": "Revive um aliado com 30% HP",
    "usable_outside_combat": false,
    "price": 120,
    "tier": 3
  }
}
```
**Balance note**: Single most expensive consumable. Max stack 1 is critical -- cannot stockpile revives. 30% HP means the revived character is still fragile.

#### 4.3.5 Teleport Scroll
```json
{
  "teleport_scroll": {
    "name": "Teleport Scroll",
    "category": "UTILITY",
    "mana_cost": 0,
    "target_type": "ALL_ALLIES",
    "effects": [
      {"effect_type": "FLEE", "note": "guaranteed escape, no HP cost"}
    ],
    "max_stack": 1,
    "description": "Fuga garantida de qualquer combate (exceto boss)",
    "usable_outside_combat": false,
    "price": 80,
    "tier": 3
  }
}
```
**Balance note**: Smoke bomb upgrade -- guaranteed escape vs smoke bomb's chance-based. Cannot be used in boss fights.

---

### 4.4 Utility Consumables (4 items, available across tiers)

#### 4.4.1 Speed Potion
```json
{
  "speed_potion": {
    "name": "Speed Potion",
    "category": "BUFF",
    "mana_cost": 0,
    "target_type": "SINGLE_ALLY",
    "effects": [{"effect_type": "BUFF", "base_power": 4, "stat": "SPEED", "duration": 4}],
    "max_stack": 3,
    "description": "+4 Speed por 4 turnos (age antes dos inimigos)",
    "usable_outside_combat": false,
    "price": 30,
    "tier": 2
  }
}
```

#### 4.4.2 Iron Potion (Defense Buff)
```json
{
  "iron_potion": {
    "name": "Iron Potion",
    "category": "BUFF",
    "mana_cost": 0,
    "target_type": "SINGLE_ALLY",
    "effects": [{"effect_type": "BUFF", "base_power": 15, "stat": "PHYSICAL_DEFENSE", "duration": 4}],
    "max_stack": 3,
    "description": "+15 Defesa Fisica por 4 turnos",
    "usable_outside_combat": false,
    "price": 30,
    "tier": 2
  }
}
```

#### 4.4.3 Barrier Potion (Magic Defense Buff)
```json
{
  "barrier_potion": {
    "name": "Barrier Potion",
    "category": "BUFF",
    "mana_cost": 0,
    "target_type": "SINGLE_ALLY",
    "effects": [{"effect_type": "BUFF", "base_power": 15, "stat": "MAGICAL_DEFENSE", "duration": 4}],
    "max_stack": 3,
    "description": "+15 Defesa Magica por 4 turnos",
    "usable_outside_combat": false,
    "price": 30,
    "tier": 2
  }
}
```

#### 4.4.4 Ancient Map
```json
{
  "ancient_map": {
    "name": "Ancient Map",
    "category": "UTILITY",
    "mana_cost": 0,
    "target_type": "ALL_ALLIES",
    "effects": [{"effect_type": "REVEAL_MAP", "note": "reveals all rooms on current floor"}],
    "max_stack": 1,
    "description": "Revela todas as salas do andar atual",
    "usable_outside_combat": false,
    "price": 45,
    "tier": 2
  }
}
```

---

### 4.5 Consumable Roster Summary

| Item | Tier | Category | Price | Key Effect |
|------|------|----------|-------|------------|
| Medium Health Potion | 2 | HEALING | 30g | Heal 120 HP |
| Medium Mana Potion | 2 | HEALING | 30g | Heal 80 Mana |
| Elixir of Iron | 2 | BUFF | 35g | +12 PHYS_ATK 4 turns |
| Arcane Incense | 2 | BUFF | 35g | +12 MAG_ATK 4 turns |
| Holy Water | 2 | OFFENSIVE | 40g | 60 HOLY dmg + cleanse |
| Fire Bomb | 2 | OFFENSIVE | 45g | AoE 50 FIRE + burn |
| Ice Bomb | 2 | OFFENSIVE | 45g | AoE 50 ICE + cold |
| Lightning Bomb | 2 | OFFENSIVE | 45g | AoE 50 LIGHTNING + paralyze chance |
| Speed Potion | 2 | BUFF | 30g | +4 SPEED 4 turns |
| Iron Potion | 2 | BUFF | 30g | +15 PHYS_DEF 4 turns |
| Barrier Potion | 2 | BUFF | 30g | +15 MAG_DEF 4 turns |
| Ancient Map | 2 | UTILITY | 45g | Reveal floor map |
| Large Health Potion | 3 | HEALING | 60g | Heal 250 HP |
| Large Mana Potion | 3 | HEALING | 60g | Heal 150 Mana |
| Full Elixir | 3 | HEALING | 100g | Heal 200 HP + 100 Mana + cleanse |
| Revive Totem | 3 | REVIVE | 120g | Revive ally at 30% HP |
| Teleport Scroll | 3 | UTILITY | 80g | Guaranteed flee |

**Total: 17 new consumables** (6 tier 2 core + 4 tier 2 utility + 2 tier 2 offensive variants + 5 tier 3)

---

## 5. Legendary Weapons and Armor

### 5.1 Design Philosophy

Legendary items are not just "bigger numbers". Each legendary has a **unique passive effect** that changes how the character plays. They are boss-tier drops only (never in shops), and their power should feel earned.

**Rarity difference:**
- Common: Raw stats only
- Uncommon: Stats + element
- Rare: Stats + element + CHA requirement
- Legendary: Stats + element + unique passive + CHA 22 requirement

---

### 5.2 Legendary Weapons (4 items)

#### 5.2.1 Dragon Fang Blade
```json
{
  "dragon_fang_blade": {
    "name": "Dragon Fang Blade",
    "weapon_type": "SWORD",
    "damage_kind": "SLASHING",
    "damage_type": "PHYSICAL",
    "weapon_die": 14,
    "attack_range": "MELEE",
    "category": "MARTIAL",
    "rarity": "LEGENDARY",
    "element": "FIRE",
    "cha_requirement": 22,
    "passive": "DRAGON_FURY",
    "passive_description": "Each consecutive hit on the same target deals +10% cumulative damage (max +40%). Resets when target changes."
  }
}
```
**Design intent**: Rewards focused single-target damage. The player must commit to one target to maximize DPS. Anti-synergy with AoE strategies -- creates a meaningful choice.

#### 5.2.2 Soulreaper Staff
```json
{
  "soulreaper_staff": {
    "name": "Soulreaper Staff",
    "weapon_type": "STAFF",
    "damage_kind": "BLUDGEONING",
    "damage_type": "MAGICAL",
    "weapon_die": 14,
    "attack_range": "RANGED",
    "category": "MAGICAL",
    "rarity": "LEGENDARY",
    "element": "DARKNESS",
    "cha_requirement": 22,
    "passive": "SOUL_HARVEST",
    "passive_description": "Killing an enemy restores 15% of the wielder's max mana. Each kill also grants +5 MAGICAL_ATTACK for the rest of combat (max +20)."
  }
}
```
**Design intent**: Snowball weapon. Gets stronger as enemies die. Incentivizes the mage to secure kills rather than just poke damage.

#### 5.2.3 Frostbite Longbow
```json
{
  "frostbite_longbow": {
    "name": "Frostbite Longbow",
    "weapon_type": "BOW",
    "damage_kind": "PIERCING",
    "damage_type": "PHYSICAL",
    "weapon_die": 12,
    "attack_range": "RANGED",
    "category": "MARTIAL",
    "rarity": "LEGENDARY",
    "element": "ICE",
    "cha_requirement": 22,
    "passive": "FROZEN_HEART",
    "passive_description": "Attacks apply 1 stack of COLD. At 3 stacks, target is FROZEN for 1 turn (stacks reset). Frozen targets take +50% damage from the next hit."
  }
}
```
**Design intent**: Control weapon disguised as DPS. The ranger becomes a crowd controller by stacking COLD on priority targets. Creates combo potential with other party members attacking frozen targets.

#### 5.2.4 Warden Blade
```json
{
  "warden_blade": {
    "name": "Warden Blade",
    "weapon_type": "SWORD",
    "damage_kind": "SLASHING",
    "damage_type": "PHYSICAL",
    "weapon_die": 14,
    "attack_range": "MELEE",
    "category": "MARTIAL",
    "rarity": "LEGENDARY",
    "element": null,
    "cha_requirement": 22,
    "passive": "ELEMENTAL_SHIFT",
    "passive_description": "Each attack randomly selects from FIRE/ICE/LIGHTNING/EARTH/HOLY. Hitting a weakness with this weapon deals +25% bonus damage."
  }
}
```
**Design intent**: High-variance weapon. Sometimes amazing, sometimes mediocre. The RNG creates memorable moments. Pairs well with the Warden of Adnos thematic.

---

### 5.3 Legendary Armor (2 items)

#### 5.3.1 Wyrm Scale Armor
```json
{
  "wyrm_scale_armor": {
    "name": "Wyrm Scale Armor",
    "weight": "HEAVY",
    "ca_bonus": 10,
    "hp_bonus": 50,
    "mana_bonus": 0,
    "physical_defense_bonus": 6,
    "magical_defense_bonus": 4,
    "rarity": "LEGENDARY",
    "cha_requirement": 22,
    "passive": "DRAGONHIDE",
    "passive_description": "Immune to FIRE element. When hit by FIRE, heal 10% of max HP instead. Reduces all other elemental damage by 15%."
  }
}
```
**Design intent**: Converts fire from threat to healing. Completely changes how the player handles fire-element encounters. Pairs naturally with the Dragon Fang Blade thematically.

#### 5.3.2 Aegis of Adnos
```json
{
  "aegis_of_adnos": {
    "name": "Aegis of Adnos",
    "weight": "HEAVY",
    "ca_bonus": 12,
    "hp_bonus": 60,
    "mana_bonus": 0,
    "physical_defense_bonus": 5,
    "magical_defense_bonus": 5,
    "rarity": "LEGENDARY",
    "cha_requirement": 22,
    "passive": "WARDEN_SHIELD",
    "passive_description": "At the start of each turn, gain a shield equal to 10% of max HP. Shield absorbs damage before HP. Unused shield does not stack."
  }
}
```
**Design intent**: Proactive defense. The shield refreshes each turn, making the wearer extremely durable in long fights. Does not help against burst -- balanced by design.

---

### 5.4 Legendary Accessories (2 items)

These complement the existing legendary accessories (Crown of the Undying, Eye of the Storm, Veil of the Pale Moon, Heart of the Mountain).

#### 5.4.1 Inferno Heart
```json
{
  "inferno_heart": {
    "name": "Inferno Heart",
    "accessory_type": "AMULET",
    "stat_bonuses": [
      {"stat": "PHYSICAL_ATTACK", "flat": 15},
      {"stat": "MAGICAL_ATTACK", "flat": 10}
    ],
    "rarity": "LEGENDARY",
    "cha_requirement": 22,
    "passive": "PYROMANIAC",
    "passive_description": "All attacks gain FIRE element. BURN ailments applied by this character last 1 additional turn and deal +30% tick damage."
  }
}
```

#### 5.4.2 Warden Signet
```json
{
  "warden_signet": {
    "name": "Warden Signet",
    "accessory_type": "RING",
    "stat_bonuses": [
      {"stat": "PHYSICAL_ATTACK", "flat": 10},
      {"stat": "MAGICAL_ATTACK", "flat": 10},
      {"stat": "MAX_HP", "flat": 15}
    ],
    "rarity": "LEGENDARY",
    "cha_requirement": 22,
    "passive": "ADAPTIVE_RESONANCE",
    "passive_description": "After being hit by an element, gain +25% resistance to that element for 3 turns (stacks up to 2 elements). Adapts to the fight."
  }
}
```

---

### 5.5 Legendary Items Summary

| Item | Type | Element | Passive | Source Boss |
|------|------|---------|---------|-------------|
| Dragon Fang Blade | SWORD | FIRE | Consecutive hit bonus (+10% stacking) | Inferno Wyrm |
| Soulreaper Staff | STAFF | DARKNESS | Kill = mana restore + ATK boost | Forgotten King |
| Frostbite Longbow | BOW | ICE | COLD stacking -> FREEZE combo | Frost Warden / Hydra |
| Warden Blade | SWORD | Random | Random element per hit | Warden of Adnos |
| Wyrm Scale Armor | HEAVY | FIRE (absorb) | Fire immunity + fire heal | Inferno Wyrm |
| Aegis of Adnos | HEAVY | None | Turn-start HP shield | Warden of Adnos |
| Inferno Heart | AMULET | FIRE | All attacks become FIRE + BURN boost | Inferno Wyrm |
| Warden Signet | RING | Adaptive | Resistance to recently-hit elements | Warden of Adnos |

---

## 6. Complex Events

### 6.1 Design Philosophy

Events should feel like mini-stories, not just "pick the biggest number". The best events:
1. Offer choices with unclear optimal outcomes
2. Scale consequences with the party's current state
3. Reference the world of Adnos for flavor
4. Include at least one "high risk / high reward" option

---

### 6.2 Event Roster

#### 6.2.1 The Wounded Knight

**Category**: Multi-step story event. Tests generosity vs pragmatism.

```json
{
  "wounded_knight": {
    "title": "O Cavaleiro Ferido",
    "description": "Um cavaleiro de Adnos jaz ferido no corredor, sua armadura rachada e sangue escorrendo de um corte profundo. Ele estende a mao pedindo ajuda.",
    "choices": [
      {
        "label": "Curar o cavaleiro (gasta 20% HP do healer)",
        "effects": [
          {"type": "HP_PERCENT", "value": -0.20, "target": "HEALER_OR_HIGHEST_WIS"},
          {"type": "ITEM", "item_id": "knight_blessing", "note": "+10% ATK party for 2 combats"}
        ],
        "result_text": "O cavaleiro agradece e abencoa o grupo com forca renovada!",
        "follow_up": {
          "description": "O cavaleiro revela que carregava um mapa do proximo andar.",
          "choices": [
            {"label": "Aceitar o mapa", "effects": [{"type": "REVEAL_MAP"}], "result_text": "Salas reveladas!"},
            {"label": "Pedir ouro em vez disso", "effects": [{"type": "GOLD", "value": 60}], "result_text": "Ele entrega uma bolsa de moedas."}
          ]
        }
      },
      {
        "label": "Saquear o cavaleiro (ele nao pode resistir)",
        "effects": [
          {"type": "GOLD", "value": 40},
          {"type": "ITEM_RANDOM_WEAPON", "rarity": "UNCOMMON"}
        ],
        "result_text": "Voce pega o que pode. O cavaleiro observa com olhos opacos."
      },
      {
        "label": "Seguir em frente",
        "effects": [],
        "result_text": "Voce deixa o cavaleiro para tras."
      }
    ]
  }
}
```
**Design note**: Healing the knight costs resources but gives a two-step reward. Looting is immediate gold + item. Walking away is safe but gains nothing. Multi-step reward teaches players that generosity can pay off.

---

#### 6.2.2 The Alchemist's Bargain

**Category**: Skill check event (INT). Risk/reward gambling.

```json
{
  "alchemists_bargain": {
    "title": "A Barganha do Alquimista",
    "description": "Um alquimista louco oferece uma pocao borbulhante. 'Beba e fique mais forte... ou nao. Eu perdi a receita original.'",
    "choices": [
      {
        "label": "Beber a pocao (check INT >= 12)",
        "effects_success": [
          {"type": "BUFF_PERMANENT", "stat": "MAGICAL_ATTACK", "value": 5, "target": "DRINKER"},
          {"type": "HP_PERCENT", "value": 0.10, "target": "DRINKER"}
        ],
        "effects_failure": [
          {"type": "APPLY_AILMENT", "ailment_id": "poison", "duration": 5, "target": "DRINKER"},
          {"type": "HP_PERCENT", "value": -0.15, "target": "DRINKER"}
        ],
        "success_text": "A pocao queima, mas voce sente seu poder magico crescer!",
        "failure_text": "ARGH! Veneno! O alquimista ri histerico.",
        "stat_check": {"attribute": "INTELLIGENCE", "threshold": 12}
      },
      {
        "label": "Comprar ingredientes (30g)",
        "effects": [
          {"type": "GOLD", "value": -30},
          {"type": "ITEM", "item_id": "random_consumable_t2"}
        ],
        "result_text": "Pelo menos os ingredientes parecem uteis."
      },
      {
        "label": "Derrubar a pocao",
        "effects": [],
        "result_text": "Voce 'acidentalmente' derruba o frasco. Melhor seguro que envenenado."
      }
    ]
  }
}
```
**Design note**: INT check creates class relevance in events. Mages/Sorcerers have a natural advantage. Permanent +5 MAGICAL_ATTACK is very strong -- justified by the risk of poison + HP loss.

---

#### 6.2.3 The Cursed Shrine

**Category**: Risk/reward with persistent run effect.

```json
{
  "cursed_shrine": {
    "title": "Santuario Amaldicoado",
    "description": "Um altar negro pulsa com energia sombria. Oferendas de ossos cercam uma gema roxa flutuante. Voce sente poder... e perigo.",
    "choices": [
      {
        "label": "Tocar a gema (arriscado)",
        "effects": [
          {"type": "BUFF_PERMANENT", "stat": "PHYSICAL_ATTACK", "value": 8, "target": "TOUCHER"},
          {"type": "BUFF_PERMANENT", "stat": "MAGICAL_ATTACK", "value": 8, "target": "TOUCHER"},
          {"type": "DEBUFF_PERMANENT", "stat": "MAX_HP", "value": -30, "target": "TOUCHER"},
          {"type": "DEBUFF_PERMANENT", "stat": "MAGICAL_DEFENSE", "value": -5, "target": "TOUCHER"}
        ],
        "result_text": "Poder sombrio flui por suas veias! Mas algo foi tirado em troca..."
      },
      {
        "label": "Oferecer 50g ao altar",
        "effects": [
          {"type": "GOLD", "value": -50},
          {"type": "HP_PERCENT", "value": 0.30, "target": "ALL"},
          {"type": "MANA_PERCENT", "value": 0.30, "target": "ALL"}
        ],
        "result_text": "O altar aceita a oferenda e banha o grupo em energia restauradora."
      },
      {
        "label": "Destruir o altar (check STR >= 14)",
        "effects_success": [
          {"type": "GOLD", "value": 80},
          {"type": "ITEM", "item_id": "dark_crystal", "note": "consumable: +20% DARKNESS damage 1 combat"}
        ],
        "effects_failure": [
          {"type": "HP_PERCENT", "value": -0.20, "target": "ALL"},
          {"type": "APPLY_AILMENT", "ailment_id": "curse", "duration": 3, "target": "STRONGEST"}
        ],
        "success_text": "O altar se despedaca! A gema cai no chao, inerte.",
        "failure_text": "O altar revida com uma onda de energia negra!",
        "stat_check": {"attribute": "STRENGTH", "threshold": 14}
      }
    ]
  }
}
```
**Design note**: The gem touch is a glass-cannon trade. +8/+8 ATK is huge, but -30 HP and -5 MAGICAL_DEF makes the character fragile. Best on a backline DPS who avoids hits.

---

#### 6.2.4 The Gambler's Den

**Category**: Pure gambling. Variable outcomes.

```json
{
  "gamblers_den": {
    "title": "Covil do Apostador",
    "description": "Um goblin com um baralho sujo sorri por tras de uma mesa improvisada. 'Aposta, aposta! Dobra ou nada!'",
    "choices": [
      {
        "label": "Apostar 40g (50% chance dobrar)",
        "effects_win": [{"type": "GOLD", "value": 80}],
        "effects_lose": [{"type": "GOLD", "value": -40}],
        "win_chance": 0.50,
        "win_text": "DOBROU! O goblin range os dentes.",
        "lose_text": "Nada! O goblin ri histerico enquanto guarda suas moedas."
      },
      {
        "label": "Apostar 80g (30% chance triplicar)",
        "effects_win": [{"type": "GOLD", "value": 240}],
        "effects_lose": [{"type": "GOLD", "value": -80}],
        "win_chance": 0.30,
        "win_text": "JACKPOT! O goblin esta em choque!",
        "lose_text": "O goblin faz uma dancinha vitoriosa com suas moedas."
      },
      {
        "label": "Virar a mesa e sair",
        "effects": [{"type": "GOLD", "value": 10}],
        "result_text": "Voce vira a mesa. Algumas moedas caem no chao. Melhor que nada."
      }
    ]
  }
}
```
**Design note**: Expected value of 40g bet: 0.5 * 80 + 0.5 * (-40) = +20g. EV of 80g bet: 0.3 * 240 + 0.7 * (-80) = +16g. The safe bet is slightly better EV, but the high-risk bet has a higher ceiling. The flip-the-table option is always +10g. Mathematically sound gambling.

---

#### 6.2.5 The Forgotten Library

**Category**: Wisdom-based knowledge event with lasting benefit.

```json
{
  "forgotten_library": {
    "title": "Biblioteca Esquecida",
    "description": "Prateleiras empoeiradas se estendem nas sombras. Tomos antigos irradiam um brilho suave. O conhecimento de Adnos esta aqui, mas o tempo e limitado.",
    "choices": [
      {
        "label": "Estudar tacticas de combate (check WIS >= 10)",
        "effects_success": [
          {"type": "BUFF_PERMANENT", "stat": "PHYSICAL_ATTACK", "value": 3, "target": "ALL"},
          {"type": "BUFF_PERMANENT", "stat": "MAGICAL_ATTACK", "value": 3, "target": "ALL"}
        ],
        "effects_failure": [
          {"type": "MANA_PERCENT", "value": -0.10, "target": "READER"}
        ],
        "success_text": "Insights taticos! Todo o grupo aprende novas tecnicas.",
        "failure_text": "Os textos sao incompreensiveis. O esforco mental drena mana.",
        "stat_check": {"attribute": "WISDOM", "threshold": 10}
      },
      {
        "label": "Procurar mapas do dungeon",
        "effects": [
          {"type": "REVEAL_MAP"},
          {"type": "GOLD", "value": 20}
        ],
        "result_text": "Voce encontra mapas detalhados e algumas moedas entre as paginas!"
      },
      {
        "label": "Pegar livros para vender",
        "effects": [{"type": "GOLD", "value": 50}],
        "result_text": "Os livros valem bastante para colecionadores."
      }
    ]
  }
}
```
**Design note**: +3/+3 ATK for the ENTIRE party is extremely valuable. WIS check is easier (threshold 10), but failure still costs something. Selling books is the safe gold option.

---

#### 6.2.6 The Blacksmith's Ghost

**Category**: Weapon upgrade event. Costs gold but permanently improves a weapon.

```json
{
  "blacksmith_ghost": {
    "title": "O Fantasma do Ferreiro",
    "description": "O espectro de um ferreiro flutua sobre uma bigorna eterea. 'Traga-me uma arma... e ouro. Eu a tornarei digna de um heroi.'",
    "choices": [
      {
        "label": "Forjar elemento aleatorio (40g)",
        "effects": [
          {"type": "GOLD", "value": -40},
          {"type": "WEAPON_UPGRADE", "upgrade": "random_element"}
        ],
        "result_text": "A arma brilha com poder elemental!"
      },
      {
        "label": "Forjar elemento escolhido (80g)",
        "effects": [
          {"type": "GOLD", "value": -80},
          {"type": "WEAPON_UPGRADE", "upgrade": "choose_element"}
        ],
        "result_text": "A arma resplandece com o elemento que voce escolheu!"
      },
      {
        "label": "Pedir que reforce a arma (60g, +2 weapon_die)",
        "effects": [
          {"type": "GOLD", "value": -60},
          {"type": "WEAPON_UPGRADE", "upgrade": "weapon_die_plus_2"}
        ],
        "result_text": "O fantasma bate a arma com precisao. Ela se sente mais pesada, mais mortal."
      }
    ]
  }
}
```
**Design note**: Weapon upgrades are permanent for the run. Random element at 40g is a gamble. Chosen element at 80g is expensive but guaranteed. +2 weapon_die is pure damage and always good. Prices aligned with economy doc.

---

#### 6.2.7 The Prisoner's Dilemma

**Category**: Moral choice with party-wide consequences.

```json
{
  "prisoners_dilemma": {
    "title": "O Dilema do Prisioneiro",
    "description": "Duas celas enfrentam o corredor. Na esquerda, um anao desesperado. Na direita, uma elfa silenciosa. Uma alavanca entre elas pode abrir apenas uma.",
    "choices": [
      {
        "label": "Libertar o anao (ele e um ferreiro)",
        "effects": [
          {"type": "BUFF_PERMANENT", "stat": "PHYSICAL_DEFENSE", "value": 5, "target": "ALL"},
          {"type": "ITEM", "item_id": "iron_potion"}
        ],
        "result_text": "O anao reforja as armaduras do grupo com gratidao! +5 DEF para todos."
      },
      {
        "label": "Libertar a elfa (ela e uma curandeira)",
        "effects": [
          {"type": "HP_PERCENT", "value": 0.40, "target": "ALL"},
          {"type": "MANA_PERCENT", "value": 0.25, "target": "ALL"},
          {"type": "CLEANSE_ALL"}
        ],
        "result_text": "A elfa cura todo o grupo e remove todos os ailments. Ela desaparece nas sombras."
      },
      {
        "label": "Destruir as duas celas (check STR >= 16)",
        "effects_success": [
          {"type": "BUFF_PERMANENT", "stat": "PHYSICAL_DEFENSE", "value": 5, "target": "ALL"},
          {"type": "HP_PERCENT", "value": 0.40, "target": "ALL"},
          {"type": "MANA_PERCENT", "value": 0.25, "target": "ALL"},
          {"type": "CLEANSE_ALL"}
        ],
        "effects_failure": [
          {"type": "HP_PERCENT", "value": -0.15, "target": "STRONGEST"}
        ],
        "success_text": "Com forca bruta, voce quebra ambas as celas! Os dois prisioneiros ajudam o grupo!",
        "failure_text": "A parede nao cede. Voce se machuca tentando.",
        "stat_check": {"attribute": "STRENGTH", "threshold": 16}
      }
    ]
  }
}
```
**Design note**: Dwarf = permanent defense. Elf = healing (temporary but large). STR check to free both is very rewarding but high threshold (16). Contextual choice: low HP party wants the elf, healthy party wants permanent defense.

---

#### 6.2.8 The Elemental Rift

**Category**: Elemental puzzle event. Tests the player's understanding of the element system.

```json
{
  "elemental_rift": {
    "title": "Fenda Elemental",
    "description": "Uma fissura no espaco pulsa com energias elementais. Quatro cristais -- vermelho, azul, amarelo e verde -- flutuam ao redor. Voce pode tocar um.",
    "choices": [
      {
        "label": "Cristal vermelho (FOGO)",
        "effects": [
          {"type": "BUFF_COMBAT", "stat": "FIRE_DAMAGE", "value": 25, "duration_combats": 3},
          {"type": "DEBUFF_COMBAT", "stat": "ICE_RESISTANCE", "value": -25, "duration_combats": 3}
        ],
        "result_text": "Poder de fogo! Mas voce sente fraqueza ao gelo..."
      },
      {
        "label": "Cristal azul (GELO)",
        "effects": [
          {"type": "BUFF_COMBAT", "stat": "ICE_DAMAGE", "value": 25, "duration_combats": 3},
          {"type": "DEBUFF_COMBAT", "stat": "FIRE_RESISTANCE", "value": -25, "duration_combats": 3}
        ],
        "result_text": "Poder de gelo! Mas voce sente fraqueza ao fogo..."
      },
      {
        "label": "Cristal amarelo (RAIO)",
        "effects": [
          {"type": "BUFF_COMBAT", "stat": "LIGHTNING_DAMAGE", "value": 25, "duration_combats": 3},
          {"type": "DEBUFF_COMBAT", "stat": "WATER_RESISTANCE", "value": -25, "duration_combats": 3}
        ],
        "result_text": "Poder de raio! Mas voce sente fraqueza a agua..."
      },
      {
        "label": "Cristal verde (TERRA)",
        "effects": [
          {"type": "BUFF_COMBAT", "stat": "EARTH_DAMAGE", "value": 25, "duration_combats": 3},
          {"type": "DEBUFF_COMBAT", "stat": "LIGHTNING_RESISTANCE", "value": -25, "duration_combats": 3}
        ],
        "result_text": "Poder de terra! Mas voce sente fraqueza a raios..."
      }
    ]
  }
}
```
**Design note**: Each crystal gives +25% elemental damage but -25% resistance to its counter-element. The player must know what enemies are coming next. If the next room has fire enemies, picking the fire crystal is bad. Rewards scouting (Ancient Map synergy).

---

#### 6.2.9 The Sacrifice Altar

**Category**: High-risk event with party-modifying consequences.

```json
{
  "sacrifice_altar": {
    "title": "Altar do Sacrificio",
    "description": "Um altar de pedra negra sussurra promessas de poder. A inscricao diz: 'Ofereca o que e precioso. Receba o que e necessario.'",
    "choices": [
      {
        "label": "Sacrificar 30% HP do personagem mais forte",
        "effects": [
          {"type": "HP_PERCENT", "value": -0.30, "target": "STRONGEST"},
          {"type": "BUFF_PERMANENT", "stat": "PHYSICAL_ATTACK", "value": 10, "target": "WEAKEST"},
          {"type": "BUFF_PERMANENT", "stat": "MAGICAL_ATTACK", "value": 10, "target": "WEAKEST"}
        ],
        "result_text": "A forca do mais forte flui para o mais fraco! O equilibrio e restaurado."
      },
      {
        "label": "Sacrificar 100g",
        "effects": [
          {"type": "GOLD", "value": -100},
          {"type": "ITEM", "item_id": "random_rare_accessory"}
        ],
        "result_text": "O altar consome o ouro e materializa um artefato!"
      },
      {
        "label": "Sacrificar seu equipamento (remove arma do lider)",
        "effects": [
          {"type": "REMOVE_WEAPON", "target": "LEADER"},
          {"type": "BUFF_PERMANENT", "stat": "MAX_HP", "value": 50, "target": "ALL"},
          {"type": "BUFF_PERMANENT", "stat": "PHYSICAL_DEFENSE", "value": 5, "target": "ALL"}
        ],
        "result_text": "A arma e consumida. Em troca, uma aura protetora envolve todo o grupo."
      }
    ]
  }
}
```
**Design note**: Every option costs something valuable. HP sacrifice redistributes power. Gold sacrifice is a gamble on a rare item. Weapon sacrifice is devastating short-term but gives permanent party-wide buffs.

---

#### 6.2.10 The Mirror of Reflections

**Category**: Class-specific event. Outcome depends on party composition.

```json
{
  "mirror_of_reflections": {
    "title": "O Espelho das Reflexoes",
    "description": "Um espelho enorme mostra cada membro do grupo, mas distorcido -- versoes mais fortes, mais perigosas. O espelho pulsa, esperando.",
    "choices": [
      {
        "label": "Enfrentar o reflexo (mini-combate contra shadow clone)",
        "effects_win": [
          {"type": "BUFF_PERMANENT", "stat": "PHYSICAL_ATTACK", "value": 5, "target": "FIGHTER"},
          {"type": "BUFF_PERMANENT", "stat": "MAGICAL_ATTACK", "value": 5, "target": "FIGHTER"},
          {"type": "BUFF_PERMANENT", "stat": "MAX_HP", "value": 20, "target": "FIGHTER"}
        ],
        "effects_lose": [
          {"type": "HP_PERCENT", "value": -0.25, "target": "ALL"}
        ],
        "win_text": "Voce venceu seu reflexo! Absorveu sua forca!",
        "lose_text": "O reflexo era mais forte. O grupo foge, ferido.",
        "special": "triggers_mirror_combat"
      },
      {
        "label": "Quebrar o espelho (check CHA >= 12)",
        "effects_success": [
          {"type": "GOLD", "value": 60},
          {"type": "ITEM", "item_id": "mirror_shard", "note": "accessory: reflects 5% damage back"}
        ],
        "effects_failure": [
          {"type": "HP_PERCENT", "value": -0.10, "target": "ALL"},
          {"type": "APPLY_AILMENT", "ailment_id": "confusion", "duration": 2, "target": "ALL"}
        ],
        "success_text": "O espelho se despedaca em fragmentos uteis!",
        "failure_text": "Os estilhacos ricocheteiam! Reflexos distorcidos confundem o grupo.",
        "stat_check": {"attribute": "CHARISMA", "threshold": 12}
      },
      {
        "label": "Ignorar o espelho",
        "effects": [],
        "result_text": "Voce da as costas ao espelho. Ele escurece atras de voce."
      }
    ]
  }
}
```
**Design note**: The mirror combat is a special encounter against a shadow version of the party's strongest character. Winning gives permanent buffs. Losing costs HP. This is the most mechanically complex event -- implement last.

---

### 6.3 Event Summary

| Event | Type | Risk Level | Key Mechanic |
|-------|------|------------|--------------|
| Wounded Knight | Multi-step | Low | Generosity reward chain |
| Alchemist's Bargain | Skill check (INT) | Medium | Permanent buff or poison |
| Cursed Shrine | Risk/reward | High | Glass cannon trade |
| Gambler's Den | Gambling | Variable | Expected value calculation |
| Forgotten Library | Skill check (WIS) | Low-Medium | Party-wide ATK boost |
| Blacksmith's Ghost | Gold sink | Low | Weapon upgrade |
| Prisoner's Dilemma | Moral choice | Low-Medium | Contextual benefit |
| Elemental Rift | Elemental knowledge | Medium | Element buff/vulnerability |
| Sacrifice Altar | High-risk trade | High | Permanent party modification |
| Mirror of Reflections | Mini-combat / CHA check | High | Shadow clone fight |

**Stat check distribution:**
- STR: Cursed Shrine (14), Prisoner's Dilemma (16)
- INT: Alchemist's Bargain (12)
- WIS: Forgotten Library (10)
- CHA: Mirror of Reflections (12)
- DEX: (none -- future expansion)
- CON: (none -- future expansion)

This ensures varied classes have moments to shine in events.

---

## 7. Balance Framework

### 7.1 Enemy Damage Budget

Target: combat lasts 3-8 rounds. Player party has 4 characters with ~200-500 HP each at level ranges.

**Per-round enemy damage budget (total from all enemies):**
- Tier 1 encounter (3 enemies): ~60-100 total damage per round -> ~15-25 per character
- Tier 2 encounter (3-4 enemies): ~120-200 total damage per round -> ~30-50 per character
- Tier 3 encounter (3-4 enemies): ~200-350 total damage per round -> ~50-90 per character

**Boss damage budget (boss alone):**
- Tier 1 boss: ~40-80 damage per round (spread across party or focused)
- Tier 2 boss: ~80-140 damage per round
- Tier 3 boss: ~140-250 damage per round

### 7.2 Potion Economy

**Potions consumed per floor (estimated):**
- Floor 1-3: 2-4 small health potions, 1-2 small mana potions
- Floor 4-6: 2-3 medium health potions, 1-2 medium mana potions, 1 utility
- Floor 7-9: 1-2 large health potions, 1 large mana, 1-2 utility, maybe 1 elixir

**Gold spent on consumables per floor:**
- Floor 1-3: ~30-60g
- Floor 4-6: ~60-120g
- Floor 7-9: ~100-200g

This fits within the economy curve from ECONOMY.md.

### 7.3 Legendary Drop Rate

Legendary items should appear once every 2-3 full runs on average. Per boss kill:
- Tier 1 boss: 0% legendary drop chance
- Tier 2 boss: 5% legendary drop chance
- Tier 3 boss: 15-20% legendary drop chance

A full run has 3 bosses (one per tier bracket), so per run: 0% + 5% + ~17.5% = ~22% chance of at least 1 legendary per run. This means roughly 1 in 4-5 runs drops a legendary -- rare enough to feel special, common enough to not feel impossible.

### 7.4 Event Frequency

- 1-2 events per floor
- 3-6 events per full run
- Pool of 14 events (4 existing + 10 new) means ~3-4 runs before seeing all events
- Skill check events should appear at least once per run to make stats feel relevant

---

## 8. Drop and Spawn Distribution

### 8.1 Enemy Spawn Rules

**Floor 1-3 (Tier 1 pool):**
- Original: goblin, mushroom, rat_swarm, skeleton, slime (5)
- New: kobold_trapper, cave_bat, vine_creeper, fire_imp, armored_beetle (5)
- Total: 10 enemies. Encounters draw 3-4 from this pool.

**Floor 4-6 (Tier 2 pool):**
- New: orc_warrior, wraith, harpy, goblin_shaman, dark_mage, stone_guardian, plague_rat, shadow_assassin (8)
- Total: 8 enemies. May include 1 tier 1 enemy as "easy" filler.

**Floor 7-9 (Tier 3 pool):**
- New: mimic, basilisk, vampire, lich_acolyte, elemental_shifter, demon_knight, mind_flayer (7)
- Total: 7 enemies. May include 1 tier 2 enemy.

### 8.2 Boss Assignment

Each floor bracket randomly selects 1 boss from its pool:
- Tier 1 pool: Goblin King, Broodmother, Frost Warden, Bandit Warlord (4 options)
- Tier 2 pool: Ancient Golem, Hydra, Shadow Matriarch, War Golem Mk-II (4 options)
- Tier 3 pool: Lich Lord, Inferno Wyrm, Forgotten King, Warden of Adnos (4 options)

### 8.3 Updated Drop Tables

**Tier 2 drops (for tier 2 enemies and bosses):**
```
Pool additions: medium health/mana potions, elemental bombs, buff potions,
               tier 2 weapons (flame_sword, frost_staff, thunder_bow, holy_mace),
               tier 2 armor (chain_mail, plate_armor, mage_robes),
               uncommon accessories
```

**Tier 3 drops (for tier 3 enemies and bosses):**
```
Pool additions: large health/mana potions, full elixir, revive totem,
               rare weapons, rare armor, rare accessories,
               legendary items (boss-only, low weight)
```

### 8.4 Shop Inventory by Floor

**Floor 1-3 shop**: Existing tier 1 items + antidote + smoke bomb
**Floor 4-6 shop**: Tier 2 potions, buff potions, elemental bombs, holy water, ancient map
**Floor 7-9 shop**: Tier 3 potions, full elixir, teleport scroll, revive totem (if affordable)

---

## 9. Implementation Priority

### Phase 1 -- Core Enemies (HIGH PRIORITY)

**Goal**: Populate all 3 tiers with enough enemies for varied encounters.

1. **Create tier 2 and tier 3 enemy directories**
   - `data/dungeon/enemies/tier2/` (8 JSON files)
   - `data/dungeon/enemies/tier3/` (7 JSON files)

2. **Create tier 2 and tier 3 skill files**
   - `data/dungeon/enemies/skills/tier2_skills.json`
   - `data/dungeon/enemies/skills/tier3_skills.json`

3. **Create 5 new tier 1 enemy JSONs** in `data/dungeon/enemies/tier1/`

4. **Expand elemental_profiles.json** with profiles for all new enemies

5. **Expand weapons.json** (enemy weapons) with new natural weapons

6. **Update enemy_template_loader.py** to scan tier2/ and tier3/ directories

7. **Update encounter templates.json** with tier 2 and tier 3 compositions

**Estimated effort**: 2-3 sessions

### Phase 2 -- Bosses (HIGH PRIORITY)

1. **Create 9 new boss JSON files** in `data/dungeon/enemies/bosses/`
2. **Create boss skill entries** in `boss_skills.json`
3. **Register new bosses** in `boss_loader.py` (_BOSS_IDS tuple)
4. **Implement phase handlers** for each new boss
5. **Create boss-specific loot tables** in `drop_tables.json`

**Estimated effort**: 3-4 sessions (phase handlers are the bulk)

### Phase 3 -- Consumables (MEDIUM PRIORITY)

1. **Add 17 new entries** to `data/consumables/consumables.json`
2. **Update shop_inventory.json** with tier 2 and tier 3 shop pages
3. **Implement REVIVE effect type** if not already supported
4. **Implement REVEAL_MAP effect type** for Ancient Map
5. **Update drop_tables.json** with tier 2 and tier 3 consumable drops

**Estimated effort**: 1-2 sessions

### Phase 4 -- Events (MEDIUM PRIORITY)

1. **Add 10 new events** to `data/dungeon/events/random_events.json`
2. **Implement stat check system** (attribute >= threshold -> success/failure branch)
3. **Implement multi-step events** (follow_up field in event data)
4. **Implement weapon upgrade effects**
5. **Implement permanent buff/debuff effects** (persist across rooms)

**Estimated effort**: 2-3 sessions

### Phase 5 -- Legendary Items (LOW PRIORITY -- depends on passive system)

1. **Add 4 legendary weapons** to `data/weapons/weapons.json`
2. **Add 2 legendary armors** to `data/armors/armors.json`
3. **Add 2 legendary accessories** to `data/accessories/accessories.json`
4. **Implement passive effect system** (new module: `src/core/items/passives/`)
5. **Wire passives into combat engine** (on_hit, on_kill, on_turn_start hooks)

**Estimated effort**: 3-4 sessions (passive system is the main engineering work)

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-29 | Initial design document. 20 enemies, 9 bosses, 17 consumables, 8 legendaries, 10 events. |
