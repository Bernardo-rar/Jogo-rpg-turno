# Enemy Bestiary — Design Detalhado

## Arquetipos de Monstros

Cada monstro tem um **arquetipo** que define seu papel no combate. Isso guia o `EnemyBehavior` (Strategy) e a composicao dos encounters.

### Definicao dos Arquetipos

| Arquetipo | Papel | Prioridade de Kill | Comportamento Base |
|-----------|-------|--------------------|--------------------|
| **DPS** | Causar dano maximo | Alta (mata rapido) | Foca alvos frageis (backline, menor HP%) |
| **Tank** | Absorver dano, proteger | Baixa (mate os outros primeiro) | Taunt, intercept, se posiciona na frente |
| **Healer** | Manter aliados vivos | Muito Alta (mata PRIMEIRO) | Cura aliado com menor HP%, buffa aliados |
| **Controller** | Controlar o campo | Alta | Aplica CC/debuffs nos alvos mais perigosos |

### Behaviors por Arquetipo

```python
# src/dungeon/enemies/enemy_archetype.py
class EnemyArchetype(Enum):
    DPS = "dps"
    TANK = "tank"
    HEALER = "healer"
    CONTROLLER = "controller"
```

**DPS Behavior:**
- Prioridade: backline > menor HP% > maior dano (ameaca)
- Se tem habilidade AoE e 3+ inimigos agrupados, usa AoE
- Se HP < 30%, tenta matar o alvo mais fraco (desespero)

**Tank Behavior:**
- Prioridade: Taunt no turno 1, intercept aliado mais fragil
- Se nenhum aliado precisa de protecao, ataca frontline
- Enrage trigger: quando ultimo aliado morre, ganha +30% atk

**Healer Behavior:**
- Prioridade: curar aliado com menor HP% (se < 60%)
- Se todos aliados > 80% HP, buffa o DPS mais forte
- Se unico vivo, muda pra modo desesperado (ataque + autocura)
- NUNCA cura a si mesmo se aliado < 40% HP

**Controller Behavior:**
- Prioridade: CC no alvo com mais dano potencial (DPS da party)
- Se target ja tem CC, muda pra debuff (reduz def/atk)
- Se todos targets tem CC/debuff, usa ataque basico

---

## Sistema de Elites

Qualquer monstro nao-boss pode aparecer como **Elite**.

### Mecanica

```python
ELITE_STAT_BUFF_RANGE = (1.30, 1.40)  # 30-40% buff aleatorio

class EliteModifier:
    def apply(self, character: Character) -> Character:
        multiplier = random.uniform(*ELITE_STAT_BUFF_RANGE)
        # Buffa HP, ATK, DEF pelo multiplier
        # Adiciona prefixo "Elite" ao nome
        # Concede habilidade bonus por tier
```

### Regras

| Aspecto | Regra |
|---------|-------|
| Stat buff | Aleatorio entre **30-40%** em HP, ATK e DEF |
| Nome | Prefixo "Elite": "Elite Goblin", "Elite Orc Warrior" |
| Tier 1 elite | +1 habilidade passiva (regen leve, esquiva bonus, resistencia extra) |
| Tier 2 elite | +1 habilidade ativa (ataque AoE, buff aliados, debuff area) |
| Tier 3 elite | +1 ativa + 1 passiva |
| Loot | Drop table 1 tier acima + gold bonus 50% |
| Spawn rate | 15% em salas normais, 100% em salas "Elite" do mapa |

### Habilidades Bonus de Elite (Pool)

**Passivas:**
| Habilidade | Efeito |
|------------|--------|
| Evasion | +10% chance de esquiva |
| Regen | Regen 3% HP max por turno |
| Thorns | Reflete 10% dano recebido |
| Elemental Shield | +25% resistencia ao proprio elemento |
| Fortified | -15% dano fisico recebido |
| Swift | +20% speed |

**Ativas:**
| Habilidade | Efeito | Cooldown |
|------------|--------|----------|
| War Cry | +20% ATK para todos aliados por 2 turnos | 3 turnos |
| Ground Slam | AoE fisico (50% ATK) em todos inimigos | 4 turnos |
| Dark Bolt | Dano magico single target + Silence 1 turno | 3 turnos |
| Enrage | Sacrifica 10% HP, ganha +40% ATK por 2 turnos | 4 turnos |
| Heal Pulse | Cura todos aliados em 15% HP max | 4 turnos |
| Weaken | -20% DEF em 1 alvo por 3 turnos | 3 turnos |

---

## Bestiary Completo

### Tier 1 — Comuns (Floor 1)

