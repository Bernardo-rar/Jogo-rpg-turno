# System 2: Subclasses (26 Total -- 2 per Class)

## Design Document

### Design Pillars
1. **Build Identity** -- Subclass choice at level 3 is the single most impactful decision in a run. It defines the character's role for the rest of the run.
2. **No Wrong Choice** -- Both subclasses must be viable. One is not "the good one."
3. **Modify, Don't Replace** -- Subclasses enhance existing class mechanics, they do not replace them.
4. **Visible Impact** -- The player must feel the subclass immediately after choosing. At least one new active skill is usable right away.

### Subclass Unlock Flow

1. Party reaches level 3.
2. After attribute distribution (none at level 3), each character in the party gets a subclass choice screen.
3. Player sees both subclass options with: name, description, skills preview, passive bonus.
4. Player picks one. Irreversible for this run.
5. The character gains: 2-3 new skills added to their available pool, 1 passive bonus applied immediately, and potentially a modification to an existing class mechanic.
6. At levels 5, 7, and 9, the subclass grants additional bonuses (described per subclass).

### Subclass Progression Table

| Level | Subclass Reward |
|-------|----------------|
| 3     | Choose subclass: 2-3 skills + 1 passive |
| 5     | Subclass skill upgrade OR new skill |
| 7     | Subclass passive upgrade |
| 9     | Subclass capstone: powerful unique ability |

---

## All 26 Subclasses

---

### 1. Fighter

#### Champion
**Theme:** Raw martial superiority -- crits harder, hits harder, never stops swinging.

**Level 3 Skills:**
- **Improved Critical** (PASSIVE): Crit chance +15%. Crit damage multiplier 2.5x instead of 2.0x.
- **Mighty Blow** (ACTION, slot_cost 5): Single target physical damage (base_power 55). If it crits, the target loses their next bonus action.
- **Champion's Resolve** (BONUS_ACTION, slot_cost 3): Self-buff: +20% physical attack for 2 turns. Costs 2 AP.

**Level 3 Passive:** +10% physical attack modifier permanently.

**Level 5:** Improved Critical upgrades to +20% crit chance, 2.75x crit multiplier.
**Level 7:** Mighty Blow base_power increases to 70 and has no cooldown.
**Level 9 Capstone:** **Undying Champion** -- Once per combat, when reduced to 0 HP, revive with 30% HP and gain +50% physical attack for 2 turns.

**Mechanic Modification:** Offensive Stance now also grants +10% crit chance (stacks with Improved Critical).

---

#### Battlemaster
**Theme:** Tactical commander -- controls the battlefield with maneuvers that buff allies and debuff enemies.

**Level 3 Skills:**
- **Commanding Strike** (ACTION, slot_cost 4): Single target damage (base_power 35). Target ally gets +15 physical attack for 1 turn. Costs 2 AP.
- **Riposte** (REACTION, slot_cost 4): On being hit, counter-attack for (base_power 30) and reduce attacker's physical attack by 10 for 1 turn. Costs 1 AP. Replaces base Parry if desired.
- **Rally** (BONUS_ACTION, slot_cost 3): All allies gain +10 physical defense for 2 turns. Costs 1 AP.

**Level 3 Passive:** +1 AP generated per basic attack (normally generates 1, now generates 2). +10% physical defense.

**Level 5:** Rally also grants +5 Speed for 2 turns.
**Level 7:** Commanding Strike can target 2 enemies simultaneously (multi-target upgrade).
**Level 9 Capstone:** **Grand Stratagem** -- Once per combat, all allies gain an extra Action this turn.

**Mechanic Modification:** Normal Stance now generates +1 AP per turn passively.

---

### 2. Barbarian

#### Berserker
**Theme:** Uncontrollable rage -- more damage the more fury accumulated, risks self-destruction.

**Level 3 Skills:**
- **Frenzy Strike** (ACTION, slot_cost 5): Single target (base_power 60). Deals 10% of own max HP as self-damage. Generates 25 fury.
- **Bloodlust** (PASSIVE): When below 30% HP, all attacks deal +30% damage.
- **Rampage** (BONUS_ACTION, slot_cost 3): Consumes 40 fury. Next 2 basic attacks this combat deal +50% damage.

**Level 3 Passive:** Fury cap increased from 100 to 130. Fury decay per turn reduced from 10 to 5. +15% crit damage.

