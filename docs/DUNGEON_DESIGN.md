# Dungeon Roguelite - Design Document

## Visao Geral

Modo roguelite com runs procedurais: party de 4 personagens enfrenta sequencia de salas (combates, eventos, shops) ate o boss final. Morte = reset, mas meta-progressao persiste entre runs.

O sistema **nao toca no core/**. Fica em `src/dungeon/`, importando do core como consumidor.

---

## Documentos Detalhados

Cada sistema tem seu proprio doc com design completo:

| Sistema | Documento | Descricao |
|---------|-----------|-----------|
| Mapa Ramificado | [BRANCHING_MAP.md](dungeon/BRANCHING_MAP.md) | Estrutura de floor com caminhos, tipos de sala, navegacao |
| Bestiary | [BESTIARY.md](dungeon/BESTIARY.md) | 15 monstros com arquetipos (DPS/Tank/Healer/Controller), elites, bosses |
| Loot | [LOOT_SYSTEM.md](dungeon/LOOT_SYSTEM.md) | Drop tables, armas procedurais + predefinidas, consumiveis, raridade |
| Economia | [ECONOMY.md](dungeon/ECONOMY.md) | Curva de gold, precos, balanceamento, tensao economica |
| Rest Rooms | [REST_ROOMS.md](dungeon/REST_ROOMS.md) | Acoes de descanso (heal, meditar, afiar, forjar, etc.) |
| Run Modifiers | [RUN_MODIFIERS.md](dungeon/RUN_MODIFIERS.md) | Mutadores de dificuldade, economia, restricao, chaos |
| Party Selection | [PARTY_SELECTION.md](dungeon/PARTY_SELECTION.md) | Selecao de 4 classes, sinergias, desbloqueio, posicionamento |
| Class Colors | [CLASS_COLORS.md](dungeon/CLASS_COLORS.md) | Cor tematica de cada classe (modular via JSON) |

---

## Arquitetura

```
src/
  core/              # NAO MUDA — regras puras do RPG
  dungeon/           # NOVO — modo roguelite
    run/             # Estado da run (seed, floor, gold, reliquias)
    rooms/           # Gerador de salas, tipos, layout de floor
    enemies/         # Bestiary, enemy factory, boss AI
    events/          # Eventos entre salas (escolhas)
    shop/            # Loja, precos, inventario da shop
    relics/          # Reliquias (passivos de run)
    reactions/       # Elemental reactions (combos entre elementos)
    loot/            # Drop tables, raridades, rewards
    meta/            # Meta-progressao entre runs
  ui/                # Visual (ja existe)
```

**Regra de dependencia**: `dungeon/` importa de `core/`, mas `core/` NUNCA importa de `dungeon/`. Mesma regra unidirecional que `core/` → `ui/`.

**Por que separar?** O `core/` e o sistema de RPG generico. Amanha pode existir:
- Arena PvP (usa core, sem dungeon)
- Campanha linear com historia (usa core, dungeon diferente)
- Boss rush mode (usa core + so bosses)

---

## Fase 3.0 — Elemental Reactions

### Motivacao
O sistema elemental ja existe com 10 elementos, fraquezas/resistencias e on-hit effects. Mas nao ha interacao ENTRE elementos. Reactions criam depth tatico: a composicao da party importa, e combos recompensam planejamento.

### Conceito: Aura + Trigger
- **Aura**: primeiro elemento aplicado ao alvo (ex: FIRE via Burn)
- **Trigger**: segundo elemento atinge alvo que ja tem aura
- **Reaction**: efeito especial que consome a aura

### Tabela de Reactions

| Aura | Trigger | Reaction | Efeito |
|------|---------|----------|--------|
| FIRE | ICE | **Melt** | 1.5x dano do trigger, remove ambos |
| ICE | FIRE | **Reverse Melt** | 1.3x dano do trigger |
| WATER | LIGHTNING | **Electrocute** | Dano AoE (50% do trigger) em todos inimigos |
| LIGHTNING | WATER | **Electrocharge** | Stun 1 turno no alvo |
| FIRE | EARTH | **Ite Glass** | -30% physical_defense no alvo por 3 turnos |
| EARTH | FIRE | **Magma** | DoT forte (2x burn) por 2 turnos |
| ICE | EARTH | **Permafrost** | Congela por 2 turnos (CC forte) |
| HOLY | DARKNESS | **Purify** | Remove TODOS debuffs/ailments do alvo + burst heal |
| DARKNESS | HOLY | **Eclipse** | Dano maximo entre holy e darkness * 1.5 |
| FIRE | DARKNESS | **Shadowflame** | DoT que ignora defesa magica por 4 turnos |
| PSYCHIC | LIGHTNING | **Overload** | Drena 30% mana + confusao |
| WATER | ICE | **Shatter** | Congela + proximo hit fisico da 2x dano |
| EARTH | NATURE | **Overgrowth** | Regen party inteira por 3 turnos |
| FORCE | qualquer | **Detonate** | Consome aura, 2x dano do elemento consumido |

### Implementacao Tecnica

```python
# src/dungeon/reactions/reaction_type.py
class ReactionType(Enum):
    MELT = "melt"
    ELECTROCUTE = "electrocute"
    SHATTER = "shatter"
    # ...

# src/dungeon/reactions/reaction_table.py
# Dict[(aura: ElementType, trigger: ElementType)] -> ReactionType
REACTION_TABLE: dict[tuple[ElementType, ElementType], ReactionType] = {
    (ElementType.FIRE, ElementType.ICE): ReactionType.MELT,
    (ElementType.WATER, ElementType.LIGHTNING): ReactionType.ELECTROCUTE,
    # ...
}

# src/dungeon/reactions/reaction_resolver.py
class ReactionResolver:
    """Checa se alvo tem aura elemental, resolve reaction se trigger bate."""
    def try_react(self, target: Character, trigger_element: ElementType,
                  trigger_damage: int) -> ReactionResult | None: ...
```

**Dados**: `data/dungeon/reactions.json` com multiplicadores e duracoes (data-driven, nao hardcoded).

**Integracao com combat**: O `ReactionResolver` e chamado APOS o dano elemental ser aplicado. Ele checa se o alvo tem um ailment/effect com tag elemental (a "aura") e se o elemento do ataque atual forma uma reaction.

---

## Fase 3.1 — Enemy Bestiary

### Motivacao
Inimigos com identidade propria sao mais divertidos que "Character com stats diferentes". Cada monstro deve ter comportamento, fraquezas e visual distintos.

### Arquitetura

Monstros **NAO sao subclasses de Character**. Sao Character com:
1. `ClassModifiers` especificos (carregados de JSON)
2. `ElementalProfile` com fraquezas/resistencias tematicas
3. `EnemyBehavior` (Strategy pattern) que decide acoes
4. `EnemyArchetype` — papel tatico no combate

```python
# src/dungeon/enemies/enemy_archetype.py
class EnemyArchetype(Enum):
    DPS = "dps"              # Dano alto, HP baixo, foca em matar rapido
    TANK = "tank"            # HP/defesa altos, protege aliados, taunt
    HEALER = "healer"        # Cura aliados, prioridade de kill alta
    CONTROLLER = "controller" # CC, debuffs, disrupt a party

# src/dungeon/enemies/enemy_factory.py
class EnemyFactory:
    """Cria Character configurado como monstro a partir de template JSON."""
    def create(self, template_id: str, level: int,
               is_elite: bool = False) -> Character: ...

# src/dungeon/enemies/enemy_behavior.py (Protocol)
class EnemyBehavior(Protocol):
    """Strategy que decide o que o monstro faz no turno."""
    def choose_action(self, actor: Character,
                      allies: list[Character],
                      enemies: list[Character]) -> TurnAction: ...
```

### Arquetipos de Monstros

Cada monstro tem um **arquetipo** que define seu papel no combate. Isso guia tanto o `EnemyBehavior` quanto a composicao dos encounters:

| Arquetipo | Papel | Prioridade de Kill | Comportamento Base |
|-----------|-------|--------------------|--------------------|
| **DPS** | Causar dano maximo | Alta (mata rapido) | Foca alvos frageis (backline, menor HP) |
| **Tank** | Absorver dano, proteger | Baixa (mate os outros primeiro) | Taunt, se posiciona na frente, intercept |
| **Healer** | Manter aliados vivos | Muito Alta (mata PRIMEIRO) | Cura aliado com menor %, buff aliados |
| **Controller** | Controlar o campo | Alta | Aplica CC/debuffs nos alvos mais perigosos |

**Composicao de Encounters por Arquetipo:**
- Encounter facil: 2-3 DPS
- Encounter medio: 1 Tank + 2 DPS ou 1 Healer + 2 DPS
- Encounter dificil: 1 Tank + 1 Healer + 2 DPS
- Encounter elite: 1 Tank + 1 Healer + 1 Controller + 1 DPS

### Sistema de Elites

Qualquer monstro nao-boss pode aparecer como **Elite**. Elites sao versoes mais fortes com loot melhor.

```python
# src/dungeon/enemies/elite.py
ELITE_STAT_BUFF_RANGE = (1.30, 1.40)  # 30-40% buff aleatorio

class EliteModifier:
    """Aplica buff de elite a um monstro."""
    def apply(self, character: Character) -> Character:
        multiplier = random.uniform(*ELITE_STAT_BUFF_RANGE)
        # Buffa HP, ATK, DEF em multiplier
        # Adiciona prefixo "Elite" ao nome
        # Pode ganhar 1 habilidade extra (por tier)
        ...
```

**Regras de Elites:**
- Buff aleatorio entre **30-40%** em HP, ATK e DEF
- Recebem prefixo visual: "Elite Goblin", "Elite Orc Warrior"
- **Tier 1 elite**: +1 habilidade passiva (ex: regen leve, esquiva bonus)
- **Tier 2 elite**: +1 habilidade ativa extra (ex: ataque AoE, buff aliados)
- **Tier 3 elite**: +1 habilidade ativa + 1 passiva
- **Loot**: Drop table 1 tier acima do normal + gold bonus 50%
- **Spawn rate**: 15% em salas normais, 100% em salas de elite no mapa

### Bestiary Inicial (15 monstros)

**Tier 1 — Comuns (Floor 1)**
| Monstro | Arquetipo | HP | Tipo | Fraqueza | Comportamento |
|---------|-----------|-----|------|----------|---------------|
| **Goblin** | DPS | Baixo | Fisico | HOLY, FIRE | Agressivo, foca backline |
| **Slime** | Tank | Medio | Magico | LIGHTNING | Absorve elemento atacado, muda resistencia |
| **Rat Swarm** | DPS | Baixo | Fisico | FIRE, FORCE | Multi-hit fraco (3 ataques), aplica Poison |
| **Skeleton** | Tank | Medio | Fisico | HOLY(2x), contusao | Resistente a perfuracao, revive 1x com 30% HP |
| **Mushroom** | Controller | Baixo | Magico | FIRE | Spore cloud: AoE Poison + Confusion chance |

**Tier 2 — Intermediarios (Floor 2)**
| Monstro | Arquetipo | HP | Tipo | Fraqueza | Comportamento |
|---------|-----------|-----|------|----------|---------------|
| **Orc Warrior** | Tank | Alto | Fisico | PSYCHIC | Protege aliados (taunt), enrage ao perder aliados |
| **Wraith** | Controller | Medio | Magico | HOLY, FIRE | Imune a fisico normal, drena mana |
| **Harpy** | DPS | Medio | Misto | ICE, EARTH | Voa (dodge alto), ataque sonoro AoE |
| **Goblin Shaman** | Healer | Baixo | Magico | FORCE, FIRE | Cura aliados, buffa ataque, fraco sozinho |
| **Dark Mage** | DPS | Baixo | Magico | FORCE | Backline, casta debuffs + dano magico forte |

**Tier 3 — Perigosos (Floor 3)**
| Monstro | Arquetipo | HP | Tipo | Fraqueza | Comportamento |
|---------|-----------|-----|------|----------|---------------|
| **Mimic** | DPS | Medio | Misto | FORCE | Surprise round, parece bau de loot |
| **Basilisk** | Controller | Alto | Magico | ICE | Petrify (stun longo), veneno forte |
| **Vampire** | DPS | Alto | Misto | HOLY, FIRE | Life steal, fica mais forte com HP roubado |
| **Lich Acolyte** | Healer | Medio | Magico | HOLY, FORCE | Revive monstros mortos, cura undead |
| **Elemental** | Controller | Alto | Magico | Oposto | Muda elemento a cada 2 turnos |

> **Nota**: Golem foi movido para boss (Ancient Golem). Harpy, Wraith e Dark Mage tiveram arquetipos ajustados. Goblin Shaman e Lich Acolyte adicionados como healers (antes nao havia healers no bestiary).

### Dados: `data/dungeon/enemies/`

```json
// data/dungeon/enemies/goblin.json
{
  "id": "goblin",
  "name": "Goblin",
  "tier": 1,
  "archetype": "dps",
  "class_modifiers": {
    "hit_dice": 6, "vida_mod": 0, "mod_hp": 3,
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
  "elite_bonus_ability": "evasion_10pct"
}
```

### Boss Design (3 bosses iniciais)

**Floor 1 Boss — Goblin King**
- Fase 1 (100%-50% HP): Invoca 2 goblins a cada 3 turnos, ataque fisico forte
- Fase 2 (50%-0% HP): Para de invocar, enrage (+50% atk, +30% speed), ataques AoE
- Fraqueza: HOLY, FIRE
- Mecanica especial: Matar os goblins invocados da buff temporario ao boss (+10% def cada)

**Floor 2 Boss — Ancient Golem**
- Fase 1: Defesa absurda, ataca lento mas forte. Core exposto a cada 4 turnos (2x dano recebido)
- Fase 2 (40% HP): Quebra em 2 golems menores, cada um com 50% dos stats
- Fraqueza: LIGHTNING, WATER
- Mecanica especial: Stomp AoE que empurra frontline pra backline

**Floor 3 Boss — Lich Lord**
- Fase 1: Casta magias fortes, tem phylactery (objeto separado com HP proprio)
- Fase 2: Se phylactery nao destruida em 5 turnos, full heal + buff
- Fase 3 (phylactery destruida): Desespero, ataques mais fortes mas defesa cai
- Fraqueza: HOLY, FORCE (phylactery fraca a FIRE)
- Mecanica especial: Revive monstros de salas anteriores como undead (mais fracos)

---

## Fase 3.2 — Dungeon Run (Estrutura)

### Conceito
Uma run = sequencia de 3 floors, cada floor com salas. Salas sao geradas proceduralmente a partir de templates.

### Estrutura de Floor

```
Floor 1 (Facil):
  Sala 1: Combate (Tier 1)
  Sala 2: Combate (Tier 1) ou Evento
  Sala 3: Evento ou Shop
  Sala 4: Mini-boss ou Combate (Tier 1 elite)
  Sala 5: BOSS

Floor 2 (Medio):
  Sala 1: Combate (Tier 2)
  Sala 2: Combate (Tier 1+2 mix)
  Sala 3: Evento
  Sala 4: Shop
  Sala 5: Combate (Tier 2 elite)
  Sala 6: Evento
  Sala 7: BOSS

Floor 3 (Hard):
  Sala 1: Combate (Tier 2+3 mix)
  Sala 2: Evento
  Sala 3: Combate (Tier 3)
  Sala 4: Shop
  Sala 5: Combate (Tier 3 elite)
  Sala 6: Evento (risco alto / recompensa alta)
  Sala 7: Combate (Tier 3)
  Sala 8: BOSS FINAL
```

### Estado da Run

```python
# src/dungeon/run/run_state.py
@dataclass
class RunState:
    seed: int                          # Seed pra reproducibilidade
    party: list[Character]             # Party de 4
    current_floor: int                 # 1, 2 ou 3
    current_room: int                  # Indice da sala no floor
    gold: int                          # Moeda da run
    relics: list[Relic]                # Reliquias ativas (max 5)
    inventory: Inventory               # Consumiveis coletados
    rooms_cleared: int                 # Total de salas limpas
    enemies_killed: int                # Total de monstros mortos
    is_over: bool                      # Run acabou (morte ou vitoria)
    victory: bool                      # Ganhou ou perdeu

# src/dungeon/run/run_manager.py
class RunManager:
    """Orquestra o fluxo da run: gera floors, avanca salas, aplica rewards."""
    def start_run(self, party: list[Character], seed: int | None) -> RunState: ...
    def advance_to_next_room(self, state: RunState) -> Room: ...
    def complete_room(self, state: RunState, result: RoomResult) -> RunState: ...
    def is_run_over(self, state: RunState) -> bool: ...
```

### Tipos de Sala

```python
class RoomType(Enum):
    COMBAT = "combat"           # Batalha normal
    ELITE_COMBAT = "elite"      # Batalha dificil, loot melhor
    BOSS = "boss"               # Boss fight
    EVENT = "event"             # Escolha narrativa
    SHOP = "shop"               # Comprar itens/reliquias
    REST = "rest"               # Descansar (heal parcial)
    TREASURE = "treasure"       # Bau com loot garantido
```

---

## Fase 3.3 — Eventos Entre Salas

### Design de Eventos
Cada evento tem 2-3 escolhas com tradeoffs. Nunca existe escolha "obviamente melhor".

### Eventos Iniciais (10)

**1. Altar Sangrento**
- Opcao A: Sacrifica 25% HP de um membro → ganha reliquia aleatoria
- Opcao B: Ignora → nada acontece

**2. Fonte Misteriosa**
- Opcao A: Bebe → 60% chance full heal, 40% chance envenenamento (DoT forte)
- Opcao B: Enche frascos → ganha 2 pocoes de cura menores

**3. Mercador Shady**
- Opcao A: Compra item misterioso (preco alto) → pode ser reliquia rara OU lixo
- Opcao B: Ameaca → 50% chance ele foge e dropa gold, 50% chance combate surpresa

**4. Ferreiro Errante**
- Opcao A: Paga gold → adiciona elemento aleatorio a uma arma do grupo
- Opcao B: Paga mais gold → escolhe o elemento

**5. Prisioneiro**
- Opcao A: Liberta → aliado NPC temporario pro proximo combate (monstro domesticado)
- Opcao B: Ignora → encontra bau trancado com loot

**6. Encruzilhada**
- Opcao A: Caminho facil → sala de combate tier -1, pouco loot
- Opcao B: Caminho perigoso → sala de combate tier +1, loot dobrado
- Opcao C: Caminho oculto (precisa Rogue na party) → sala de tesouro

**7. Treinador de Guerra**
- Opcao A: Treino → um membro ganha +1 atributo permanente (aleatorio)
- Opcao B: Sparring → combate 1v1 com treinador, se ganhar +2 atributo escolhido

**8. Pedra Elemental**
- Toca a pedra → proximo combate, party inteira ganha aura de elemento aleatorio
- Se o elemento for o mesmo de um monstro da proxima sala → reaction garantida

**9. Sacrificio ao Obelisco**
- Opcao A: Sacrifica reliquia → ganha reliquia de tier superior
- Opcao B: Sacrifica gold → ganha reliquia aleatoria
- Opcao C: Nao sacrifica → monstros do proximo combate ficam +20% stats

**10. Visao do Oraculo**
- Revela as proximas 2 salas (tipo e tier dos monstros)
- Opcao A: Paga gold → tambem revela fraquezas dos monstros
- Opcao B: Gratis → so ve os tipos de sala

---

## Fase 3.4 — Sistema de Reliquias

### Conceito
Reliquias sao passivos que duram a run inteira. Maximo 5 por run. Escolher quais manter e quais descartar e parte da estrategia.

### Raridades
- **Common**: Bonus pequeno, sem downside
- **Uncommon**: Bonus medio, pode ter condicao
- **Rare**: Bonus forte, pode ter downside
- **Legendary**: Game-changing, downside significativo

### Reliquias Iniciais (20)

**Common (8)**
| Reliquia | Efeito |
|----------|--------|
| Botas de Ferro | +10% speed para frontline |
| Amuleto de Cura | Pocoes curam +25% |
| Pedra de Afiacao | +5% dano fisico |
| Cristal Arcano | +5% dano magico |
| Escudo de Espinhos | Reflete 5% do dano recebido |
| Bolsa de Moedas | +20% gold de combate |
| Anel de Vitalidade | +10% HP max para todos |
| Pergaminho de Protecao | +10% defesa no primeiro turno de cada combate |

**Uncommon (6)**
| Reliquia | Efeito |
|----------|--------|
| Ampulheta Quebrada | Primeiro turno de cada combate = turno extra gratis |
| Olho do Observador | Revela tipo da proxima sala |
| Luva do Alquimista | Consumiveis 30% chance de nao gastar |
| Totem de Resiliencia | Imune ao primeiro debuff de cada combate |
| Mascara do Berserker | +20% atk quando abaixo de 50% HP |
| Flauta Encantada | Buffs duram +1 turno |

**Rare (4)**
| Reliquia | Efeito | Downside |
|----------|--------|----------|
| Vela Sangrenta | +15% dano total | -3% HP max por sala |
| Coroa de Espinhos | Reflete 15% dano como DARKNESS | -10% healing recebido |
| Grimorio Proibido | Reactions causam 2x dano | +10% dano recebido de magias |
| Bracelete Vampirico | 10% life steal em todo dano | Pocoes curam 50% menos |

**Legendary (2)**
| Reliquia | Efeito | Downside |
|----------|--------|----------|
| Coracao do Phoenix | Party revive 1x por combate com 25% HP | Revividos ficam com -30% stats ate fim do combate |
| Orbe do Caos | Todo ataque tem elemento aleatorio + reaction chance | Nao pode escolher alvo (aleatorio) |

### Implementacao

```python
# src/dungeon/relics/relic.py
@dataclass(frozen=True)
class Relic:
    id: str
    name: str
    description: str
    rarity: RelicRarity
    effects: tuple[RelicEffect, ...]     # Passivos positivos
    downsides: tuple[RelicEffect, ...]   # Custos

# src/dungeon/relics/relic_effect.py (Protocol)
class RelicEffect(Protocol):
    """Efeito passivo de uma reliquia. Pode modificar stats, combat events, etc."""
    def on_combat_start(self, party: list[Character]) -> None: ...
    def on_turn_start(self, actor: Character) -> None: ...
    def on_damage_dealt(self, damage: int, element: ElementType | None) -> int: ...
    def on_damage_taken(self, damage: int) -> int: ...
    def on_heal(self, amount: int) -> int: ...
    def on_room_clear(self, state: RunState) -> None: ...
```

**Dados**: `data/dungeon/relics.json`

---

## Fase 3.5 — Shop

### Conceito
Shop aparece 1x por floor. Vende consumiveis, armas, e 1 reliquia.

### Economia
- Gold ganho por combate: 10-30 (tier 1), 20-50 (tier 2), 40-80 (tier 3)
- Gold ganho por boss: 100, 200, 300
- Precos de consumiveis: 10-30 gold
- Precos de armas: 50-150 gold
- Precos de reliquias: 80 (common) / 150 (uncommon) / 250 (rare)

### Inventario da Shop
Gerado proceduralmente por floor:
- 3-5 consumiveis (pocoes HP, pocoes Mana, antidotos, buffs temporarios)
- 1-2 armas (tier do floor, pode ter elemento)
- 1 reliquia (raridade aleatoria, weighted por floor)

```python
# src/dungeon/shop/shop.py
class Shop:
    def __init__(self, items: list[ShopItem], relic: Relic | None): ...
    def buy(self, state: RunState, item_index: int) -> RunState: ...
    def can_afford(self, state: RunState, item_index: int) -> bool: ...
```

---

## Fase 3.6 — Meta-progressao

### Conceito
Recompensas entre runs que expandem o pool de conteudo disponivel. NAO power creep — desbloqueia opcoes, nao poder.

### Desbloqueios
- **Classes**: Comeca com 4 classes disponiveis. Cada run completada (mesmo perdendo) desbloqueia 1 classe nova
- **Reliquias**: Pool inicial de 10 reliquias. Boss kills desbloqueiam novas no pool
- **Bestiary**: Registro de monstros encontrados (flavor text, stats, fraquezas)
- **Achievements**: "Mate 100 goblins", "Complete floor 3 sem usar pocoes", etc.

### Dados Persistentes

```python
# src/dungeon/meta/save_data.py
@dataclass
class SaveData:
    unlocked_classes: set[str]       # IDs das classes desbloqueadas
    unlocked_relics: set[str]        # IDs das reliquias no pool
    bestiary_seen: set[str]          # IDs dos monstros encontrados
    achievements: set[str]           # IDs dos achievements completados
    total_runs: int
    total_victories: int
    total_gold_earned: int
    best_floor_reached: int
```

Persistencia: JSON local em `saves/` (fora do `data/` que e game design).

---

## Roadmap de Tasks

### Fase 3.0 — Elemental Reactions

- **Task 3.0.1**: ReactionType enum + REACTION_TABLE lookup
- **Task 3.0.2**: ReactionResolver (checa aura no alvo, resolve reaction)
- **Task 3.0.3**: Efeitos individuais de cada reaction (Melt, Electrocute, Shatter, etc.)
- **Task 3.0.4**: Integracao com combat engine (hook pos-dano elemental)
- **Task 3.0.5**: Dados JSON (`data/dungeon/reactions.json`)
- **Task 3.0.6**: Testes de integracao (reaction durante combate real)

### Fase 3.1 — Enemy Bestiary → [BESTIARY.md](dungeon/BESTIARY.md)

- **Task 3.1.1**: EnemyArchetype enum + EnemyTemplate dataclass + EnemyFactory
- **Task 3.1.2**: EnemyBehavior Protocol + 4 behaviors por arquetipo (dps, tank, healer, controller)
- **Task 3.1.3**: 5 monstros Tier 1 (Goblin, Slime, Rat Swarm, Skeleton, Mushroom)
- **Task 3.1.4**: 5 monstros Tier 2 (Orc Warrior, Wraith, Harpy, Goblin Shaman, Dark Mage)
- **Task 3.1.5**: 5 monstros Tier 3 (Mimic, Basilisk, Vampire, Lich Acolyte, Elemental)
- **Task 3.1.6**: EliteModifier (30-40% stat buff, habilidades bonus, loot boost)
- **Task 3.1.7**: Boss 1 — Goblin King (fases, invocacao)
- **Task 3.1.8**: Boss 2 — Ancient Golem (core exposto, split)
- **Task 3.1.9**: Boss 3 — Lich Lord (phylactery, revive)
- **Task 3.1.10**: Encounter composer (gera grupos por dificuldade + arquetipos)
- **Task 3.1.11**: EnemyTurnHandler (integra behaviors com CombatEngine)

### Fase 3.2 — Dungeon Structure → [BRANCHING_MAP.md](dungeon/BRANCHING_MAP.md)

- **Task 3.2.1**: MapNode dataclass + RoomType enum
- **Task 3.2.2**: FloorMap + MapGenerator (mapa ramificado com camadas)
- **Task 3.2.3**: Regras de adjacencia e validacao de mapa
- **Task 3.2.4**: RunState + RunManager (orquestra a run, navegacao no mapa)
- **Task 3.2.5**: CombatRoom (configura e roda batalha, distribui loot)
- **Task 3.2.6**: Integracao: run completa Floor 1 (navegacao + combates + boss)

### Fase 3.3 — Eventos

- **Task 3.3.1**: Event Protocol + EventChoice dataclass
- **Task 3.3.2**: 5 eventos iniciais (Altar, Fonte, Ferreiro, Prisioneiro, Encruzilhada)
- **Task 3.3.3**: 5 eventos adicionais (Mercador, Treinador, Pedra, Obelisco, Oraculo)
- **Task 3.3.4**: EventRoom (apresenta evento, aplica escolha ao RunState)

### Fase 3.4 — Reliquias

- **Task 3.4.1**: Relic + RelicEffect Protocol + RelicManager
- **Task 3.4.2**: 8 reliquias Common
- **Task 3.4.3**: 6 reliquias Uncommon
- **Task 3.4.4**: 4 reliquias Rare + 2 Legendary
- **Task 3.4.5**: Integracao com combat (hooks de reliquia durante batalha)

### Fase 3.5 — Loot System → [LOOT_SYSTEM.md](dungeon/LOOT_SYSTEM.md)

- **Task 3.5.1**: Rarity enum + DropEntry + DropTable dataclasses
- **Task 3.5.2**: Drop tables por tier (data-driven JSON)
- **Task 3.5.3**: WeaponGenerator (base + prefixo + sufixo procedural)
- **Task 3.5.4**: Prefixos e sufixos de arma (elemental, ofensivo, utilitario)
- **Task 3.5.5**: 10 armas legendarias predefinidas (drops de boss/elite)
- **Task 3.5.6**: Lista completa de consumiveis com efeitos
- **Task 3.5.7**: Integracao loot com combate (reward apos vitoria)

### Fase 3.6 — Shop + Economia → [ECONOMY.md](dungeon/ECONOMY.md)

- **Task 3.6.1**: Shop + ShopItem + ShopGenerator
- **Task 3.6.2**: GoldCalculator (rewards por combate, ajuste por modifier/reliquia)
- **Task 3.6.3**: PriceCalculator (precos dinamicos, venda de itens)
- **Task 3.6.4**: ShopRoom (UI de compra, integracao com RunState)

### Fase 3.7 — Rest Rooms → [REST_ROOMS.md](dungeon/REST_ROOMS.md)

- **Task 3.7.1**: RestAction enum + RestRoom (7 acoes de descanso)
- **Task 3.7.2**: Forge system (combinacao de consumiveis, receitas JSON)
- **Task 3.7.3**: Integracao rest room com RunState e mapa

### Fase 3.8 — Party Selection → [PARTY_SELECTION.md](dungeon/PARTY_SELECTION.md)

- **Task 3.8.1**: PartySelection (selecao de 4 classes, validacao)
- **Task 3.8.2**: Dados de sinergias entre classes
- **Task 3.8.3**: Tela de party selection (UI, class info, posicionamento)

### Fase 3.9 — Run Modifiers → [RUN_MODIFIERS.md](dungeon/RUN_MODIFIERS.md)

- **Task 3.9.1**: RunModifier dataclass + RunModifierType enum
- **Task 3.9.2**: 6 modifiers de dificuldade + 4 economia + 4 restricao + 3 chaos
- **Task 3.9.3**: Stacking, score multiplier, desbloqueio progressivo
- **Task 3.9.4**: Tela de selecao de modifiers pre-run

### Fase 3.10 — Meta-progressao

- **Task 3.10.1**: SaveData + persistencia JSON
- **Task 3.10.2**: Desbloqueio de classes (por floor completado)
- **Task 3.10.3**: Desbloqueio de reliquias e modifiers
- **Task 3.10.4**: Bestiary + Achievements

### Fase 3.11 — Class Colors + Visual → [CLASS_COLORS.md](dungeon/CLASS_COLORS.md)

- **Task 3.11.1**: `data/ui/class_colors.json` com 13 cores tematicas
- **Task 3.11.2**: `load_class_colors()` loader modular
- **Task 3.11.3**: Integracao com UI (card borders, nomes, party selection)

### Fase 3.12 — Integracao Final

- **Task 3.12.1**: Run completa (party selection → 3 floors → boss final)
- **Task 3.12.2**: Balanceamento (HP, dano, precos, drop rates, curva de gold)
- **Task 3.12.3**: UI da dungeon (mapa ramificado, tela de evento, shop, rest)

---

## Ordem de Execucao Recomendada

```text
3.0 (Reactions) ──→ 3.1 (Bestiary) ──→ 3.2 (Dungeon Map) ──→ 3.3 (Eventos)
                                                              ├→ 3.4 (Reliquias)
                                                              ├→ 3.5 (Loot)
                                                              ├→ 3.6 (Shop/Economia)
                                                              └→ 3.7 (Rest Rooms)
3.8 (Party Selection) ← pode comecar em paralelo com 3.2
3.9 (Run Modifiers) ← depende de 3.2 (RunState)
3.10 (Meta) ← depende de 3.8 (desbloqueio de classes)
3.11 (Colors) ← pode ser feito a qualquer momento
3.12 (Integracao) ← por ultimo, une tudo
```

**Prioridades:**

- Reactions e Bestiary primeiro: dao conteudo pro combate
- Dungeon Map segundo: da o loop de jogo com branching
- Loot, Shop, Rest, Eventos, Reliquias: paralelos depois da estrutura
- Party Selection: pode comecar cedo (nao depende de dungeon)
- Meta e integracao final por ultimo

---

## Notas de Design

### O que NAO fazer
- **Nao tocar no core/** — dungeon e consumidor, nao modificador
- **Nao hardcodar numeros** — tudo em JSON para iterar rapido
- **Nao over-engineer** — comeca com 3 floors fixos, procedural de verdade depois
- **Nao balancear cedo** — primeiro faz funcionar, depois ajusta numeros

### Inspiracoes
- **Slay the Spire**: Reliquias, eventos com tradeoff, map de salas
- **Darkest Dungeon**: Stress/risco, party composition importa
- **Genshin Impact**: Elemental reactions como core mechanic
- **Hades**: Meta-progressao que desbloqueia opcoes (nao poder)

### Principios
1. **Escolha > Acaso**: Toda aleatoriedade deve ter contrapeso de escolha do jogador
2. **Sinergia > Stats**: Party composition e combos devem importar mais que numeros brutos
3. **Risk/Reward**: Toda escolha boa deve ter um custo potencial
4. **One More Run**: O loop deve ser curto o suficiente pra "so mais uma run"
