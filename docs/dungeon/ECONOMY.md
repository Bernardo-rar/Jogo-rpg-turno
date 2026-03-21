# Economy — Design Detalhado

## Conceito

Gold e o recurso central da run. Ganho via combate, gasto na shop e em eventos. A economia deve ser **tensa mas nao frustrante** — o jogador nunca compra tudo, sempre tem que priorizar.

---

## Fontes de Gold

### Combate

| Fonte | Gold Range | Media |
|-------|-----------|-------|
| Monstro Tier 1 | 3-8 por monstro | ~5 |
| Monstro Tier 2 | 6-15 por monstro | ~10 |
| Monstro Tier 3 | 12-25 por monstro | ~18 |
| Encounter T1 (3 monstros) | 10-25 | ~15 |
| Encounter T2 (3-4 monstros) | 20-50 | ~35 |
| Encounter T3 (3-4 monstros) | 40-80 | ~55 |
| Elite T1 | 20-45 | ~30 |
| Elite T2 | 35-75 | ~50 |
| Elite T3 | 60-120 | ~85 |
| Boss Floor 1 | 100 (fixo) | 100 |
| Boss Floor 2 | 200 (fixo) | 200 |
| Boss Floor 3 | 300 (fixo) | 300 |

### Outras Fontes

| Fonte | Gold | Notas |
|-------|------|-------|
| Treasure Room | 30-80 (varia por floor) | Alem de item |
| Evento — Mercador Shady (ameacar, sucesso) | 20-40 | 50% chance |
| Evento — Obelisco (sacrifica reliquia) | 0 | Troca por reliquia, nao gold |
| Vender item na shop | 40% do valor de compra | Opcional |
| Reliquia "Bolsa de Moedas" | +20% gold de combate | Passivo |

---

## Gastos de Gold

### Shop — Precos por Categoria

**Consumiveis:**
| Item | Preco |
|------|-------|
| Pocao HP Menor | 15g |
| Pocao HP Media | 30g |
| Pocao HP Maior | 60g |
| Pocao HP Total | 100g |
| Pocao Mana Menor | 15g |
| Pocao Mana Media | 30g |
| Pocao Mana Maior | 60g |
| Pocao Restauracao | 40g |
| Elixir Completo | 150g |
| Antidoto | 10g |
| Sal Aromatico | 10g |
| Agua Benta | 25g |
| Elixir Purificacao | 50g |
| Oleo de Ataque | 20g |
| Incenso Arcano | 20g |
| Pocao de Ferro | 25g |
| Pocao de Barreira | 25g |
| Pocao de Velocidade | 30g |
| Cristal Elemental | 35g |
| Oleo Elemental | 50g |
| Elixir de Furia | 45g |
| Bomba de Fumaca | 20g |
| Pergaminho Teleporte | 80g |
| Mapa Antigo | 40g |
| Totem de Revive | 100g |

**Armas (preco base por raridade, ajustado pelo tier):**
| Raridade | Preco Base | Tier 1 | Tier 2 | Tier 3 |
|----------|-----------|--------|--------|--------|
| Common | 30g | 30g | 40g | 50g |
| Uncommon | 60g | 60g | 80g | 100g |
| Rare | 120g | 120g | 150g | 180g |
| Epic | 200g | — | 200g | 250g |

**Reliquias (preco base por raridade):**
| Raridade | Preco |
|----------|-------|
| Common | 80g |
| Uncommon | 150g |
| Rare | 250g |
| Legendary | NAO vendido em shop (so drop) |

### Eventos com Custo

| Evento | Custo | Beneficio |
|--------|-------|-----------|
| Ferreiro (elemento aleatorio) | 40g | Elemento na arma |
| Ferreiro (escolhe elemento) | 80g | Elemento escolhido |
| Mercador Shady (compra misterioso) | 60-100g | Reliquia random (pode ser lixo) |
| Oraculo (versao paga) | 30g | Revela fraquezas |

---

## Curva de Gold Esperada

### Cenario: Caminho Medio (sem modifier, sem reliquia economica)

**Floor 1** (~4 combates + 1 elite + 1 boss):
| Fonte | Gold Estimado |
|-------|--------------|
| 4 encounters T1 | ~60g |
| 1 elite T1 | ~30g |
| Boss | 100g |
| **Total Floor 1** | **~190g** |

Gastos Floor 1: Shop (~80-120g) + eventos (~0-40g) = ~100-160g
**Saldo pro Floor 2: ~30-90g**