**Level 5:** Frenzy Strike self-damage reduced to 5% max HP, base_power increased to 75.
**Level 7:** Bloodlust threshold increased to 50% HP (activates earlier).
**Level 9 Capstone:** **Deathless Rage** -- While above 80 fury, cannot be reduced below 1 HP. Lasts until fury drops below 40.

**Mechanic Modification:** Fury bar gains passively at rate of 5/turn (normally only gains from taking/dealing damage).

---

#### Totem Warrior
**Theme:** Spiritual connection to nature -- becomes an unmovable wall that protects allies.

**Level 3 Skills:**
- **Bear Totem** (BONUS_ACTION, slot_cost 4): Self and adjacent allies gain damage reduction 15% for 3 turns. Costs 20 fury.
- **Spirit Link** (REACTION, slot_cost 3): When an ally takes fatal damage, redirect 50% of the damage to self. Costs 30 fury.
- **Totemic Roar** (ACTION, slot_cost 4): AoE damage (base_power 20) to all enemies. All enemies get -10 physical attack for 2 turns.

**Level 3 Passive:** +15% max HP. +5 to all defenses.

**Level 5:** Bear Totem damage reduction increases to 20%.
**Level 7:** Spirit Link no longer costs fury (free reaction).
**Level 9 Capstone:** **Ancestral Guardian** -- Summon a spirit totem that absorbs the first 30% of all party damage each turn for 3 turns. Costs 60 fury.

**Mechanic Modification:** Fury bar now generates from taking damage at 1.5x rate (normally 1x).

---

### 3. Mage

#### Evoker
**Theme:** AoE destruction specialist -- bigger explosions, more elemental variety.

**Level 3 Skills:**
- **Meteor Shard** (ACTION, slot_cost 6): All enemies (base_power 40, element FIRE). Has 20% chance to apply Scorch.
- **Frost Nova** (ACTION, slot_cost 5): All enemies (base_power 25, element ICE). Applies Cold (-5 Speed) for 2 turns.
- **Elemental Mastery** (PASSIVE): All elemental damage +15%.

**Level 3 Passive:** AoE skills cost 15% less mana. +15% magical attack.

**Level 5:** Elemental Mastery increases to +25%. Weakness exploitation deals +20% bonus (instead of default).
**Level 7:** Meteor Shard upgrades: base_power 55, Scorch chance 40%.
**Level 9 Capstone:** **Cataclysm** -- All enemies (base_power 80, random element among FIRE/ICE/LIGHTNING). Costs 40 mana. 8-turn cooldown.

**Mechanic Modification:** Overcharge mode now also causes AoE spells to hit for +10% damage (on top of existing Overcharge bonus).

---

#### Chronomancer
**Theme:** Time manipulation -- haste for allies, slow for enemies, turn order control.

**Level 3 Skills:**
- **Haste** (ACTION, slot_cost 5): Single ally gains +10 Speed and +1 bonus action for 2 turns. 15 mana.
- **Slow** (ACTION, slot_cost 4): Single enemy loses 50% Speed for 2 turns. 12 mana.
- **Time Warp** (BONUS_ACTION, slot_cost 3): Self: next spell cast this turn costs 0 mana. 3-turn cooldown.

**Level 3 Passive:** +5 Speed for self. All buff durations on allies extended by +1 turn.

**Level 5:** Haste can target 2 allies. Slow can target 2 enemies.
**Level 7:** All debuff durations on enemies extended by +1 turn.
**Level 9 Capstone:** **Temporal Collapse** -- All enemies skip their next turn entirely. 25 mana. Once per combat.

**Mechanic Modification:** Overcharge mode reduces all cooldowns by 1 turn while active.

---

### 4. Cleric

#### Life Domain
**Theme:** Unmatched healing -- keeps the party alive through anything.

**Level 3 Skills:**
- **Mass Heal** (ACTION, slot_cost 6): All allies heal (base_power 30). Generates 2 Holy Power. 25 mana.
- **Revitalize** (BONUS_ACTION, slot_cost 3): Single ally: remove 1 debuff and heal (base_power 15). 10 mana.
- **Blessed Aura** (PASSIVE): Party members within same position (front/back) regen +5 HP per turn.

**Level 3 Passive:** All healing done +20%.