#### Goblin
| Campo | Valor |
|-------|-------|
| Arquetipo | DPS |
| HP | Baixo |
| Tipo | Fisico |
| Posicao | FRONT |
| Fraqueza | HOLY, FIRE |
| Resistencia | — |
| Comportamento | Agressivo, foca backline. Se 2+ goblins vivos, ganham +10% atk (pack tactics) |
| Arma | Rusty Dagger (perfuracao, dado baixo) |
| Elite bonus | Evasion (+10% dodge) |
| Loot | Gold baixo, chance de dagger ou pocao menor |

#### Slime
| Campo | Valor |
|-------|-------|
| Arquetipo | Tank |
| HP | Medio |
| Tipo | Magico |
| Posicao | FRONT |
| Fraqueza | LIGHTNING |
| Resistencia | Absorve o ultimo elemento que o atingiu (muda resistencia) |
| Comportamento | Defensivo. Absorve dano, body block. Se HP < 25%, split em 2 mini-slimes (40% HP cada) |
| Arma | Slam (contusao) |
| Elite bonus | Regen (3% HP/turno) |
| Loot | Gold baixo, chance de slime jelly (consumivel: resistencia elemental 1 combate) |

#### Rat Swarm
| Campo | Valor |
|-------|-------|
| Arquetipo | DPS |
| HP | Baixo |
| Tipo | Fisico |
| Posicao | FRONT |
| Fraqueza | FIRE, FORCE |
| Resistencia | Perfuracao (enxame, armas finas passam) |
| Comportamento | Multi-hit: 3 ataques fracos por turno, cada um com 20% chance Poison |
| Arma | Bite x3 (perfuracao, dado muito baixo) |
| Elite bonus | Swift (+20% speed) |
| Loot | Gold minimo, chance de antidoto |

#### Skeleton
| Campo | Valor |
|-------|-------|
| Arquetipo | Tank |
| HP | Medio |
| Tipo | Fisico |
| Posicao | FRONT |
| Fraqueza | HOLY (2x), contusao |
| Resistencia | Perfuracao (ossos, sem orgaos), Poison (imune), Bleed (imune) |
| Comportamento | Defensivo com revive. Quando morre pela primeira vez, revive com 30% HP no proximo turno |
| Arma | Rusty Sword (corte, dado medio) |
| Elite bonus | Fortified (-15% dano fisico) |
| Loot | Gold baixo, chance de osso encantado (consumivel: +DEF 1 combate) |

#### Mushroom
| Campo | Valor |
|-------|-------|
| Arquetipo | Controller |
| HP | Baixo |
| Tipo | Magico |
| Posicao | BACK |
| Fraqueza | FIRE |
| Resistencia | Poison (imune) |
| Comportamento | Spore Cloud: AoE que aplica Poison + 30% chance Confusion. Prioriza alvos sem debuff |
| Arma | Spore Attack (magico, EARTH) |
| Elite bonus | Elemental Shield (+25% resistencia EARTH) |
| Loot | Gold baixo, chance de cogumelo curativo (consumivel: cura + limpa Poison) |

---

### Tier 2 — Intermediarios (Floor 2)

#### Orc Warrior
| Campo | Valor |
|-------|-------|
| Arquetipo | Tank |
| HP | Alto |
| Tipo | Fisico |
| Posicao | FRONT |
| Fraqueza | PSYCHIC |
| Resistencia | Contusao |
| Comportamento | Taunt no turno 1. Protege aliados interceptando ataques. Enrage quando ultimo aliado morre (+50% atk, +30% speed) |
| Arma | War Axe (corte, dado alto) |
| Elite bonus | Thorns (10% reflect) |
| Loot | Gold medio, chance de axe ou armadura media |

#### Wraith
| Campo | Valor |
|-------|-------|
| Arquetipo | Controller |
| HP | Medio |
| Tipo | Magico |
| Posicao | BACK |
| Fraqueza | HOLY, FIRE |
| Resistencia | Imune a fisico normal (precisa magico ou elemental pra acertar) |
| Comportamento | Drena mana com ataque principal. Aplica Silence em casters. Se party sem mana, muda pra drain HP |
| Arma | Soul Drain (magico, DARKNESS) |
| Elite bonus | Evasion (+10% dodge, ethereal) |
| Loot | Gold medio, chance de anel de sombra (acessorio) ou pocao mana |

#### Harpy
| Campo | Valor |
|-------|-------|
| Arquetipo | DPS |
| HP | Medio |
| Tipo | Misto |
| Posicao | BACK (voando) |
| Fraqueza | ICE, EARTH |
| Resistencia | EARTH (imune a ground effects) |
| Comportamento | Dodge alto (voo). Sonic Screech: AoE que reduz precisao da party. Dive Attack: dano forte single target |
| Arma | Talons (perfuracao) + Sonic Screech (magico, FORCE) |
| Elite bonus | Swift (+20% speed) |
| Loot | Gold medio, chance de pena encantada (consumivel: +speed 1 combate) |

