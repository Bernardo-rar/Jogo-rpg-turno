# Run Modifiers — Design Detalhado

## Conceito

Run modifiers (ou "mutadores") sao condicoes globais que alteram a run inteira. Comecam **basicos** e simples. Sao opcoes que o jogador ativa ANTES de iniciar a run pra aumentar dificuldade em troca de recompensa.

Inspiracao: Pact of Punishment (Hades), Ascension (Slay the Spire).

---

## Tipos de Modifier

### Categorias

| Categoria | Descricao |
|-----------|-----------|
| **Dificuldade** | Torna a run mais dificil (mais dano, menos cura) |
| **Economia** | Altera ganho/gasto de gold |
| **Restricao** | Limita opcoes do jogador |
| **Chaos** | Efeitos imprevisíveis (pode ajudar ou atrapalhar) |

---

## Modifiers Basicos (Pool Inicial)

### Dificuldade

| Modifier | Efeito | Recompensa |
|----------|--------|------------|
| **Frail** | Party recebe +15% dano | +15% gold ganho |
| **Enfeebled** | Party causa -15% dano | +15% gold ganho |
| **Cursed Healing** | Cura (pocoes, skills, rest) reduzida em 30% | +20% gold ganho |
| **Elite Surge** | Elites tem +50% chance de spawn (15% → 22.5%) | +10% gold ganho |
| **Boss Rush** | Bosses ganham +20% stats | Loot de boss +1 tier |
| **Fragile Start** | Party comeca com 70% HP | +10% gold ganho |

### Economia

| Modifier | Efeito | Recompensa |
|----------|--------|------------|
| **Poverty** | -30% gold de combate | Itens na shop -20% preco |
| **Inflation** | Precos da shop +40% | +25% gold de combate |
| **Tax Collector** | Perde 10% do gold a cada floor clear | Loot de combate +1 drop extra |
| **Minimalist** | Inventario max reduzido de 10 pra 6 slots | Consumiveis sao 20% mais fortes |

### Restricao

| Modifier | Efeito | Recompensa |
|----------|--------|------------|
| **No Rest** | Rest rooms sao removidos do mapa | +1 evento extra por floor |
| **Sealed Relics** | Max reliquias reduzido de 5 pra 3 | Reliquias dropadas sao +1 raridade |
| **One Path** | Mapa tem apenas 1 caminho (sem branching) | Todos os nos sao revelados |
| **Limited Party** | Party de 3 em vez de 4 | Membros restantes ganham +15% stats |

### Chaos

| Modifier | Efeito | Recompensa |
|----------|--------|------------|
| **Elemental Storm** | Cada combate tem 1 elemento aleatorio. Todos recebem +30% dano desse elemento | Reactions dao +50% efeito |
| **Mutating Enemies** | Monstros tem 1 afixo aleatorio extra (dos afixos de elite) | +20% loot quality |
| **Fortune's Wheel** | A cada sala, 50%: +20% stats party / 50%: -20% stats party | Gold dobrado |

---

## Stacking

- O jogador pode ativar **multiplos modifiers** na mesma run
- Efeitos stackam multiplicativamente (ex: Frail +15% + Enfeebled -15% = ambos aplicados)
- Recompensas stackam aditivamente (ex: +15% + +15% = +30% gold)
- **Combos perigosos**: Frail + Cursed Healing = muito dificil mas muito rewarding

### Score Multiplier

Cada modifier ativo adiciona ao **score multiplier** da run:

| Dificuldade do Modifier | Score Bonus |
|-------------------------|-------------|
| Leve (Poverty, Minimalist) | +10% |
| Medio (Frail, Enfeebled, Inflation) | +20% |
| Forte (No Rest, Limited Party, Boss Rush) | +30% |
| Chaos | +15% (imprevisivel) |

Score final = base score * (1 + soma dos bonus). Score mais alto desbloqueia achievements e cosmeticos.

---

## Desbloqueio

- Comeca com 3 modifiers desbloqueados: **Frail**, **Poverty**, **Fragile Start**
- Cada run completada (vitoria) desbloqueia 1 modifier novo
- Runs com modifiers ativos desbloqueiam modifiers mais dificeis

### Ordem de Desbloqueio

1. Frail, Poverty, Fragile Start (iniciais)
2. Enfeebled, Inflation (apos 1 vitoria)
3. Cursed Healing, Elite Surge, Tax Collector (apos 2 vitorias)
4. Minimalist, Sealed Relics, Boss Rush (apos 3 vitorias)
5. No Rest, One Path, Limited Party (apos 5 vitorias)
6. Elemental Storm, Mutating Enemies, Fortune's Wheel (apos 7 vitorias)

---

## Implementacao

```python
# src/dungeon/run/run_modifier.py
class RunModifierType(Enum):
    FRAIL = "frail"
    ENFEEBLED = "enfeebled"
    CURSED_HEALING = "cursed_healing"
    ELITE_SURGE = "elite_surge"
    BOSS_RUSH = "boss_rush"
    FRAGILE_START = "fragile_start"
    POVERTY = "poverty"
    INFLATION = "inflation"
    TAX_COLLECTOR = "tax_collector"
    MINIMALIST = "minimalist"
    NO_REST = "no_rest"
    SEALED_RELICS = "sealed_relics"
    ONE_PATH = "one_path"
    LIMITED_PARTY = "limited_party"
    ELEMENTAL_STORM = "elemental_storm"
    MUTATING_ENEMIES = "mutating_enemies"
    FORTUNES_WHEEL = "fortunes_wheel"

@dataclass(frozen=True)
class RunModifier:
    type: RunModifierType
    name: str
    description: str
    category: str                   # "difficulty", "economy", "restriction", "chaos"
    effects: dict[str, float]       # Ex: {"damage_taken_mult": 1.15, "gold_mult": 1.15}
    score_bonus: float              # Ex: 0.20 (+20%)
    unlock_requirement: str         # Ex: "2_victories"
```

### Dados: `data/dungeon/run_modifiers.json`