**Level 5:** Mass Heal also cleanses 1 ailment from each target.
**Level 7:** Blessed Aura HP regen increases to +10 per turn and now works regardless of position.
**Level 9 Capstone:** **Miracle** -- Fully heal all party members and remove all debuffs/ailments. 40 mana. Once per combat.

**Mechanic Modification:** Channel Divinity now also heals all allies for 15% of their max HP.

---

#### War Domain
**Theme:** Holy warrior -- offensive cleric that smites enemies while providing moderate support.

**Level 3 Skills:**
- **Holy Smite** (ACTION, slot_cost 5): Single enemy (base_power 45, element HOLY). If target is debuffed, deal +25% damage. Costs 2 Holy Power + 10 mana.
- **Battle Prayer** (BONUS_ACTION, slot_cost 3): All allies gain +10 physical attack for 2 turns. Generates 1 Holy Power.
- **Retribution** (PASSIVE): When an ally takes damage, the attacker takes 10% of the damage as HOLY.

**Level 3 Passive:** +15% magical attack. Physical attacks also gain +5 HOLY damage.

**Level 5:** Holy Smite bonus against debuffed targets increases to +40%.
**Level 7:** Retribution damage increases to 15% and applies to magic damage too.
**Level 9 Capstone:** **Wrath of the Divine** -- All enemies (base_power 70, element HOLY). Applies Weakness (-15% defense) for 3 turns. 30 mana. Once per combat.

**Mechanic Modification:** Divine Smite (base class skill) costs 1 less Holy Power.

---

### 5. Paladin

#### Devotion
**Theme:** Impenetrable guardian -- aura-powered tank that shields the party.

**Level 3 Skills:**
- **Holy Shield** (REACTION, slot_cost 4): Grant an ally a shield equal to 30% of Paladin's max HP. Costs 2 Divine Favor.
- **Cleansing Touch** (BONUS_ACTION, slot_cost 3): Remove 2 debuffs/ailments from target ally. Costs 1 Divine Favor.
- **Protective Aura** (PASSIVE): While Defensive Aura is active, all allies take 10% less damage.

**Level 3 Passive:** +10% max HP. Defensive Aura potency +15%.

**Level 5:** Holy Shield now also grants +15 physical defense for 2 turns.
**Level 7:** Protective Aura damage reduction increases to 15%.
**Level 9 Capstone:** **Invincible Vow** -- All allies become immune to damage for 1 turn. 6 Divine Favor. Once per combat.

**Mechanic Modification:** Aura switching no longer costs a bonus action (can be done as a free action).

---

#### Vengeance
**Theme:** Relentless pursuer -- marks enemies for death and executes them with empowered smites.

**Level 3 Skills:**
- **Vow of Enmity** (BONUS_ACTION, slot_cost 3): Mark a single enemy: all attacks against that enemy deal +20% damage (party-wide). Lasts 3 turns. Costs 2 Divine Favor.
- **Avenging Strike** (ACTION, slot_cost 5): Single enemy (base_power 50, element HOLY). If target is marked by Vow of Enmity, guaranteed crit. Costs 2 Divine Favor + 10 mana.
- **Relentless Advance** (PASSIVE): After killing an enemy, gain +1 action point resource (Divine Favor).

**Level 3 Passive:** +15% physical attack. Offensive Aura potency +15%.

**Level 5:** Vow of Enmity damage bonus increases to +30%.
**Level 7:** Avenging Strike gains lifesteal: heal for 25% of damage dealt.
**Level 9 Capstone:** **Oath of Vengeance** -- Triple damage on next attack. If it kills the target, reset all cooldowns. 4 Divine Favor. Once per combat.

**Mechanic Modification:** Glimpse of Glory (base skill) now also debuffs all enemies with -10% defense for 2 turns.

---

### 6. Rogue

#### Assassin
**Theme:** Alpha strike burst -- massive damage from stealth, resets on kills.

**Level 3 Skills:**
- **Assassinate** (ACTION, slot_cost 6): Single enemy (base_power 70). Must be in stealth. Guaranteed crit. Breaks stealth. 15 mana.
- **Shadow Step** (BONUS_ACTION, slot_cost 2): Teleport to back line and enter stealth. 8 mana. 2-turn cooldown.
- **Death Mark** (PASSIVE): Enemies below 25% HP take +30% damage from Rogue.

**Level 3 Passive:** Stealth damage bonus increased from base to +50% (normally +25%).