#### Goblin Shaman
| Campo | Valor |
|-------|-------|
| Arquetipo | Healer |
| HP | Baixo |
| Tipo | Magico |
| Posicao | BACK |
| Fraqueza | FORCE, FIRE |
| Resistencia | — |
| Comportamento | Cura aliado com menor HP%. Se todos > 80%, buffa ATK do aliado mais forte. Fraco sozinho, muda pra dano magico fraco |
| Arma | Bone Staff (magico, EARTH) |
| Elite bonus | Heal Pulse (cura AoE aliados 15% HP, CD 4) |
| Loot | Gold medio, chance de totem curativo (consumivel) ou staff |

#### Dark Mage
| Campo | Valor |
|-------|-------|
| Arquetipo | DPS |
| HP | Baixo |
| Tipo | Magico |
| Posicao | BACK |
| Fraqueza | FORCE |
| Resistencia | DARKNESS |
| Comportamento | Dano magico forte single target. Alterna entre Dark Bolt (dano) e Curse (debuff -DEF). Se HP < 30%, casta AoE desesperado |
| Arma | Dark Staff (magico, DARKNESS) |
| Elite bonus | Dark Bolt ativo extra (dano + Silence) |
| Loot | Gold medio, chance de grimorio ou pocao mana grande |

---

### Tier 3 — Perigosos (Floor 3)

#### Mimic
| Campo | Valor |
|-------|-------|
| Arquetipo | DPS |
| HP | Medio |
| Tipo | Misto |
| Posicao | FRONT |
| Fraqueza | FORCE |
| Resistencia | Varia (muda a cada 3 turnos) |
| Comportamento | **Surprise round**: primeiro turno, party nao age (pego de surpresa). Ataque forte com Chomp (perfuracao + contusao). Pode engolir um personagem (stun 1 turno, dano continuo) |
| Arma | Chomp (misto, dado alto) |
| Elite bonus | Fortified + Enrage |
| Loot | Gold alto (mimics guardam tesouro), loot garantido tier 2-3 |

#### Basilisk
| Campo | Valor |
|-------|-------|
| Arquetipo | Controller |
| HP | Alto |
| Tipo | Magico |
| Posicao | FRONT |
| Fraqueza | ICE |
| Resistencia | EARTH, Poison (imune) |
| Comportamento | Petrifying Gaze: stun 2 turnos (single target, save de WIS). Veneno forte em ataque basico. Prioriza petrificar o healer/DPS da party |
| Arma | Fangs (perfuracao, EARTH) + Gaze (magico) |
| Elite bonus | Elemental Shield (EARTH) + Ground Slam |
| Loot | Gold alto, chance de olho de basilisco (reliquia material?) ou arma envenenada |

#### Vampire
| Campo | Valor |
|-------|-------|
| Arquetipo | DPS |
| HP | Alto |
| Tipo | Misto |
| Posicao | FRONT |
| Fraqueza | HOLY, FIRE |
| Resistencia | DARKNESS, Bleed (imune) |
| Comportamento | Life steal: cura 30% do dano causado. Fica mais forte conforme rouba HP (stacking buff +5% atk por hit). Charm: 20% chance de confudir um alvo |
| Arma | Claws (corte, DARKNESS) + Bite (perfuracao, life steal) |
| Elite bonus | Regen + Enrage |
| Loot | Gold alto, chance de capa vampirica (acessorio) ou arma com life steal |

#### Lich Acolyte
| Campo | Valor |
|-------|-------|
| Arquetipo | Healer |
| HP | Medio |
| Tipo | Magico |
| Posicao | BACK |
| Fraqueza | HOLY, FORCE |
| Resistencia | DARKNESS, Poison (imune), Bleed (imune) |
| Comportamento | Revive: pode trazer de volta 1 monstro morto com 40% HP (CD 5 turnos). Cura undead aliados. Se sozinho, casta Dark Bolt + autocura |
| Arma | Necro Staff (magico, DARKNESS) |
| Elite bonus | Heal Pulse + Fortified |
| Loot | Gold alto, chance de grimorio necromante ou reliquia |

#### Elemental
| Campo | Valor |
|-------|-------|
| Arquetipo | Controller |
| HP | Alto |
| Tipo | Magico |
| Posicao | FRONT |
| Fraqueza | Oposto ao elemento atual |
| Resistencia | Imune ao proprio elemento. Muda a cada 2 turnos: FIRE → ICE → LIGHTNING → EARTH → loop |
| Comportamento | Ataque do elemento atual. AoE quando muda de elemento (burst de transicao). Aplica aura elemental que pode causar reactions |
| Arma | Elemental Slam (magico, elemento variavel) |
| Elite bonus | Elemental Shield + War Cry |
| Loot | Gold alto, chance de cristal elemental (item que adiciona elemento a arma) |

