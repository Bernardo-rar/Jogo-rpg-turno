# Branching Map — Design Detalhado

## Conceito

Em vez de uma sequencia linear de salas, cada floor tem um **mapa ramificado** estilo Slay the Spire. O jogador escolhe qual caminho seguir, com trade-offs entre risco e recompensa.

---

## Estrutura do Mapa

### Anatomia de um Floor

```
        [START]
        /     \
      [C1]   [C2]          <- Camada 1: Combate
      / \     |  \
   [C3] [Ev] [E1] [C4]     <- Camada 2: Mix (Combate/Evento/Elite)
    |    |    |    / \
   [Sh] [C5] [R] [C6] [Ev] <- Camada 3: Mix (Shop/Rest/Combate)
    \    |    |   /   /
     [C7]   [E2]  [C8]     <- Camada 4: Pre-boss (mais dificil)
       \     |    /
        [BOSS]              <- Camada final: Boss (convergencia)
```

**Legenda:**
- `C` = Combate normal
- `E` = Elite (combate dificil, loot melhor)
- `Ev` = Evento (escolha narrativa)
- `Sh` = Shop
- `R` = Rest (descanso)
- `T` = Treasure (bau de loot)

### Regras de Geracao do Mapa

| Regra | Descricao |
|-------|-----------|
| Largura | 2-4 nos por camada |
| Profundidade | Floor 1: 4 camadas + boss. Floor 2: 5 + boss. Floor 3: 6 + boss |
| Conexoes | Cada no conecta a 1-3 nos da proxima camada. Nunca pula camada |
| Convergencia | Todas as rotas convergem no boss (ultima camada tem 1 no so) |
| Start | Sempre 2-3 opcoes iniciais |
| Visibilidade | Jogador ve o mapa inteiro, mas so ve o TIPO de cada no (nao o conteudo exato) |

### Distribuicao de Tipos por Floor

**Floor 1 (4 camadas + boss, ~8-12 nos total):**
| Tipo | Quantidade | Obrigatorio? |
|------|------------|-------------|
| Combate | 4-6 | Sim |
| Elite | 1 | Sim |
| Evento | 1-2 | Sim (min 1) |
| Shop | 1 | Sim |
| Rest | 1 | Sim |
| Treasure | 0-1 | Nao |
| Boss | 1 | Sim |

**Floor 2 (5 camadas + boss, ~10-15 nos total):**
| Tipo | Quantidade | Obrigatorio? |
|------|------------|-------------|
| Combate | 5-7 | Sim |
| Elite | 1-2 | Sim |
| Evento | 2-3 | Sim (min 2) |
| Shop | 1 | Sim |
| Rest | 1-2 | Sim |
| Treasure | 0-1 | Nao |
| Boss | 1 | Sim |

**Floor 3 (6 camadas + boss, ~12-18 nos total):**
| Tipo | Quantidade | Obrigatorio? |
|------|------------|-------------|
| Combate | 6-9 | Sim |
| Elite | 2-3 | Sim |
| Evento | 2-3 | Sim (min 2) |
| Shop | 1-2 | Sim |
| Rest | 1-2 | Sim |
| Treasure | 1 | Sim |
| Boss | 1 | Sim |

### Regras de Adjacencia (o que NAO pode estar lado a lado)

- Shop nunca na camada 1 (precisa gold primeiro)
- Rest nunca na camada 1 (nao precisa descansar ainda)
- Elite nunca adjacente a outro Elite na mesma camada
- Boss sempre sozinho na ultima camada
- Treasure nunca adjacente a Shop (redundante)
- Pelo menos 1 caminho do mapa deve passar por Shop (acessibilidade)
- Pelo menos 1 caminho do mapa deve passar por Rest

---

## Implementacao

### Estrutura de Dados

```python
# src/dungeon/rooms/map_node.py
@dataclass
class MapNode:
    id: str                           # "f1_c2_n3" (floor 1, camada 2, no 3)
    room_type: RoomType               # COMBAT, ELITE, EVENT, SHOP, REST, TREASURE, BOSS
    tier: int                         # Tier dos monstros (se combate)
    connections: list[str]            # IDs dos nos da proxima camada
    visited: bool = False
    revealed: bool = False            # Se conteudo especifico e visivel

# src/dungeon/rooms/floor_map.py
@dataclass
class FloorMap:
    floor_number: int                 # 1, 2 ou 3
    layers: list[list[MapNode]]       # Camadas do mapa
    boss_node: MapNode                # No final (boss)

    def get_available_nodes(self, current_node: MapNode) -> list[MapNode]:
        """Retorna nos acessiveis a partir do no atual."""
        ...

    def get_paths_to_boss(self) -> list[list[MapNode]]:
        """Retorna todas as rotas possiveis ate o boss."""
        ...

# src/dungeon/rooms/map_generator.py
class MapGenerator:
    """Gera FloorMap proceduralmente a partir de seed e regras."""
    def generate(self, floor_number: int, seed: int) -> FloorMap: ...
```

### Algoritmo de Geracao (Resumo)

1. Definir numero de camadas baseado no floor
2. Para cada camada, gerar 2-4 nos com tipos aleatorios (respeitando distribuicao)
3. Conectar nos entre camadas (cada no conecta a 1-3 da proxima)
4. Validar regras de adjacencia
5. Garantir que pelo menos 1 caminho passa por Shop e Rest
6. Se alguma regra falhar, regenerar a camada problematica
7. Adicionar boss como ultima camada (1 no, todos conectam nele)

### Seed e Reproducibilidade

- Cada run tem uma seed
- A seed gera o mapa deterministicamente
- Mesma seed = mesmo mapa, mesmos encounters, mesmos eventos
- Jogador pode compartilhar seeds pra desafios

---

## Navegacao do Jogador

### O que o jogador ve

- Mapa completo com TODOS os nos visiveis
- **Tipo** de cada no e visivel (icone: espada, caveira, ?, loja, fogueira, bau)
- **Conteudo** nao e visivel (nao sabe QUAIS monstros, QUAL evento)
- Caminho atual destacado
- Nos visitados escurecidos

### Decisoes do Jogador

A cada no completado, jogador escolhe o proximo no dentre os conectados. Exemplos de decisoes:

- "Vou pro combate porque preciso de gold pra shop"
- "Vou pro rest porque meu healer ta com 20% HP"
- "Vou pro elite porque quero loot melhor antes do boss"
- "Vou pro evento porque talvez consiga reliquia gratis"

### Informacao Adicional (Reliquias/Skills)

Algumas reliquias e eventos revelam mais informacao:
- **Olho do Observador** (reliquia): revela conteudo dos nos adjacentes ao atual
- **Visao do Oraculo** (evento): revela fraquezas dos monstros nas proximas 2 salas
- **Mapa Antigo** (consumivel): revela conteudo de todos os nos de 1 camada

---

## RunState Atualizado

```python
@dataclass
class RunState:
    seed: int
    party: list[Character]
    current_floor: int                # 1, 2 ou 3
    current_node: MapNode | None      # No atual (None = inicio)
    floor_map: FloorMap               # Mapa do floor atual
    gold: int
    relics: list[Relic]
    inventory: Inventory
    rooms_cleared: int
    enemies_killed: int
    modifiers: list[RunModifier]      # Modificadores da run
    is_over: bool
    victory: bool
```