**Level 5:** Assassinate refunds 50% mana if it kills the target.
**Level 7:** Death Mark threshold increases to 35% HP.
**Level 9 Capstone:** **Perfect Kill** -- If Assassinate kills the target, immediately re-enter stealth and gain a free action. Once per combat.

**Mechanic Modification:** Stealth now lasts 2 turns instead of 1 (but still breaks on attacking).

---

#### Thief
**Theme:** Item specialist and speed demon -- uses items without turns, steals from enemies.

**Level 3 Skills:**
- **Quick Hands** (PASSIVE): Using a consumable item does not cost an action (1/turn).
- **Pilfer** (BONUS_ACTION, slot_cost 3): Steal a random buff from an enemy. If no buffs, steal 15 gold instead. 8 mana.
- **Smoke Bomb** (BONUS_ACTION, slot_cost 3): All party members gain +20 physical defense for 1 turn. Enter stealth. 10 mana. 3-turn cooldown.

**Level 3 Passive:** +10% item effectiveness. +5 Speed.

**Level 5:** Quick Hands can be used 2x per turn.
**Level 7:** Pilfer also applies a random debuff to the target (-10 to a random stat for 2 turns).
**Level 9 Capstone:** **Master Thief** -- At the start of combat, steal 1 item from each enemy (consumable or gold). Passive, automatic.

**Mechanic Modification:** Envenom (base skill) now lasts 3 attacks instead of 1.

---

### 7. Ranger

#### Hunter
**Theme:** Single-target annihilator -- stacks focus for devastating finishing blows.

**Level 3 Skills:**
- **Colossus Slayer** (PASSIVE): Attacks against enemies above 50% HP deal +20% damage. Attacks against enemies below 50% HP deal +10% damage and generate +1 Predatory Focus.
- **Precise Shot** (ACTION, slot_cost 5): Single enemy (base_power 50). Ignores 30% of target's defense. Costs 3 Predatory Focus + 12 mana.
- **Kill Command** (BONUS_ACTION, slot_cost 3): Mark a target: next attack against it deals +40% damage. Costs 2 Predatory Focus.

**Level 3 Passive:** +15% physical attack against single targets.

**Level 5:** Precise Shot ignores 50% of defense.
**Level 7:** Kill Command also makes the next attack guaranteed crit.
**Level 9 Capstone:** **Perfect Shot** -- Single enemy (base_power 100). Ignores all defense. Costs 7 Predatory Focus. 6-turn cooldown.

**Mechanic Modification:** Predatory Focus cap increases from 8 to 12.

---

#### Beastmaster
**Theme:** Companion fighter -- summons a beast that acts independently.

**Level 3 Skills:**
- **Summon Companion** (BONUS_ACTION, slot_cost 4): Summon a wolf companion to the front line. Wolf has HP = 40% of Ranger's max HP, attacks for (base_power 20). Persists until killed. 20 mana. Once per combat.
- **Pack Tactics** (PASSIVE): While companion is alive, both Ranger and companion deal +15% damage.
- **Command: Pounce** (BONUS_ACTION, slot_cost 2): Companion attacks a target and applies -10 Speed for 1 turn. Costs 1 Predatory Focus.

**Level 3 Passive:** Companion generates 1 Predatory Focus per attack. +10% physical attack.

**Level 5:** Companion HP increases to 50% of Ranger's max HP. Companion damage base_power increases to 30.
**Level 7:** Pack Tactics bonus increases to +25%.
**Level 9 Capstone:** **Alpha Predator** -- Ranger and companion attack the same target simultaneously for combined (base_power 90). If target dies, companion fully heals. 5 Predatory Focus. 5-turn cooldown.

**Mechanic Modification:** Hunter's Mark also affects the companion's attacks.

---

### 8. Bard

#### College of Valor
**Theme:** Battle bard -- buffs through combat participation, groove stacks from attacking.

**Level 3 Skills:**
- **Battle Hymn** (ACTION, slot_cost 5): All allies (base_power 10 PSYCHIC damage to all enemies) + all allies gain +12 physical attack for 2 turns. Generates 2 groove. 15 mana.
- **War Drums** (BONUS_ACTION, slot_cost 3): All allies gain +8 Speed for 2 turns. Generates 1 groove.
- **Heroic Inspiration** (PASSIVE): When an ally crits, Bard gains 1 groove.

