# RPG Turno

RPG por turnos ambientado no mundo de **Adnos**. Party de 4 personagens, 13 classes com subclasses, sistema de combate baseado em action economy, posicionamento front/back, sistema elemental e progressao de level 1-10.

## Tech Stack

| Tecnologia | Uso |
|---|---|
| **Python 3.12+** | Linguagem principal |
| **pytest** | Framework de testes (TDD) |
| **Ruff** | Linter e formatter |
| **Pygame** | UI futura (planejado) |

## Arquitetura

Projeto **modular por camadas**, separando logica pura de apresentacao:

```
src/
  core/              # Logica pura do jogo (ZERO dependencia de UI)
    attributes/      # Sistema de atributos (STR, DEX, CON, INT, WIS, CHA, MIND)
    characters/      # Classe base Character e hierarquia
    classes/         # Classes jogaveis (Fighter, Mage, ...)
    combat/          # Engine de combate por turnos
    skills/          # Sistema de habilidades e spell slots
    items/           # Armas, armaduras, consumiveis
    effects/         # Buffs, debuffs, status ailments
    elements/        # Sistema elemental
    progression/     # Level up, talentos, subclasses
  ui/                # Camada visual (futuro - nunca importada por core/)
tests/               # Espelha a estrutura de src/core/
data/                # JSONs de balanceamento (stats, formulas, classes)
```

A camada `core/` **nunca importa** de `ui/` — a dependencia e unidirecional, permitindo testar toda a logica do jogo sem interface grafica.

## Principios e Boas Praticas

### SOLID

- **Single Responsibility** — Funcoes com no maximo 20 linhas, classes com no maximo 200 linhas e 10 metodos. Cada modulo tem uma unica razao para mudar.
- **Open/Closed** — Novas classes, skills e efeitos sao adicionados criando novos arquivos, sem modificar os existentes. Zero cadeias de `isinstance()`.
- **Liskov Substitution** — `Fighter` e `Mage` substituem `Character` em qualquer contexto sem quebrar comportamento.
- **Interface Segregation** — Protocols pequenos e focados (`Combatant`, `Targetable`, `TurnHandler`) ao inves de interfaces monoliticas.
- **Dependency Inversion** — Modulos dependem de abstrações (Protocol/ABC). Injecao de dependencia via construtor em todas as classes.

### Clean Code

- **Nomes descritivos**: `calculate_physical_damage()`, nao `calc()` ou `proc()`
- **Sem magic numbers**: todo literal numerico e uma constante nomeada
- **Guard clauses e early returns**: maximo 3 niveis de indentacao
- **Dataclasses imutaveis** (`frozen=True`) para dados de entrada e resultados
- **Funcoes puras** sem efeito colateral no sistema de combate
- **Dados de balanceamento em JSON**, nao hardcoded no codigo

### TDD (Test-Driven Development)

Todo codigo segue o ciclo **Red -> Green -> Refactor**:

1. **Red** — Escrever o teste primeiro; ele deve falhar
2. **Green** — Escrever o minimo de codigo para o teste passar
3. **Refactor** — Melhorar o codigo mantendo os testes verdes

```
287 testes passando | 0 falhas
```

Estrutura de teste:
```python
def test_fighter_overdrive_consumes_all_action_points():
    # Arrange - preparar dados
    # Act - executar acao
    # Assert - verificar resultado
```

### Design Patterns

| Pattern | Onde e usado |
|---|---|
| **Strategy** | `TurnHandler` Protocol — diferentes estrategias de acao no combate |
| **Factory** | Criacao de personagens com `ClassModifiers.from_json()` |
| **State** | `Stance` do Fighter (Balanced/Offensive/Defensive) |
| **Composite** | `ManaBarrier` do Mage absorve dano antes do HP |
| **Protocol (Structural Typing)** | `Combatant`, `Targetable`, `TurnHandler` — DI sem heranca forcada |

## Sistema de Combate

- **Action Economy**: Acao Normal + Acao Bonus + Reacao por turno
- **Posicionamento**: Front line / Back line (melee so atinge front, ranged atinge ambos)
- **Ordem de turnos**: Baseada em Speed (DEX), empates por ordem alfabetica
- **Dano**: `max(1, attack_power - defense)` com critico multiplicando antes da defesa
- **Defesa Fisica**: `(DEX + CON + STR) * mod_def_fisico`
- **Defesa Magica**: `(CON + WIS + INT) * mod_def_magico`

## Como Rodar

```bash
# Instalar dependencias
pip install -e .

# Rodar todos os testes
pytest

# Rodar testes com cobertura
pytest --cov=src

# Rodar testes de um modulo especifico
pytest tests/core/test_combat/

# Rodar apenas testes que falharam na ultima vez
pytest --lf
```

## Status do Projeto

- [x] Setup do projeto (pyproject.toml, pytest, estrutura)
- [x] Sistema de atributos (7 primarios + derivados + thresholds)
- [x] Classe base Character com HP, Mana, posicao
- [x] Action Economy (acao, bonus, reacao)
- [x] Ordem de turnos (speed-based)
- [x] Posicionamento front/back com targeting
- [x] Sistema de dano e defesa (fisico/magico + critico)
- [x] Combat Engine loop completo
- [x] Fighter (estancias, pontos de acao)
- [x] Mage (barreira de mana, overcharge)
- [ ] 11 classes restantes
- [ ] Sistema de subclasses (escolha no lvl 3)
- [ ] Sistema de habilidades e spell slots
- [ ] Buffs, debuffs e status ailments
- [ ] Sistema elemental
- [ ] Equipamentos (armas, armaduras, acessorios)
- [ ] Progressao (level up 1-10, talentos)
- [ ] IA de inimigos
- [ ] UI com Pygame
