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
1035 testes passando | 100% cobertura | 0 falhas
```

Estrutura de teste:
```python
def test_fighter_overdrive_consumes_all_action_points():
    # Arrange - preparar dados
    # Act - executar acao
    # Assert - verificar resultado
```

### Commits

Um commit por task do PRD. Commits podem ter 20+ arquivos — isso e intencional. Cada task e uma feature coesa (enums + dataclass + loader + testes), e separar artificialmente quebraria o principio de que cada commit deixa o projeto num estado funcional e verde. Codigo e seus testes sao uma unidade: `git bisect` e `git revert` operam na feature inteira, sem deixar testes orfaos ou codigo sem cobertura.

### Design Patterns

Guia detalhado com exemplos: [`docs/DESIGN_PATTERNS.md`](docs/DESIGN_PATTERNS.md)

| Pattern | Onde e usado |
|---|---|
| **Template Method** | `Effect.tick()` — esqueleto fixo, hooks customizaveis nas subclasses |
| **Strategy** | `TurnHandler` Protocol — diferentes estrategias de acao no combate |
| **Dispatch Table** | `DispatchTurnHandler` — mapa nome→handler com fallback |
| **Factory** | `buff_factory.py`, `ailment_factory.py`, `from_json()`/`from_dict()` |
| **ABC + Polimorfismo** | `Effect` ABC → `StatBuff`, `StatDebuff`, `DotAilment`, `CcAilment` |
| **Protocol (ISP)** | `Combatant`, `Targetable`, `TurnHandler` — interfaces segregadas |
| **State (Inline)** | `Stance` do Fighter, `Overcharge` do Mage, `ChannelDivinity` do Cleric |
| **Value Object** | Frozen dataclasses: `DamageResult`, `CombatEvent`, `StatModifier`, `Weapon` |
| **Dependency Injection** | Construtor injection em todas as classes (facilita mocks nos testes) |
| **Memoization** | `get_threshold_bonuses()` com cache invalidavel |

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

### Fase 1 — Core Engine

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
- [x] Cleric (divindade, cura, holy power, channel divinity)
- [x] Mock Battle integracao (Fighter+Mage+Cleric vs Goblins)

### Fase 2 — Profundidade (em andamento)

- [x] Effects framework (Effect ABC, EffectManager, stacking, tick/expire)
- [x] Buffs e Debuffs (StatBuff/StatDebuff, factories, flat/percent)
- [x] Status Ailments (13 ailments: DoTs, CC, debuffs, resource locks)
- [x] Sistema elemental (10 elementos, fraquezas/resistencias, on-hit data-driven)
- [x] Integracao effects + combat engine (tick phase, elemental attack)
- [x] Sistema de armas (15 armas, weapon_die routing, proficiencias, armas elementais)
- [ ] Level up e progressao (XP, level 1-10, attribute points)
- [ ] 10 classes restantes (Barbarian, Paladin, Ranger, Monk, Sorcerer, Warlock, Druid, Rogue, Bard, Artificer)
- [ ] Armaduras e acessorios
- [ ] Consumiveis e inventario
- [ ] Mock Battle v2 (integracao completa)
- [ ] Pygame preview visual

### Futuro

- [ ] Sistema de subclasses (escolha no lvl 3)
- [ ] Sistema de habilidades e spell slots
- [ ] IA de inimigos
- [ ] UI completa com Pygame