**Level 3 Passive:** Groove cap increased from 10 to 15. Groove generated per action +1. +10% party physical attack while groove >= 5.

**Level 5:** Battle Hymn also grants +8 physical defense.
**Level 7:** Heroic Inspiration triggers on any ally kill (not just crits).
**Level 9 Capstone:** **Anthem of Victory** -- All allies gain +1 action, +30% damage, and heal 15% max HP. Costs 12 groove. Once per combat.

**Mechanic Modification:** Musical Groove now passively generates 1 per turn (normally only from actions).

---

#### College of Lore
**Theme:** Knowledge debuffer -- weakens enemies through psychic assaults and information warfare.

**Level 3 Skills:**
- **Cutting Words** (REACTION, slot_cost 3): When an enemy attacks, reduce their damage by 25% for that attack. Costs 2 groove.
- **Psychic Scream** (ACTION, slot_cost 5): All enemies (base_power 30, element PSYCHIC). -10 magical defense for 2 turns. Generates 1 groove. 18 mana.
- **Expose Weakness** (BONUS_ACTION, slot_cost 3): Single enemy: reveal all elemental weaknesses. Target takes +15% elemental damage for 3 turns. Generates 1 groove.

**Level 3 Passive:** All debuffs applied by Bard last +1 turn. Groove generation from debuff skills +1. +10% magical attack.

**Level 5:** Cutting Words also reflects 15% of the mitigated damage back.
**Level 7:** Psychic Scream also reduces physical defense by 10.
**Level 9 Capstone:** **Song of Unraveling** -- All enemies lose ALL buffs and take (base_power 50, element PSYCHIC). 10 groove. Once per combat.

**Mechanic Modification:** Grand Finale (base skill) now also applies -20 to all enemy defenses for 2 turns.

---

### 9. Monk

#### Way of the Open Hand
**Theme:** Maximum damage throughput -- devastating combo attacks, equilibrium rewards aggression.

**Level 3 Skills:**
- **Palm Strike** (ACTION, slot_cost 5): Single enemy (base_power 50). If Equilibrium is in Destruction zone, deals +30% damage. Shifts toward Destruction. 12 mana.
- **Quivering Palm** (ACTION, slot_cost 7): Single enemy (base_power 35). Applies Quivering Palm debuff: after 2 turns, target takes (base_power 60) pure damage. 20 mana. 5-turn cooldown.
- **Flow State** (PASSIVE): Consecutive attacks without using a defensive skill grant stacking +5% damage (max +25%).

**Level 3 Passive:** +10% physical attack. Destruction zone bonuses increased by +10%.

**Level 5:** Palm Strike bonus in Destruction zone increases to +50%.
**Level 7:** Flow State max stacks increase to +40%.
**Level 9 Capstone:** **One-Inch Punch** -- Single target (base_power 120). Consumes all Equilibrium (must be deep in Destruction). 6-turn cooldown.

**Mechanic Modification:** Flurry of Blows hits 3 times instead of 2 (third hit base_power 10).

---

#### Way of Shadow
**Theme:** Evasive martial artist -- dodges everything, strikes from nowhere.

**Level 3 Skills:**
- **Shadow Strike** (ACTION, slot_cost 4): Single enemy (base_power 35). If Equilibrium is in Vitality zone, gain stealth after attack. 10 mana.
- **Vanishing Step** (REACTION, slot_cost 3): Completely negate one incoming attack. Shifts toward Vitality. 3-turn cooldown.
- **Phantom Movement** (PASSIVE): +15% dodge chance. While in Vitality zone, +10% additional dodge.

**Level 3 Passive:** +10 Speed. +15% physical defense.

**Level 5:** Vanishing Step cooldown reduced to 2 turns.
**Level 7:** Phantom Movement dodge bonus in Vitality zone increases to +20%.
**Level 9 Capstone:** **Eclipse** -- Become untargetable for 1 turn. Next attack deals +100% damage. Once per combat.

**Mechanic Modification:** Meditate (base skill) now also grants +15 physical defense for 1 turn.

---

### 10. Druid

#### Circle of the Moon
**Theme:** Shape-shifting predator -- stronger animal forms with more HP and damage.