---

## Bosses

### Floor 1 — Goblin King

**Tier**: Boss
**Arquetipo**: DPS/Tank hibrido
**HP**: Muito Alto
**Fraqueza**: HOLY, FIRE

| Fase | HP Range | Comportamento |
|------|----------|---------------|
| Fase 1 | 100%-50% | Invoca 2 goblins a cada 3 turnos. Ataque fisico forte single target. Grito de guerra: buffa goblins invocados |
| Fase 2 | 50%-0% | Para de invocar. Enrage: +50% atk, +30% speed. Ataques AoE com Cleave |

**Mecanica especial**: Matar goblins invocados da buff temporario ao boss (+10% DEF por goblin morto, dura 2 turnos). Estrategia: ignorar goblins ou matar rapido antes do buff stackar.

### Floor 2 — Ancient Golem

**Tier**: Boss
**Arquetipo**: Tank
**HP**: Extremo
**Fraqueza**: LIGHTNING, WATER

| Fase | HP Range | Comportamento |
|------|----------|---------------|
| Fase 1 | 100%-40% | Defesa absurda. Ataca lento mas forte. Core exposto a cada 4 turnos (recebe 2x dano por 1 turno) |
| Fase 2 | 40%-0% | Quebra em 2 golems menores (50% stats cada). Se um morrer, o outro enrage |

**Mecanica especial**: Stomp AoE que empurra frontline pra backline. Jogador precisa reposicionar.

### Floor 3 — Lich Lord

**Tier**: Boss Final
**Arquetipo**: Controller/Healer
**HP**: Muito Alto
**Fraqueza**: HOLY, FORCE (phylactery fraca a FIRE)

| Fase | HP Range | Comportamento |
|------|----------|---------------|
| Fase 1 | 100%+ | Magias fortes. Phylactery separada (objeto com HP proprio) |
| Fase 2 | Phylactery viva 5+ turnos | Full heal + buff massivo. Phylactery regen leve |
| Fase 3 | Phylactery destruida | Desespero: +50% dano magico, -30% DEF |

**Mecanica especial**: Revive monstros de salas anteriores da run como undead (70% stats originais). Maximo 2 revividos por vez.

---

## Composicao de Encounters

### Templates de Encounter por Dificuldade

```
Facil (salas iniciais):
  - 3x DPS (tier do floor)
  - 2x DPS + 1x Tank

Medio (salas intermediarias):
  - 1x Tank + 2x DPS
  - 1x Healer + 2x DPS
  - 2x Controller + 1x DPS

Dificil (salas pre-boss):
  - 1x Tank + 1x Healer + 2x DPS
  - 1x Tank + 1x Controller + 2x DPS
  - 1x Healer + 1x Controller + 2x DPS

Elite (salas de elite no mapa):
  - 1x Elite (qualquer) + 2x normais
  - 1x Tank + 1x Healer + 1x Controller + 1x DPS (todos elite)
```

### Regras de Geracao

- Nunca gerar encounter de 1 monstro (exceto elite solo ou mini-boss)
- Maximo 5 monstros por encounter (performance + balance)
- Tier dos monstros = tier do floor, com +-1 de variacao
- Encounters de elite garantem pelo menos 1 monstro elite
- Boss sempre sozinho (invoca adds pela mecanica)

---

## Dados: `data/dungeon/enemies/`

Cada monstro tem seu JSON:

```json
{
  "id": "goblin",
  "name": "Goblin",
  "tier": 1,
  "archetype": "dps",
  "class_modifiers": {
    "hit_dice": 6, "mod_hp_flat": 0, "mod_hp_mult": 3,
    "mana_multiplier": 0,
    "mod_atk_physical": 4, "mod_atk_magical": 1,
    "mod_def_physical": 2, "mod_def_magical": 1,
    "regen_hp_mod": 1, "regen_mana_mod": 0
  },
  "base_attributes": {
    "STR": 8, "DEX": 14, "CON": 6, "INT": 4, "WIS": 4, "CHA": 3, "MIND": 2
  },
  "elemental_profile": "fire_weak",
  "behavior": "aggressive_backline",
  "position": "FRONT",
  "loot_table": "tier1_common",
  "weapon_template": "rusty_dagger",
  "elite_bonus_ability": "evasion_10pct",
  "special_traits": ["pack_tactics"]
}
```
