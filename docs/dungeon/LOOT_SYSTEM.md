# Loot System — Design Detalhado

## Conceito

Loot e a recompensa tangivel por combate. O sistema tem 2 eixos:
1. **Armas/Equipamentos gerados proceduralmente** — base + afixos aleatorios
2. **Itens predefinidos unicos** — armas nomeadas com efeitos especiais fixos

Alem disso: consumiveis, materiais, e gold.

---

## Categorias de Loot

### 1. Armas
Principal loot. Podem ser geradas ou predefinidas.

### 2. Consumiveis
Pocoes, antidotos, buffs temporarios. Usados durante ou fora de combate.

### 3. Materiais
Ingredientes pra forge (rest room). Nao tem uso direto.

### 4. Gold
Moeda da run. Gasto na shop.

### 5. Reliquias
Drops raros de elites e bosses. Ver [Reliquias](../DUNGEON_DESIGN.md#fase-34--sistema-de-reliquias).

---

## Raridade

| Raridade | Cor | Drop Rate Base | Afixos | Power Level |
|----------|-----|----------------|--------|-------------|
| **Common** | Branco | 50% | 0 | Baseline |
| **Uncommon** | Verde | 30% | 1 | +15-25% |
| **Rare** | Azul | 15% | 2 | +30-50% |
| **Epic** | Roxo | 4% | 2 + bonus especial | +60-80% |
| **Legendary** | Dourado | 1% | Unico (predefinido) | +100%+ |

> Drop rates ajustados por tier do monstro, elite status, e reliquias.

---

## Armas — Geracao Procedural

### Estrutura de uma Arma Gerada

```
[Prefixo] + [Base] + [Sufixo]
```

Exemplo: **"Flamejante Espada Longa da Celeridade"**
- Prefixo: Flamejante (FIRE damage)
- Base: Espada Longa (corte, d8)
- Sufixo: da Celeridade (+speed)

### Bases (usa sistema de armas existente)

As 15 armas base do `data/weapons/` servem como pool:

| Base | Tipo | Dado | Proficiencia |
|------|------|------|-------------|
| Dagger | Perfuracao | d4 | Rogue, Bard |
| Short Sword | Corte | d6 | Fighter, Rogue, Ranger |
| Long Sword | Corte | d8 | Fighter, Paladin |
| Great Sword | Corte | d12 | Fighter, Barbarian |
| War Axe | Corte | d8 | Fighter, Barbarian, Ranger |
| Mace | Contusao | d6 | Cleric, Paladin |
| War Hammer | Contusao | d10 | Fighter, Paladin, Barbarian |
| Spear | Perfuracao | d6 | Fighter, Monk, Ranger |
| Halberd | Corte/Perfuracao | d10 | Fighter, Paladin |
| Staff | Contusao | d4 | Mage, Warlock, Druid |
| Wand | Magico | d6 | Mage, Sorcerer, Warlock |
| Bow | Perfuracao | d8 | Ranger, Rogue |
| Crossbow | Perfuracao | d10 | Ranger, Artificer |
| Fist Weapon | Contusao | d6 | Monk |
| Tome | Magico | d8 | Mage, Cleric, Sorcerer |

### Prefixos (Elemental / Ofensivo)

| Prefixo | Efeito | Raridade Min |
|---------|--------|-------------|
| Flamejante | +FIRE dano (10-20% base) | Uncommon |
| Gelida | +ICE dano (10-20% base) | Uncommon |
| Eletrificada | +LIGHTNING dano (10-20% base) | Uncommon |
| Sagrada | +HOLY dano (10-20% base) | Rare |
| Sombria | +DARKNESS dano (10-20% base) | Rare |
| Venenosa | 20% chance Poison on-hit | Uncommon |
| Sangrenta | 20% chance Bleed on-hit | Uncommon |
| Furiosa | +15% dano quando portador < 50% HP | Rare |
| Vampirica | 5% life steal | Epic |
| Caotica | Elemento aleatorio a cada hit | Epic |

### Sufixos (Defensivo / Utilitario)

| Sufixo | Efeito | Raridade Min |
|--------|--------|-------------|
| da Celeridade | +10% speed | Uncommon |
| da Protecao | +5% DEF fisica | Uncommon |
| da Resiliencia | +5% DEF magica | Uncommon |
| do Vigor | +5% HP max | Rare |
| da Concentracao | +5% mana max | Rare |
| do Vampiro | +3% life steal | Rare |
| da Execucao | +20% dano vs inimigos < 25% HP | Epic |
| do Mestre | -1 turno CD de habilidades | Epic |

### Regras de Geracao

```python
# src/dungeon/loot/weapon_generator.py
class WeaponGenerator:
    def generate(self, tier: int, rarity: Rarity,
                 seed: int) -> Weapon:
        base = self._pick_base(tier, seed)
        prefix = self._pick_prefix(rarity, seed) if rarity >= UNCOMMON else None
        suffix = self._pick_suffix(rarity, seed) if rarity >= RARE else None
        return self._assemble(base, prefix, suffix)
```

- Common: base pura, sem afixos
- Uncommon: base + 1 afixo (prefixo OU sufixo)
- Rare: base + 2 afixos (prefixo E sufixo)
- Epic: base + 2 afixos + bonus especial
- Legendary: predefinido (ver abaixo)

---

## Armas Predefinidas (Legendarias)

Armas unicas com nome, historia e efeito especial. NAO sao geradas proceduralmente. Dropam de bosses ou eventos raros.

| Arma | Tipo | Dado | Elemento | Efeito Especial |
|------|------|------|----------|-----------------|
| **Kingslayer** | Espada Longa | d10 | — | +50% dano vs bosses |
| **Phoenix Edge** | Espada Longa | d8 | FIRE | Ao matar um inimigo, proxima ataque auto-crit |
| **Frostmourne** | Espada Grande | d12 | ICE | Ataques tem 25% chance Freeze. -10% speed portador |
| **Shadowfang** | Adaga | d6 | DARKNESS | Ataques da backline dao 2x dano. Frontline dao 0.5x |
| **Staff of Eternity** | Cajado | d6 | CELESTIAL | Magias custam 20% menos mana |
| **Thundergod's Wrath** | Martelo | d12 | LIGHTNING | 1x por combate: AoE que stun todos inimigos 1 turno |
| **Lifedrinker** | Machado | d10 | DARKNESS | 15% life steal. Portador perde 3% HP max por combate |
| **Holy Avenger** | Lanca | d8 | HOLY | +30% dano vs undead. Cura 5% HP ao matar undead |
| **Bow of the Wind** | Arco | d10 | FORCE | Ignora posicao (ataca front ou back livremente) |
| **Grimoire of Chaos** | Tome | d10 | Aleatorio | Cada magia tem elemento aleatorio. +25% dano magico |

### Drop Rules para Legendarias

- Boss Floor 1: 10% chance de drop legendario
- Boss Floor 2: 20% chance
- Boss Floor 3: 40% chance
- Elite Tier 3: 3% chance
- Evento "Mercador Shady": pool especifico de 3 legendarias

---

## Consumiveis

### Lista Completa

**Cura:**
| Item | Efeito | Tier | Preco Shop |
|------|--------|------|-----------|
| Pocao de Cura Menor | Cura 20% HP max | 1 | 15g |
| Pocao de Cura Media | Cura 40% HP max | 2 | 30g |
| Pocao de Cura Maior | Cura 70% HP max | 3 | 60g |
| Pocao de Cura Total | Full heal | 3 | 100g |

**Mana:**
| Item | Efeito | Tier | Preco Shop |
|------|--------|------|-----------|
| Pocao de Mana Menor | Restaura 20% mana max | 1 | 15g |
| Pocao de Mana Media | Restaura 40% mana max | 2 | 30g |
| Pocao de Mana Maior | Restaura 70% mana max | 3 | 60g |

**Restauracao:**
| Item | Efeito | Tier | Preco Shop |
|------|--------|------|-----------|
| Pocao de Restauracao | Cura 25% HP + 25% mana | 2 | 40g |
| Elixir Completo | Full heal + full mana | 3 | 150g |

**Cura de Status:**
| Item | Efeito | Tier | Preco Shop |
|------|--------|------|-----------|
| Antidoto | Remove Poison | 1 | 10g |
| Sal Aromatico | Remove Stun, Sleep, Confusion | 1 | 10g |
| Agua Benta | Remove Curse, Silence | 2 | 25g |
| Elixir de Purificacao | Remove TODOS ailments de 1 alvo | 3 | 50g |

**Buffs Temporarios (duram 1 combate):**
| Item | Efeito | Tier | Preco Shop |
|------|--------|------|-----------|
| Oleo de Ataque | +15% dano fisico 1 combate | 1 | 20g |
| Incenso Arcano | +15% dano magico 1 combate | 1 | 20g |
| Pocao de Ferro | +15% DEF fisica 1 combate | 2 | 25g |
| Pocao de Barreira | +15% DEF magica 1 combate | 2 | 25g |
| Pocao de Velocidade | +20% speed 1 combate | 2 | 30g |
| Cristal Elemental | Adiciona elemento aleatorio a arma 1 combate | 2 | 35g |
| Oleo Elemental | Adiciona elemento ESCOLHIDO a arma 1 combate | 3 | 50g |
| Elixir de Furia | +25% ATK, -10% DEF 1 combate | 3 | 45g |

**Especiais:**
| Item | Efeito | Tier | Preco Shop |
|------|--------|------|-----------|
| Bomba de Fumaca | Foge do combate (nao funciona vs boss) | 1 | 20g |
| Pergaminho de Teleporte | Pula 1 sala do mapa (avanca sem combater) | 3 | 80g |
| Mapa Antigo | Revela conteudo de todos os nos de 1 camada | 2 | 40g |
| Totem de Revive | Revive 1 membro com 25% HP se morrer em combate | 3 | 100g |

---

## Drop Tables

### Estrutura

```python
# src/dungeon/loot/drop_table.py
@dataclass(frozen=True)
class DropEntry:
    item_type: str          # "weapon", "consumable", "material", "gold"
    item_id: str | None     # ID especifico ou None pra random
    rarity: Rarity | None   # Se weapon, qual raridade
    weight: int             # Peso relativo (maior = mais provavel)
    quantity: tuple[int, int]  # (min, max)

@dataclass(frozen=True)
class DropTable:
    id: str
    guaranteed: list[DropEntry]    # Sempre dropa
    random_pool: list[DropEntry]   # Rola 1-3 drops daqui
    random_count: tuple[int, int]  # (min, max) drops do pool
```

### Drop Tables por Tier

**Tier 1 (Floor 1 normal):**
- Garantido: 10-30 gold
- Pool (1-2 drops): pocao HP menor (40%), pocao mana menor (20%), antidoto (15%), material T1 (15%), arma common (10%)

**Tier 1 Elite:**
- Garantido: 20-45 gold + 1 consumivel aleatorio
- Pool (2-3 drops): pocao media (25%), arma uncommon (25%), material T1 (20%), buff temporario (15%), arma rare (10%), reliquia common (5%)

**Tier 2 (Floor 2 normal):**
- Garantido: 20-50 gold
- Pool (1-2 drops): pocao media (30%), buff temporario (20%), material T2 (20%), arma uncommon (15%), arma rare (10%), sal aromatico (5%)

**Tier 2 Elite:**
- Garantido: 35-75 gold + 1 arma uncommon+
- Pool (2-3 drops): pocao maior (20%), arma rare (25%), buff temporario (20%), material T2 (15%), reliquia uncommon (10%), arma epic (5%), cristal elemental (5%)

**Tier 3 (Floor 3 normal):**
- Garantido: 40-80 gold
- Pool (1-3 drops): pocao maior (25%), arma rare (20%), buff temporario (20%), material T3 (15%), arma epic (10%), agua benta (10%)

**Tier 3 Elite:**
- Garantido: 60-120 gold + 1 arma rare+
- Pool (2-4 drops): arma epic (20%), pocao maior (15%), reliquia rare (15%), buff temporario (15%), material T3 (15%), elixir (10%), arma legendary (5%), totem revive (5%)

**Boss Floor 1:**
- Garantido: 100 gold + 1 reliquia (common/uncommon) + 1 arma uncommon+
- Pool (1-2 drops): arma rare (30%), pocao maior (25%), buff temporario (20%), reliquia uncommon (15%), arma legendary (10%)

**Boss Floor 2:**
- Garantido: 200 gold + 1 reliquia (uncommon/rare) + 1 arma rare+
- Pool (2-3 drops): arma epic (25%), reliquia rare (20%), elixir (20%), arma legendary (20%), buff temporario (15%)

**Boss Floor 3 (Final):**
- Garantido: 300 gold + 1 reliquia (rare/legendary) + 1 arma epic+
- Pool (2-3 drops): arma legendary (30%), reliquia legendary (20%), elixir completo (20%), arma epic (20%), material T3 (10%)

---

## Dados: `data/dungeon/loot/`

```
data/dungeon/loot/
  drop_tables.json       # Todas as drop tables por tier
  weapon_prefixes.json   # Prefixos de arma com efeitos
  weapon_suffixes.json   # Sufixos de arma com efeitos
  legendary_weapons.json # Armas predefinidas unicas
  consumables.json       # Todos consumiveis com efeitos e precos
  forge_recipes.json     # Receitas de combinacao (rest room)
```