**Level 3 Skills:**
- **Savage Transformation** (BONUS_ACTION, slot_cost 5): Transform into a powerful beast form: +30% max HP, +20% physical attack, -20% magical defense. Lasts entire combat. Replaces base Transform.
- **Maul** (ACTION, slot_cost 4): Single enemy (base_power 45). Only usable in beast form. Applies Bleed (base_power 10, 3 turns).
- **Wild Resilience** (PASSIVE): In beast form, regenerate 5% max HP per turn.

**Level 3 Passive:** Beast form HP bonus increased to +40%. Beast form gains +10 physical defense.

**Level 5:** Maul base_power increases to 60. Bleed base_power increases to 15.
**Level 7:** Wild Resilience increases to 8% max HP per turn.
**Level 9 Capstone:** **Primal Avatar** -- Transform into apex predator form: +60% max HP, +40% physical attack, +20% physical defense. Immune to CC. Lasts 3 turns. Once per combat.

**Mechanic Modification:** Transformation no longer costs mana. Can transform as many times as wanted.

---

#### Circle of the Land
**Theme:** Spell-focused druid -- more field conditions, stronger nature magic, mana efficiency.

**Level 3 Skills:**
- **Entangling Roots** (ACTION, slot_cost 5): All enemies (base_power 20, element EARTH). Applies -20% Speed for 2 turns. Creates Earth field condition. 15 mana.
- **Nature's Bounty** (BONUS_ACTION, slot_cost 3): All allies heal (base_power 12). If a field condition is active, heal +50%. 12 mana.
- **Ley Line Tap** (PASSIVE): While a field condition is active, all spells cost 20% less mana.

**Level 3 Passive:** Field conditions last +2 turns. +10% magical attack.

**Level 5:** Entangling Roots also reduces physical attack by 10%.
**Level 7:** Ley Line Tap mana reduction increases to 30%.
**Level 9 Capstone:** **Wrath of Nature** -- All enemies (base_power 70, element EARTH). Automatically creates a field condition that deals (base_power 15) per turn for 4 turns. 35 mana. Once per combat.

**Mechanic Modification:** Wild Growth (base skill) can now create 2 different field conditions simultaneously.

---

### 11. Sorcerer

#### Draconic Bloodline
**Theme:** Elemental specialist -- chooses an element, all spells of that element are empowered.

**Level 3 Skills:**
- **Draconic Affinity** (PASSIVE): Choose one element at subclass selection. That element's damage +25%.
- **Dragon Breath** (ACTION, slot_cost 6): All enemies (base_power 40, chosen element). 20 mana.
- **Draconic Armor** (PASSIVE): +15% physical defense. Resistance to chosen element (50% less damage from it).

**Level 3 Passive:** Chosen element spells cost 15% less mana. +25% chosen element damage.

**Level 5:** Draconic Affinity bonus increases to +35%.
**Level 7:** Dragon Breath also applies the on-hit effect of the chosen element (e.g., Fire applies burn).
**Level 9 Capstone:** **Dragon Form** -- For 3 turns: +30% all attacks, immune to chosen element, all spells deal chosen element. 30 mana. Once per combat.

**Mechanic Modification:** Metamagic can also change a spell's element to the Draconic element (element swap).

---

#### Wild Magic
**Theme:** Chaotic sorcerer -- random powerful effects, high variance, high ceiling.

**Level 3 Skills:**
- **Wild Surge** (PASSIVE): Each spell cast has a 25% chance to trigger a random Wild Surge effect (from a table of 10 effects -- some very good, some disruptive).
- **Chaos Bolt** (ACTION, slot_cost 4): Single enemy (base_power 30, random element each cast). If it kills, bounces to another enemy for half damage. 12 mana.
- **Bend Luck** (REACTION, slot_cost 3): Reroll any single die result (crit check, ailment chance, etc.) for ally or enemy. 2-turn cooldown.

**Level 3 Passive:** +10% all damage. +5% chance of "mega surge" (effect is doubled).

**Level 5:** Wild Surge chance increases to 35%. Mega surge chance to 10%.
**Level 7:** Chaos Bolt can bounce up to 3 times.
**Level 9 Capstone:** **Controlled Chaos** -- Trigger 3 Wild Surge effects simultaneously (player picks from 5 random options, chooses 3). Once per combat.

