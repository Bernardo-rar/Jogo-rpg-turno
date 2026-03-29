# Visual Polish GDD -- RPG Turno

**Version**: 1.0
**Date**: 2026-03-29
**Status**: Design Spec (pre-implementation)
**Depends on**: existing animation system (`src/ui/animations/`), Pygame 2.x, Consolas/monospace font


---

## Table of Contents

1. [Design Pillars](#1-design-pillars)
2. [System 1 -- Element-Specific Particle Effects](#2-system-1----element-specific-particle-effects)
3. [System 2 -- Character Card Improvements](#3-system-2----character-card-improvements)
4. [System 3 -- Scene Transition Animations](#4-system-3----scene-transition-animations)
5. [System 4 -- Cooldown Visual Display](#5-system-4----cooldown-visual-display)
6. [System 5 -- Combat Log Enhancement](#6-system-5----combat-log-enhancement)
7. [Implementation Priority Matrix](#7-implementation-priority-matrix)
8. [Performance Budget](#8-performance-budget)
9. [File Manifest](#9-file-manifest)
10. [Changelog](#10-changelog)


---

## 1. Design Pillars

Every visual change must satisfy at least one of these pillars. If it satisfies none, cut it.

| Pillar | Definition | Test Question |
|--------|-----------|---------------|
| **Readability** | The player can instantly identify what happened | "Can I understand this event in under 0.5 seconds?" |
| **Juice** | The game feels alive, responsive, and rewarding | "Does this make hitting/healing feel better?" |
| **Identity** | Each element/class/state looks distinct | "Can I tell fire from ice without reading text?" |
| **Performance** | 60 FPS on modest hardware, zero frame drops | "Does this stay under the particle budget?" |


---

## 2. System 1 -- Element-Specific Particle Effects

### 2.1 Purpose

Replace the generic `MagicBurst` (concentric circles) with distinct elemental identities. Physical attacks get multi-slash treatment. Every attack type should be visually distinguishable at a glance.

### 2.2 Player Experience Goal

"I cast a fire spell and the target erupts in flame. I cast ice and shards crystallize. Each element feels different."


### 2.3 Architecture: Particle System

The particle system is composed of two classes and a data-driven configuration.

#### 2.3.1 Particle (Value Object)

```
Particle:
    x: float                # world position
    y: float
    vx: float               # velocity pixels/ms
    vy: float
    lifetime_ms: int         # total lifetime
    elapsed_ms: int          # current age
    color: (R, G, B)
    size: float              # radius in pixels
    size_decay: float        # 1.0 = no decay, 0.0 = shrinks to nothing
    gravity: float           # pixels/ms^2, positive = down
    rotation: float          # degrees (for non-circular shapes)
    shape: "circle" | "line" | "diamond" | "spark"
```

**Update rule** (called every frame):
```
x += vx * dt_ms
y += vy * dt_ms
vy += gravity * dt_ms
size = initial_size * (1.0 - (elapsed / lifetime) * (1.0 - size_decay))
alpha = 255 * (1.0 - elapsed / lifetime)
```

#### 2.3.2 ParticleEmitter

```
ParticleEmitter:
    config: ParticleConfig   # data-driven config
    target_rect: (x, y, w, h)
    blocking: bool
    _particles: list[Particle]
    _elapsed_ms: int

    spawn() -> creates N particles with randomized properties from config
    update(dt_ms) -> ticks all particles, removes dead ones
    draw(surface) -> renders all alive particles
    is_done -> True when all particles expired
```

#### 2.3.3 ParticleConfig (Frozen Dataclass)

```python
@dataclass(frozen=True)
class ParticleConfig:
    name: str
    count: int                          # number of particles
    duration_ms: int                    # emitter total duration
    lifetime_range: tuple[int, int]     # per-particle lifetime min/max ms
    speed_range: tuple[float, float]    # pixels/ms
    angle_range: tuple[float, float]    # emission angle in degrees
    size_range: tuple[float, float]     # radius min/max pixels
    size_decay: float                   # 0.0-1.0
    colors: list[tuple[int, int, int]]  # palette, pick randomly
    gravity: float                      # pixels/ms^2
    shape: str                          # "circle" | "line" | "diamond" | "spark"
    spawn_area: str                     # "center" | "bottom" | "full" | "edges"
    blocking: bool                      # whether it blocks combat flow
```


### 2.4 Element Specifications

Each element gets a unique `ParticleConfig`. All values are `[PLACEHOLDER]` -- tune after first visual test.

#### Physical Slash (Enhanced)

| Property | Value | Rationale |
|----------|-------|-----------|
| Duration | 350ms | Slightly longer than current 300ms for multi-slash |
| Count | 3 slash lines + 8 spark particles | Three diagonal lines + debris |
| Movement | Lines extend diagonally (top-left to bottom-right, then opposite) | Classic X-slash manga/anime read |
| Colors | `(255,255,200)`, `(220,220,180)`, `(200,200,160)` | Warm white, steel-ish |
| Shape | `line` for slashes, `spark` for debris | Lines drawn with `pygame.draw.line`, sparks are small rects |
| Blocking | True | Must finish before next action |

**Visual sequence**:
1. Frame 0-120ms: First slash (top-left to bottom-right), expanding
2. Frame 60-180ms: Second slash (top-right to bottom-left), expanding (offset 60ms)
3. Frame 100-250ms: Third slash (horizontal), expanding
4. Frame 150-350ms: 8 spark particles scatter outward from intersection point

**Implementation**: New class `MultiSlash` replaces current `SlashEffect`. Three `pygame.draw.line` calls with staggered progress + `ParticleEmitter` for sparks.


#### Fire

| Property | Value | Rationale |
|----------|-------|-----------|
| Duration | 500ms | Medium -- fire should linger |
| Count | 25 particles | Dense enough to look like flame |
| Lifetime | 200-400ms per particle | Short-lived individual embers |
| Movement | Rise upward with slight horizontal jitter | Fire rises |
| Speed | 0.03-0.08 px/ms upward | Gentle float |
| Colors | `(255,120,30)`, `(255,80,0)`, `(255,200,50)` | Orange core, red edge, yellow tips |
| Size | 2-5px | Small embers |
| Size decay | 0.3 | Shrinks to 30% before dying |
| Gravity | -0.0001 | Negative = particles float up |
| Shape | `circle` | Soft dots |
| Spawn area | `bottom` | Fire rises from base of target |
| Blocking | True | |

**Extra**: Draw a brief orange-tinted overlay (alpha 30, 200ms) on the target card to simulate "engulfed in flame."


#### Ice

| Property | Value | Rationale |
|----------|-------|-----------|
| Duration | 450ms | Quick crystallization |
| Count | 15 particles | Fewer but larger shards |
| Lifetime | 300-450ms | Linger as they crystallize |
| Movement | Scatter outward from center, then decelerate | Burst then freeze |
| Speed | 0.04-0.1 px/ms | Burst velocity |
| Colors | `(130,200,255)`, `(180,230,255)`, `(220,240,255)` | Cyan to white gradient |
| Size | 3-7px | Larger crystalline fragments |
| Size decay | 0.8 | Almost stays full size (ice doesn't melt fast) |
| Gravity | 0.00005 | Slight downward drift |
| Shape | `diamond` | Crystalline look (rotated square) |
| Spawn area | `center` | Burst from impact point |
| Blocking | True | |

**Extra**: Brief white flash (alpha 60, 100ms) at spawn moment to sell the "freeze" impact.


#### Lightning

| Property | Value | Rationale |
|----------|-------|-----------|
| Duration | 300ms | Fastest element -- lightning is instant |
| Count | 4 bolt segments + 12 spark particles | Bolts + scatter |
| Lifetime | 100-200ms | Very brief |
| Movement | Zigzag downward (bolts), scatter outward (sparks) | Top-to-bottom bolt |
| Colors | `(255,255,100)`, `(255,255,200)`, `(200,200,255)` | Yellow core, white corona |
| Size | 2-3px for sparks | Tiny electrical arcs |
| Shape | `spark` for particles, custom zigzag draw for bolts | |
| Spawn area | `full` | Bolt hits anywhere on card |
| Blocking | True | |

**Implementation**: New class `LightningBolt` -- draws 3-4 zigzag line segments from top to target center. Each segment is a series of connected `pygame.draw.line` calls with random horizontal offsets every 8-12 pixels vertically. Sparks use `ParticleEmitter`.

**Visual sequence**:
1. Frame 0: Full-screen white flash (alpha 40, 50ms)
2. Frame 0-150ms: Zigzag bolt drawn from above card to center
3. Frame 100-300ms: Spark particles from impact point


#### Holy

| Property | Value | Rationale |
|----------|-------|-----------|
| Duration | 600ms | Majestic, slower |
| Count | 20 particles | Golden rain |
| Lifetime | 400-600ms | Lingers like divine light |
| Movement | Float downward gently | Light descending |
| Speed | 0.02-0.04 px/ms | Graceful |
| Colors | `(255,255,200)`, `(255,240,150)`, `(255,220,100)` | Gold gradient |
| Size | 2-4px | Small sparkles |
| Size decay | 0.5 | Fade to half |
| Gravity | 0.00003 | Slight downward |
| Shape | `diamond` | Star-like sparkles |
| Spawn area | `full` | Rain across entire card |
| Blocking | True | |

**Extra**: Subtle golden glow (BuffAura-style) around card during effect.


#### Darkness

| Property | Value | Rationale |
|----------|-------|-----------|
| Duration | 550ms | Creeping |
| Count | 18 particles | Dense fog |
| Lifetime | 350-550ms | Lingers ominously |
| Movement | Drift inward toward center, slight oscillation | Converging mist |
| Speed | 0.01-0.03 px/ms | Slow, creeping |
| Colors | `(100,50,150)`, `(80,30,120)`, `(60,20,100)` | Deep purple |
| Size | 4-8px | Large, diffuse blobs |
| Size decay | 0.6 | |
| Gravity | 0 | Weightless mist |
| Shape | `circle` | Blurry blobs |
| Spawn area | `edges` | Converge from card edges to center |
| Blocking | True | |


#### Water

| Property | Value | Rationale |
|----------|-------|-----------|
| Duration | 450ms | Medium splash |
| Count | 20 particles | Droplets |
| Lifetime | 250-400ms | |
| Movement | Arc upward then fall (parabolic) | Splash pattern |
| Speed | 0.05-0.1 px/ms | |
| Colors | `(50,130,255)`, `(80,160,255)`, `(120,190,255)` | Blue gradient |
| Size | 2-4px | Small droplets |
| Gravity | 0.00015 | Strong gravity = parabolic arc |
| Shape | `circle` | Water drops |
| Spawn area | `center` | Splash from impact |
| Blocking | True | |


#### Earth

| Property | Value | Rationale |
|----------|-------|-----------|
| Duration | 400ms | Impact + settle |
| Count | 15 particles | Rock chunks |
| Lifetime | 200-350ms | |
| Movement | Burst upward then fall | Impact explosion |
| Speed | 0.06-0.12 px/ms | Forceful |
| Colors | `(160,120,60)`, `(140,100,40)`, `(120,80,30)` | Brown/earth |
| Size | 3-6px | Larger chunks |
| Gravity | 0.0002 | Heavy = falls fast |
| Shape | `diamond` | Angular rock fragments |
| Spawn area | `bottom` | Erupts from below |
| Blocking | True | |


#### Psychic

| Property | Value | Rationale |
|----------|-------|-----------|
| Duration | 500ms | Disorienting |
| Count | 12 particles | |
| Movement | Spiral inward toward target head area | Mind invasion |
| Colors | `(255,150,200)`, `(255,120,180)`, `(220,100,160)` | Pink/magenta |
| Size | 2-4px | |
| Shape | `diamond` | |
| Spawn area | `edges` | Close in from outside |
| Blocking | True | |


#### Force

| Property | Value | Rationale |
|----------|-------|-----------|
| Duration | 350ms | Quick concussive blast |
| Count | 20 particles | Shockwave fragments |
| Movement | Burst outward from center in all directions | Explosion |
| Colors | `(200,200,200)`, `(220,220,220)`, `(240,240,240)` | White/silver |
| Size | 2-5px | |
| Gravity | 0.00005 | Slight drift |
| Shape | `spark` | Impact sparks |
| Spawn area | `center` | Radial burst |
| Blocking | True | |

**Extra**: Screen shake (2px, 200ms) via `CardShake` on all visible cards simultaneously.


#### Celestial

| Property | Value | Rationale |
|----------|-------|-----------|
| Duration | 600ms | Ethereal |
| Count | 16 particles | |
| Movement | Orbit around card center, slowly expanding | Cosmic orbit |
| Colors | `(200,180,255)`, `(180,160,240)`, `(220,200,255)` | Pale violet |
| Size | 2-4px | |
| Shape | `circle` | Soft orbs |
| Spawn area | `center` | Orbit from center |
| Blocking | True | |


#### Heal (Enhanced)

| Property | Value | Rationale |
|----------|-------|-----------|
| Duration | 500ms | Slightly longer than current 400ms |
| Count | 15 particles | More than current 10 |
| Movement | Rise upward with gentle sine-wave horizontal drift | Serene float |
| Colors | `(80,255,80)`, `(120,255,120)`, `(160,255,160)` | Green gradient |
| Size | 2-5px | |
| Shape | `circle` | Soft orbs |
| Spawn area | `bottom` | Rise from base |
| Blocking | True | |

**Extra**: Brief green tint on HP bar (pulse brighter for 200ms).


#### Buff (Enhanced)

| Property | Value | Rationale |
|----------|-------|-----------|
| Duration | 600ms | Match current |
| Effect | Pulsing border (keep current BuffAura) + 8 rising sparkles | Combine aura with particles |
| Colors | `(80,200,80)`, `(120,255,120)` | Green/cyan |
| Blocking | False | Non-blocking allows combat to continue |


#### Debuff (Enhanced)

| Property | Value | Rationale |
|----------|-------|-----------|
| Duration | 600ms | Match current |
| Effect | Pulsing border (red) + 8 descending particles | Draining feel |
| Colors | `(200,80,80)`, `(255,60,60)` | Red |
| Blocking | False | |


### 2.5 Integration with AnimationFactory

The `AnimationFactory._create_magical_damage` method is the single modification point. Currently it creates a `MagicBurst` for all elements. The new dispatch will be:

```
ELEMENT_EFFECTS: dict[ElementType, ParticleConfig] = {
    ElementType.FIRE: FIRE_CONFIG,
    ElementType.ICE: ICE_CONFIG,
    ...
}
```

For elements that need custom draw logic (Lightning zigzag, MultiSlash lines), a dedicated class is used instead of generic `ParticleEmitter`.

**Modified files**: `animation_factory.py` (swap MagicBurst for element-specific emitters)
**New files**: `particle.py`, `particle_emitter.py`, `particle_configs.py`, `multi_slash.py`, `lightning_bolt.py`
**Preserved files**: `MagicBurst` kept as fallback for unmapped elements


### 2.6 Tuning Levers

| Lever | Range | Effect |
|-------|-------|--------|
| `count` | 5-50 | Density of effect |
| `duration_ms` | 200-800 | How long effect lingers |
| `speed_range` | 0.01-0.15 | Particle velocity |
| `size_range` | 1-10 | Particle prominence |
| `gravity` | -0.0003 to 0.0003 | Float up vs fall down |
| `colors[0]` | any RGB | Primary effect color |
| `size_decay` | 0.0-1.0 | Whether particles shrink |

All values are in `particle_configs.py` as module-level constants. No JSON needed -- these are purely visual configs that never change at runtime.


### 2.7 Edge Cases

- **Element is None**: Falls back to generic MagicBurst (current behavior preserved)
- **Target card off-screen**: Particles clipped by surface bounds (Pygame handles this)
- **Multiple simultaneous effects**: Each gets its own ParticleEmitter instance, all update independently
- **Speed multiplier active (2x/3x)**: dt_ms is already scaled in PlayableCombatScene.update, particles respect this automatically


---

## 3. System 2 -- Character Card Improvements

### 3.1 Purpose

Make character cards more informative and visually distinctive without adding sprite art. All rendering uses `pygame.draw` primitives.

### 3.2 Player Experience Goal

"I can identify each character's class, position, and status at a glance without reading text."


### 3.3 Class Icons (Geometric Symbols)

Each class gets a 16x16 pixel icon drawn with `pygame.draw` primitives. Rendered in the top-right corner of the character card.

| Class | Symbol | Draw Method | Color |
|-------|--------|-------------|-------|
| Fighter | Sword: vertical line + crossguard | 2 lines | `RES_FIGHTER_AP` |
| Mage | Star: 4-point star | 4 triangles | `RES_MAGE_BARRIER` |
| Cleric | Cross: plus sign | 2 thick lines | `RES_CLERIC_HOLY` |
| Barbarian | Axe: triangle blade + shaft | polygon + line | `RES_BARBARIAN_FURY` |
| Paladin | Shield: rounded rect with cross | rect + 2 lines | `RES_PALADIN_FAVOR` |
| Ranger | Arrow: triangle tip + shaft | polygon + line | `RES_RANGER_FOCUS` |
| Monk | Fist: circle with inner line | circle + line | `RES_MONK_EQUILIBRIUM` |
| Sorcerer | Flame: teardrop shape | polygon | `RES_SORCERER_ROTATION` |
| Warlock | Eye: ellipse with dot | ellipse + circle | `RES_WARLOCK_INSANITY` |
| Druid | Leaf: curved polygon | polygon | `RES_DRUID_FORM` |
| Rogue | Dagger: thin triangle + crossguard | polygon + line | `RES_ROGUE_STEALTH` |
| Bard | Note: circle + stem + flag | circle + 2 lines | `RES_BARD_GROOVE` |
| Artificer | Gear: circle with notches | circle + lines | `RES_ARTIFICER_SUIT` |

**Implementation**: New file `src/ui/components/class_icon.py` with function:
```
draw_class_icon(surface, class_name: str, x: int, y: int, size: int = 16) -> None
```

Dispatch table: `class_name.lower() -> draw function`. Each draw function is 5-10 lines of `pygame.draw` calls.

**Integration**: Called from `draw_character_card` after drawing the name. Position: `x + CARD_WIDTH - 24, y + 4`.


### 3.4 Position Indicators

**Current**: Front and back characters differ only by X position (20px offset). Not visually clear.

**Design**: Add a small text tag below the character name.

| Position | Visual | Color |
|----------|--------|-------|
| FRONT | `[F]` text tag in bold | `(200, 160, 60)` -- warm gold |
| BACK | `[B]` text tag in muted | `(120, 120, 140)` -- cool gray |

Additionally, FRONT cards get a slightly brighter border (current border + 20 brightness), BACK cards get the default border.

**Implementation**: Modify `_draw_name` in `character_card.py` to append position tag. The Position enum value is already available in `CharacterSnapshot`.


### 3.5 Death State Enhancement

**Current**: Card uses `DEAD_COLOR (80,80,80)` background. `DeathFade` adds a dark overlay.

**Proposed additions**:
1. Large "X" drawn across the card in `(120, 40, 40)` with 3px line width
2. Name rendered in `TEXT_MUTED` instead of `TEXT_WHITE`
3. HP/Mana bars hidden (no point showing them)
4. All effect icons cleared

**Implementation**: Modify `draw_character_card` to check `snap.is_alive`. If dead, draw simplified card: gray background, X overlay, name only.


### 3.6 Active Turn Glow Enhancement

**Current**: Yellow pulsing border via `draw_turn_indicator` (0.7 + 0.3*sin wave, 3px border).

**Proposed**:
1. Increase border to 4px during active turn
2. Add corner glow: 4 small circles at card corners with same pulse alpha
3. Add subtle inner glow: second border 1px inside, half alpha

**Implementation**: Modify `draw_turn_indicator` in `turn_indicator.py`. Add inner rect draw call and corner circle draws.


### 3.7 Status Effect Stacking

**Current**: `draw_effect_icons` shows up to 5 effect badges. Duplicate effects show as separate badges.

**Proposed**: Group identical effects and show count:
- Single effect: `Ps` (current behavior)
- Stacked effect: `Ps x3` (badge is wider: 34px instead of 22px)

**Implementation**: Pre-process the `effects` tuple in `draw_effect_icons`:
1. Count occurrences of each effect name
2. Render unique names with count suffix if count > 1
3. Wider badge for stacked effects


### 3.8 Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `src/ui/components/class_icon.py` | CREATE | Class icon dispatch + draw functions |
| `src/ui/components/character_card.py` | MODIFY | Add icon, position tag, death X, alive check |
| `src/ui/components/turn_indicator.py` | MODIFY | Enhanced glow with corners + inner border |
| `src/ui/components/effect_icons.py` | MODIFY | Stack grouping logic |
| `tests/ui/test_components/test_class_icon.py` | CREATE | Test draw dispatch + all 13 classes |


---

## 4. System 3 -- Scene Transition Animations

### 4.1 Purpose

Transitions communicate context changes. A fade says "scene change." A slide says "entering battle." A crack says "you lost." The player should feel the emotional weight of each transition.

### 4.2 Player Experience Goal

"Entering combat feels like stepping into an arena. Victory feels triumphant. Defeat feels heavy."


### 4.3 Combat Start: Card Slide-In

**Trigger**: `PlayableCombatScene` initializes.

**Visual sequence** (total duration: 600ms):
1. Frame 0-100ms: Screen is dark (BG_DARK)
2. Frame 100-400ms: Party cards slide in from right edge. Enemy cards slide in from left edge. Each card has a staggered delay (50ms between cards). Movement uses ease-out curve: `1 - (1-t)^2`
3. Frame 400-600ms: All cards in final position. Turn timeline fades in (alpha 0->255 over 200ms).

**Implementation**: New class `CombatIntroAnimation`:
- Stores initial off-screen X positions for each card
- On each frame, interpolates X from off-screen to final position
- Applies as card offsets (same mechanism as CardShake offsets)
- `blocking = True` -- no input accepted during intro

**Tuning levers**:
| Lever | Value | Range |
|-------|-------|-------|
| `SLIDE_DURATION_MS` | 300ms | 200-500 |
| `STAGGER_MS` | 50ms | 20-100 |
| `INITIAL_OFFSET` | 400px | 300-600 |
| `EASE_POWER` | 2.0 | 1.5-3.0 |


### 4.4 Victory: Gold Sparkle

**Trigger**: Combat result is `PARTY_VICTORY`.

**Visual sequence** (total duration: 1200ms):
1. Frame 0-200ms: "VICTORY" text fades in (scale from 0.8 to 1.0 -- simulated via font size lerp)
2. Frame 0-800ms: 30 gold sparkle particles spawn from center, drift outward in all directions
3. Frame 200-1200ms: Particles linger, fade out
4. Frame 800+: "[ENTER] Continue" prompt appears

**Particle spec**:
- Count: 30
- Colors: `(255,220,80)`, `(255,240,150)`, `(255,200,50)`
- Size: 2-4px
- Shape: diamond
- Movement: radial outward, slow (0.02-0.05 px/ms)
- Gravity: -0.00002 (slight upward float)
- Lifetime: 600-1000ms

**Implementation**: Integrate into `PlayableCombatScene._draw_result` or create `VictoryOverlay` class that the scene spawns when combat ends with victory.


### 4.5 Defeat: Screen Darken + Pulse

**Trigger**: Combat result is `PARTY_DEFEAT`.

**Visual sequence** (total duration: 1000ms):
1. Frame 0-200ms: Screen dims rapidly (overlay alpha 0->180)
2. Frame 200-400ms: Red pulse (overlay briefly flashes `(80,0,0,60)`)
3. Frame 400-600ms: "DEFEAT" text fades in, red color
4. Frame 600+: "[ENTER] Continue" prompt

**Implementation**: `DefeatOverlay` class, similar structure to `VictoryOverlay` but with dark/red color scheme. No particles -- defeat should feel heavy, not flashy.


### 4.6 Room Transition on Map: Node Pulse

**Trigger**: Player selects a node on the dungeon map.

**Visual sequence** (300ms):
1. Selected node border pulses bright (alpha oscillation 0.5 -> 1.0 -> 0.5, 2 cycles in 300ms)
2. Node color briefly brightens (+40 to each RGB channel, clamped)
3. After 300ms, scene transitions via existing `FadeTransition`

**Implementation**: Modify `DungeonMapScene.handle_event` to set a `_selected_node` and `_select_elapsed`. In `draw`, if a node is selected and elapsed < 300ms, apply pulse effect before triggering `on_complete`.


### 4.7 Boss Entrance: Shake + Flash

**Trigger**: Entering a BOSS room combat.

**Visual sequence** (800ms, plays before normal combat intro):
1. Frame 0-100ms: Full-screen white flash (alpha 0->200->0)
2. Frame 100-500ms: Screen shakes (sinusoidal, 6px amplitude, 4 cycles, decaying)
3. Frame 300-600ms: Boss name text fades in center, large font, red/purple color
4. Frame 600-800ms: Text fades out, transitions to normal combat intro

**Implementation**: `BossIntroAnimation` class. `blocking = True`. Plays before `CombatIntroAnimation`. The `PlayableCombatScene` constructor checks if the combat is a boss fight (passed as init param) and prepends this animation.


### 4.8 Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `src/ui/animations/combat_intro.py` | CREATE | Card slide-in animation |
| `src/ui/animations/victory_overlay.py` | CREATE | Gold sparkle victory effect |
| `src/ui/animations/defeat_overlay.py` | CREATE | Dark red defeat effect |
| `src/ui/animations/boss_intro.py` | CREATE | Flash + shake + name reveal |
| `src/ui/scenes/dungeon_map_scene.py` | MODIFY | Node pulse on selection |
| `src/ui/scenes/playable_combat_scene.py` | MODIFY | Wire intro/outro animations |


---

## 5. System 4 -- Cooldown Visual Display

### 5.1 Purpose

Players need to know when a skill will become available again. Currently, skills on cooldown show `(CD: N)` as text in the menu -- but only when viewing that skill's category. This is buried. We need to surface cooldown information proactively.

### 5.2 Player Experience Goal

"I can see at a glance which skills are cooling down and when they'll be ready, without navigating into the skill menu."


### 5.3 Action Menu: Cooldown Display (Already Exists -- Enhance)

**Current**: `_skill_unavailable_reason` returns `"CD: {remaining}"` which renders as gray text.

**Enhancement**:
1. Add a visual cooldown "meter" after the skill name: a small bar (30x6px) that fills as cooldown progresses
2. Color: gray background, `TEXT_MUTED` fill that grows as turns pass
3. Format: `Fireball (CD: 2) [==----]` where `=` is filled and `-` is remaining

**Implementation**: Modify `_draw_option` in `action_panel.py`. When an option has `reason` starting with `"CD:"`, parse the number and draw a mini progress bar.

Parsing: extract the number from reason text, also need `cooldown_total` (the skill's base cooldown) to compute fill ratio. This means `MenuOption` needs an optional `cooldown_info: tuple[int, int] | None` field (remaining, total).


### 5.4 Timeline: Cooldown Dots

**Proposed**: Under each character's timeline slot, show small dots representing skills on cooldown.

**Design decision: DEFER.** The timeline slots are already compact (100x26px). Adding cooldown dots would require either making slots taller (breaking layout) or using sub-pixel rendering. The action menu cooldown display + skill tooltip already provide this information when the player needs it.

**If revisited**: Use 3px colored dots below the slot, one per skill on cooldown, color-coded by remaining turns (red=1, yellow=2, gray=3+).


### 5.5 Skill Tooltip Enhancement

**Current**: `draw_skill_tooltip` shows skill name, description, damage, mana cost.

**Add**: If skill is on cooldown, show `"Cooldown: X/Y turns"` line in the tooltip with a mini bar.

**Implementation**: Modify `skill_tooltip.py` to accept optional cooldown info.


### 5.6 Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `src/ui/input/menu_state.py` | MODIFY | Add `cooldown_info` to MenuOption |
| `src/ui/input/action_menu.py` | MODIFY | Populate cooldown_info in skill options |
| `src/ui/components/action_panel.py` | MODIFY | Draw cooldown mini-bar |
| `src/ui/components/skill_tooltip.py` | MODIFY | Add cooldown line |


---

## 6. System 5 -- Combat Log Enhancement

### 6.1 Purpose

The combat log is the player's history of what happened. It should be scannable, with visual cues that let the player identify event types without reading full sentences.

### 6.2 Player Experience Goal

"I can scroll through the log and immediately see attacks (red), heals (green), buffs (blue) by color and tag. Old entries fade so the most recent action pops."


### 6.3 Event Prefix Tags

Since the font is Consolas (monospace), Unicode symbols are unreliable. Use bracketed text tags instead.

| Event Type | Tag | Color | Example |
|------------|-----|-------|---------|
| Damage (physical) | `[ATK]` | `TEXT_DAMAGE` | `[ATK] Fighter hits Goblin for 25` |
| Damage (magical) | `[MAG]` | Element color | `[MAG] Mage hits Goblin for 30` |
| Damage (critical) | `[CRIT]` | `TEXT_CRITICAL` | `[CRIT] Fighter hits Goblin for 50 CRIT!` |
| Heal | `[HEAL]` | `TEXT_HEAL` | `[HEAL] Cleric heals Fighter for 15` |
| Buff | `[BUFF]` | `EFFECT_BUFF` | `[BUFF] Mage buffs self: INT Up` |
| Debuff | `[DBF]` | `EFFECT_DEBUFF` | `[DBF] Warlock debuffs Goblin: STR Down` |
| Ailment | `[DOT]` | `TEXT_EFFECT` | `[DOT] Goblin afflicted: Poison` |
| Mana restore | `[MP]` | `MANA_BLUE` | `[MP] Mage restores 10 mana` |
| Cleanse | `[CLN]` | `TEXT_HEAL` | `[CLN] Cleric cleanses Poison from Fighter` |
| Death | `[KILL]` | `(255, 60, 60)` | `[KILL] Goblin has been slain!` |
| Turn start | `[TURN]` | `TEXT_YELLOW` | `[TURN] -- Fighter's turn --` |

**Implementation**: Modify `_format_event` in `playable_combat_scene.py` to prepend the tag. The tag and message can use different colors via a two-part render: tag in accent color, message in `TEXT_WHITE`.


### 6.4 Scrollable Log

**Current**: Shows last `LOG_MAX_VISIBLE` (9 in replay, 4 in interactive) lines. No scroll.

**Proposed**:
- `PageUp` / `PageDown` scrolls the log by `LOG_MAX_VISIBLE` lines
- Scroll position resets to bottom when a new event is added (auto-scroll)
- Visual scroll indicator: small up/down arrows at top/bottom of log panel when content extends beyond view

**Implementation**: Add `_scroll_offset` to `CombatLogPanel`. Modify `draw` to render from `offset` instead of always `[-max_visible:]`. Add `scroll_up` / `scroll_down` methods.


### 6.5 Entry Fade (Alpha Gradient)

**Current**: All visible lines rendered at full opacity.

**Proposed**: Oldest visible line renders at 40% alpha, newest at 100%. Linear interpolation between them.

Formula: `alpha = 0.4 + 0.6 * (line_index / (max_visible - 1))`

Where `line_index=0` is the oldest visible line and `line_index=max_visible-1` is the newest.

**Implementation**: Modify `CombatLogPanel.draw` to compute per-line alpha and render each line to an SRCALPHA surface.


### 6.6 Kill/Streak Highlighting

**Proposed**:
- When a character kills an enemy, the `[KILL]` log entry gets a special background: dark red bar behind the text
- Multi-kills within the same turn (AOE): `[KILL x2]` tag
- Overkill (damage > 2x remaining HP): `[OVERKILL]` tag in bright red

**Implementation**: Track kill events in `PlayableCombatScene._flush_new_events`. Death detection already exists in `_detect_deaths`. When a death is detected, add a kill log entry with the `[KILL]` tag and optionally a highlight background rect.


### 6.7 Two-Color Line Rendering

To render `[ATK]` in red and the rest of the message in white on the same line:

```python
def _draw_log_line(surface, x, y, tag, tag_color, message, msg_color, font, alpha):
    # Render tag
    tag_surf = font.render(tag + " ", True, (*tag_color, alpha))
    surface.blit(tag_surf, (x, y))
    # Render message after tag
    msg_x = x + tag_surf.get_width()
    msg_surf = font.render(message, True, (*msg_color, alpha))
    surface.blit(msg_surf, (msg_x, y))
```

This requires changing `CombatLogPanel._lines` from `list[tuple[str, tuple]]` to `list[LogEntry]` where:
```python
@dataclass(frozen=True)
class LogEntry:
    tag: str
    tag_color: tuple[int, int, int]
    message: str
    message_color: tuple[int, int, int]
    highlight_bg: bool = False
```


### 6.8 Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `src/ui/components/combat_log_panel.py` | MODIFY | LogEntry dataclass, scroll, alpha gradient, two-color render |
| `src/ui/scenes/playable_combat_scene.py` | MODIFY | Use tags in `_log_event`, add kill detection log |
| `tests/ui/test_components/test_combat_log_panel.py` | CREATE | Test scroll, alpha calc, line capacity |


---

## 7. Implementation Priority Matrix

Priorities ordered by **visual impact / effort ratio**. Higher priority = implement first.

| Priority | System | Visual Impact | Effort | Rationale |
|----------|--------|---------------|--------|-----------|
| **P0** | Element Particle Effects (Fire, Ice, Lightning) | HIGH | MEDIUM | These 3 elements cover ~60% of combat visuals. The particle system built here enables all other elements cheaply. |
| **P1** | Combat Log Tags + Fade | HIGH | LOW | Immediate readability improvement. Small code change, big UX win. |
| **P2** | Physical MultiSlash | MEDIUM | LOW | Most common attack type. Replaces boring single line with satisfying triple-slash. |
| **P3** | Death State Enhancement | MEDIUM | LOW | Dead cards currently look too similar to alive ones at a glance. |
| **P4** | Combat Intro Slide-In | HIGH | MEDIUM | First impression of every combat. Sets the tone. |
| **P5** | Remaining Elements (Holy, Dark, Water, Earth, Psychic, Force, Celestial) | MEDIUM | LOW each | Once particle system exists from P0, each element is ~30 min of config. |
| **P6** | Class Icons | MEDIUM | MEDIUM | 13 icons to draw. Nice for identity but not blocking gameplay. |
| **P7** | Victory/Defeat Overlays | MEDIUM | LOW | Emotional punctuation. Currently just text. |
| **P8** | Cooldown Mini-Bar | LOW | LOW | Nice-to-have. Current text display works. |
| **P9** | Scrollable Log | LOW | LOW | 4 lines is usually enough. Scroll is insurance. |
| **P10** | Boss Intro | LOW | MEDIUM | Only triggers on boss fights. Low frequency. |
| **P11** | Active Turn Glow Enhancement | LOW | LOW | Current glow works. Enhancement is subtle. |
| **P12** | Position Indicators | LOW | LOW | X offset already communicates this. Tag is redundant but clear. |
| **P13** | Status Effect Stacking | LOW | LOW | Edge case -- stacking is rare currently. |
| **P14** | Node Pulse on Map | LOW | LOW | Very brief interaction moment. |
| **P15** | Kill Streak Highlighting | LOW | LOW | Satisfying but rare and cosmetic. |


### Suggested Implementation Batches

**Batch 1 (Core Particle System + Quick Wins)**:
- Build `Particle`, `ParticleEmitter`, `ParticleConfig` classes
- Implement Fire, Ice, Lightning configs
- Implement MultiSlash
- Implement Combat Log tags + fade

**Batch 2 (Transitions + Remaining Elements)**:
- Combat Intro slide-in
- All remaining element configs
- Death state enhancement
- Victory/Defeat overlays

**Batch 3 (Polish)**:
- Class icons (all 13)
- Cooldown mini-bar
- Scrollable log
- Boss intro
- Active turn glow
- Position indicators
- Effect stacking
- Node pulse
- Kill streaks


---

## 8. Performance Budget

### 8.1 Particle Limits

| Constraint | Value | Rationale |
|------------|-------|-----------|
| Max particles per emitter | 50 | Tested on low-end machines |
| Max total particles on screen | 200 | 200 circles at 60 FPS = ~3ms draw time |
| Max simultaneous emitters | 8 | 4 party + 4 enemies worst case (AOE) |
| Target frame time | 16.67ms (60 FPS) | Hard ceiling |
| Particle draw budget | 4ms per frame | 25% of frame time |

### 8.2 Optimization Strategies

1. **SRCALPHA surface reuse**: Create one screen-sized SRCALPHA surface per frame, draw all particles to it, blit once. Currently each animation creates its own SRCALPHA surface (see `FloatingText.draw`, `MagicBurst.draw`). Consolidating saves surface allocation.

2. **Batch similar draws**: Group particles by shape. All circles in one pass, all diamonds in another. Reduces draw state changes.

3. **Early exit**: If alpha < 10, skip draw entirely.

4. **Particle pool** (future): Pre-allocate 200 Particle objects, reuse instead of creating/GC-ing. Not needed initially but available if profiling shows GC pressure.


### 8.3 Measurement

Add a debug overlay (toggled by F3) that shows:
- Current particle count
- Frame time (ms)
- Active animation count

Implementation: `src/ui/debug/perf_overlay.py` -- simple text overlay, reads from `AnimationManager`.


---

## 9. File Manifest

### New Files

| Path | Purpose |
|------|---------|
| `src/ui/animations/particle.py` | Particle value object |
| `src/ui/animations/particle_emitter.py` | ParticleEmitter class |
| `src/ui/animations/particle_configs.py` | All element ParticleConfig constants |
| `src/ui/animations/multi_slash.py` | Enhanced physical attack animation |
| `src/ui/animations/lightning_bolt.py` | Lightning-specific zigzag + sparks |
| `src/ui/animations/combat_intro.py` | Card slide-in transition |
| `src/ui/animations/victory_overlay.py` | Victory sparkle effect |
| `src/ui/animations/defeat_overlay.py` | Defeat darken + pulse |
| `src/ui/animations/boss_intro.py` | Boss entrance dramatic animation |
| `src/ui/components/class_icon.py` | Geometric class icons |
| `src/ui/debug/perf_overlay.py` | Debug particle/FPS counter |
| `tests/ui/test_animations/test_particle.py` | Particle update tests |
| `tests/ui/test_animations/test_particle_emitter.py` | Emitter lifecycle tests |
| `tests/ui/test_animations/test_multi_slash.py` | MultiSlash timing tests |
| `tests/ui/test_components/test_class_icon.py` | Icon dispatch tests |
| `tests/ui/test_components/test_combat_log_enhanced.py` | Log scroll/fade tests |

### Modified Files

| Path | Changes |
|------|---------|
| `src/ui/animations/animation_factory.py` | Element-specific dispatch in `_create_magical_damage` |
| `src/ui/components/character_card.py` | Class icon, position tag, death X |
| `src/ui/components/turn_indicator.py` | Enhanced glow (inner border + corners) |
| `src/ui/components/effect_icons.py` | Stack grouping |
| `src/ui/components/combat_log_panel.py` | LogEntry, scroll, fade, two-color |
| `src/ui/components/action_panel.py` | Cooldown mini-bar |
| `src/ui/components/skill_tooltip.py` | Cooldown line |
| `src/ui/input/menu_state.py` | `cooldown_info` field on MenuOption |
| `src/ui/input/action_menu.py` | Populate cooldown_info |
| `src/ui/scenes/playable_combat_scene.py` | Intro/outro anims, log tags, kill detection |
| `src/ui/scenes/dungeon_map_scene.py` | Node pulse on selection |


---

## 10. Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-29 | Initial visual polish GDD. All 5 systems specified. |