**Floor 2** (~5 combates + 1-2 elite + 1 boss):
| Fonte | Gold Estimado |
|-------|--------------|
| 5 encounters T2 | ~175g |
| 1-2 elites T2 | ~50-100g |
| Boss | 200g |
| **Total Floor 2** | **~425-475g** |

Gastos Floor 2: Shop (~120-200g) + eventos (~0-80g) = ~120-280g
**Saldo pro Floor 3: ~175-355g** (acumulado com resto do F1)

**Floor 3** (~6 combates + 2-3 elite + 1 boss):
| Fonte | Gold Estimado |
|-------|--------------|
| 6 encounters T3 | ~330g |
| 2-3 elites T3 | ~170-255g |
| Boss | 300g |
| **Total Floor 3** | **~800-885g** |

### Resumo da Curva

| Floor | Gold Ganho | Gold Gasto (estimado) | Saldo Acumulado |
|-------|-----------|----------------------|----------------|
| 1 | ~190g | ~130g | ~60g |
| 2 | ~450g | ~200g | ~310g |
| 3 | ~840g | ~350g | ~800g |
| **Total Run** | **~1480g** | **~680g** | **~800g sobra** |

> O jogador gasta ~45% do gold ganho. Os ~55% restantes sao "folga" pra eventos, bad luck, e escolhas nao-otimas. Se estiver apertado, precisa priorizar combates e elites em vez de eventos.

---

## Balanceamento: Tensao Economica

### Principios

1. **Nunca compra tudo**: Shop tem mais itens do que o jogador pode comprar. Sempre escolhe
2. **Gold e tempo**: Ir pra combate extra = mais gold mas mais HP gasto
3. **Risco/recompensa**: Elites dao ~2x gold mas sao mais perigosos
4. **Pocao tax**: Pocoes sao necessarias mas caras — nao poder estocar pocoes infinitas
5. **Legendary sao drops, nao compras**: Armas top vem de bosses/elites, nao da shop

### Alavancas de Ajuste

Se economia estiver facil demais:
- Aumentar precos da shop
- Reduzir gold de combate
- Adicionar "tax" por floor (perda de gold)

Se economia estiver dificil demais:
- Aumentar gold de elites (recompensar risco)
- Adicionar opcao de vender itens
- Treasure rooms mais comuns

### Modifiers Economicos (ver RUN_MODIFIERS.md)

| Modifier | Efeito na Economia |
|----------|-------------------|
| Poverty | -30% gold, -20% precos |
| Inflation | +25% gold, +40% precos |
| Tax Collector | -10% gold por floor, +1 drop |
| Minimalist | Menos slots, consumiveis 20% mais fortes |
| Bolsa de Moedas (reliquia) | +20% gold combate |

---

## Implementacao

```python
# src/dungeon/economy/gold_calculator.py
class GoldCalculator:
    """Calcula gold reward de combate baseado em contexto."""

    def calculate_combat_reward(self, enemies: list[Character],
                                 is_elite: bool,
                                 modifiers: list[RunModifier],
                                 relics: list[Relic]) -> int:
        base = sum(self._gold_per_enemy(e) for e in enemies)
        if is_elite:
            base = int(base * 1.5)
        base = self._apply_modifiers(base, modifiers)
        base = self._apply_relics(base, relics)
        return base

    def calculate_boss_reward(self, floor: int) -> int:
        return {1: 100, 2: 200, 3: 300}[floor]

# src/dungeon/economy/price_calculator.py
class PriceCalculator:
    """Calcula precos da shop baseado em contexto."""

    def get_price(self, item: ShopItem,
                  modifiers: list[RunModifier]) -> int:
        base = item.base_price
        return self._apply_modifiers(base, modifiers)

    def get_sell_price(self, item: ShopItem) -> int:
        return int(item.base_price * 0.4)
```

### Dados: `data/dungeon/economy.json`

```json
{
  "gold_per_monster": {
    "tier1": {"min": 3, "max": 8},
    "tier2": {"min": 6, "max": 15},
    "tier3": {"min": 12, "max": 25}
  },
  "boss_gold": {"floor1": 100, "floor2": 200, "floor3": 300},
  "elite_gold_multiplier": 1.5,
  "sell_price_ratio": 0.4,
  "treasure_gold": {
    "floor1": {"min": 30, "max": 50},
    "floor2": {"min": 40, "max": 65},
    "floor3": {"min": 55, "max": 80}
  }
}
```