**Wild Surge Table (10 effects):**
1. +30% damage on this spell
2. Heal caster for 20% max HP
3. All enemies take 15 damage
4. Caster gains +20 Speed for 2 turns
5. Random ally gains a shield (25% caster max HP)
6. Random enemy is Confused for 1 turn
7. All allies gain +10% damage for 1 turn
8. Caster takes 10% max HP as damage (downside)
9. All cooldowns reduced by 1
10. Random element applied to target for 2 turns

**Mechanic Modification:** Mana Rotation also has a 20% chance to trigger a Wild Surge.

---

### 12. Warlock

#### Fiend Pact
**Theme:** Dark power dealer -- insanity fuels devastating shadow magic.

**Level 3 Skills:**
- **Hellfire** (ACTION, slot_cost 6): All enemies (base_power 35, element DARKNESS). Applies Scorch (base_power 8, 3 turns). 18 mana.
- **Dark Bargain** (BONUS_ACTION, slot_cost 3): Sacrifice 15% current HP. Gain 30 insanity. Next dark spell deals +40% damage.
- **Soul Leech** (PASSIVE): When killing an enemy with a darkness spell, heal 20% of damage dealt.

**Level 3 Passive:** +15% DARKNESS damage. Insanity gain +20%.

**Level 5:** Hellfire Scorch base_power increases to 12.
**Level 7:** Soul Leech heal increases to 30% and triggers on any kill (not just darkness).
**Level 9 Capstone:** **Infernal Gate** -- Summon infernal entity that attacks all enemies for (base_power 80, DARKNESS) and heals party for 50% of damage dealt. 90 insanity. Once per combat.

**Mechanic Modification:** Insatiable Thirst (class mechanic) now also converts 10% of healing received into insanity.

---

#### Celestial Pact
**Theme:** Redeemed warlock -- insanity powers holy healing alongside dark damage.

**Level 3 Skills:**
- **Searing Light** (ACTION, slot_cost 4): Single enemy (base_power 30, element HOLY). Heals lowest HP ally for 50% of damage dealt. 12 mana. Generates 10 insanity.
- **Celestial Radiance** (ACTION, slot_cost 5): All allies heal (base_power 25). All enemies take (base_power 10, HOLY). 20 mana. Generates 15 insanity.
- **Light in the Dark** (PASSIVE): At 50+ insanity, all healing done +20%.

**Level 3 Passive:** Healing spells generate insanity equal to 25% of healing done. +15% healing done.

**Level 5:** Searing Light heals for 75% of damage dealt.
**Level 7:** Light in the Dark threshold reduced to 30 insanity and bonus increased to +30%.
**Level 9 Capstone:** **Duality Burst** -- Deal (base_power 60, HOLY) to all enemies and heal all allies for same amount. 80 insanity. Once per combat.

**Mechanic Modification:** Familiar (if summoned) can now also heal a random ally for 10% of Warlock's max HP per turn.

---

### 13. Artificer

#### Alchemist
**Theme:** Potion master -- creates and enhances consumables during combat.

**Level 3 Skills:**
- **Brew Potion** (BONUS_ACTION, slot_cost 3): Create a temporary combat potion (choose from: heal 25% max HP, restore 20% max mana, +15 attack for 2 turns, or cure all ailments). Costs 15 mana. 2/combat.
- **Alchemical Fire** (ACTION, slot_cost 4): Single enemy (base_power 35, element FIRE). Applies Burn (base_power 10, 3 turns). 12 mana.
- **Potent Mixtures** (PASSIVE): All consumable items used by any party member are +30% effective.

**Level 3 Passive:** +1 consumable item slot for party inventory. Consumables cost 20% less gold in shops. +10% healing received.

**Level 5:** Brew Potion can create 3/combat. New option: Full Restore (heal+mana 15% each).
**Level 7:** Potent Mixtures bonus increases to +50%.
**Level 9 Capstone:** **Philosopher's Stone** -- At combat start, automatically apply 1 random potion to each party member. Passive.

**Mechanic Modification:** Tech Suit (base mechanic) also provides +10% item effectiveness.

---

#### Armorer
**Theme:** Power armor specialist -- becomes a tanky frontliner with energy-based defense.

**Level 3 Skills:**
- **Energy Overload** (ACTION, slot_cost 5): Single enemy (base_power 40, element LIGHTNING). Grants self +20 physical defense for 1 turn. 15 mana.
- **Guardian Mode** (BONUS_ACTION, slot_cost 4): All allies in same position gain +15 physical defense for 2 turns. Self takes 10% more damage (taunt). 12 mana.
- **Reactive Plating** (PASSIVE): When hit, gain a shield equal to 10% of damage taken. Stacks up to 30% max HP.

**Level 3 Passive:** +20% physical defense. +10% max HP.

**Level 5:** Guardian Mode defense bonus increases to +20. Self damage increase reduced to 5%.
**Level 7:** Reactive Plating cap increases to 50% max HP.
**Level 9 Capstone:** **Fortress Protocol** -- For 3 turns: +50% physical defense, +50% magical defense, all damage to allies redirected to Artificer (who takes 50% of redirected damage). 30 mana. Once per combat.

**Mechanic Modification:** Tech Suit energy pool increases by 30%. Suit abilities cost 15% less energy.

---

## Data Structure

### `data/subclasses/subclass_definitions.json`
```json
{
  "fighter_champion": {
    "subclass_id": "fighter_champion",
    "class_id": "fighter",
    "name": "Champion",
    "description": "Raw martial superiority -- crits harder, hits harder, never stops swinging.",
    "passive_bonus": {
      "stat_modifiers": [
        {"stat": "PHYSICAL_ATTACK", "type": "PERCENT", "value": 10}
      ]
    },
    "skill_ids_level_3": ["improved_critical", "mighty_blow", "champions_resolve"],
    "upgrades": {
      "5": {"description": "Improved Critical: +20% crit, 2.75x mult"},
      "7": {"description": "Mighty Blow: base_power 70, no cooldown"},
      "9": {"skill_id": "undying_champion", "description": "Capstone: revive once per combat"}
    }
  }
}
```

### `data/subclasses/skills/<subclass_id>.json`
One file per subclass containing all new skills introduced at levels 3, 5, 7, 9.

---

## Implementation Steps

### Step 1: Subclass Data Schema
- Create `data/subclasses/subclass_definitions.json` with all 26 entries.
- Create `src/core/progression/subclass_definition.py` (frozen dataclass + loader).
- Test: definitions load, all 26 subclasses present, class_id matches.

### Step 2: Subclass Skill JSONs
- Create 26 skill JSON files under `data/subclasses/skills/`.
- Extend `SkillLoader` to load subclass skills.
- Test: all subclass skills parse correctly.

### Step 3: Subclass Application
- Create `src/core/progression/subclass_system.py`:
  - `choose_subclass(character, subclass_id)` -- validates class match, applies passive, adds skills.
  - `apply_level_upgrade(character, level)` -- applies the level 5/7/9 upgrades.
- Add `subclass_id: str | None` field to Character.
- Test: subclass choice applies passive, adds skills, prevents double-choosing.

### Step 4: Subclass Choice UI
- Create `src/ui/scenes/subclass_choice_scene.py`.
- Wire into run orchestrator: when level 3 is reached, show subclass choice after attribute distribution.

### Step 5: Level 5/7/9 Upgrades
- Hook `apply_level_upgrade` into the level-up flow.
- Test: each upgrade is correctly applied at the right level.

---

## Files to Create/Modify

### Create
- `data/subclasses/subclass_definitions.json`
- `data/subclasses/skills/` (26 JSON files)
- `src/core/progression/subclass_definition.py`
- `src/core/progression/subclass_system.py`
- `src/ui/scenes/subclass_choice_scene.py`
- `tests/core/test_progression/test_subclass_system.py`

### Modify
- `src/core/characters/character.py` -- add `subclass_id` field
- `src/core/skills/skill_loader.py` -- load subclass skills
- `src/core/progression/level_up_system.py` -- trigger subclass choice at level 3
- `src/dungeon/run/run_orchestrator.py` -- add `SUBCLASS_CHOICE` scene

---

## Test Strategy

| Test Category | What to Verify |
|--------------|----------------|
| Data Loading | All 26 subclass definitions load without error |
| Class Match  | Cannot apply a Fighter subclass to a Mage |
| Skill Addition | Subclass skills appear in character's available skill pool |
| Passive Application | Stat modifiers from passive are reflected in combat stats |
| No Double Pick | Cannot choose a subclass if one is already chosen |
| Level Upgrades | Correct upgrades applied at levels 5, 7, 9 |
| Capstone | Level 9 capstone skill appears and is usable |
