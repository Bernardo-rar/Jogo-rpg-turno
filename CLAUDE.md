# RPG Turno - Projeto de Jogo

## Visao Geral
RPG por turnos ambientado no mundo de **Adnos**. Party de 4 personagens com 13 classes, subclasses, sistema de combate baseado em action economy (acao, acao bonus, reacao), posicionamento front/back, sistema elemental e progressao de level 1-10.

## Tech Stack
- **Linguagem**: Python 3.12+
- **Testes**: pytest (TDD obrigatorio)
- **UI futura**: Pygame ou equivalente (a ser definido depois do combat engine)
- **Padrao**: Codigo, nomes de variaveis, funcoes e classes em **ingles**. Comentarios e docs podem ser em portugues.

## Arquitetura
Projeto **modular por camadas**, separando logica pura de apresentacao:
```
src/
  core/              # Logica pura do jogo (ZERO dependencia de UI)
    attributes/      # Sistema de atributos (STR, DEX, CON, INT, WIS, CHA, MIND)
    characters/      # Classe base Character e hierarquia
    classes/         # 13 classes (fighter, mage, etc) - cada uma em seu modulo
    combat/          # Engine de combate por turnos
    skills/          # Sistema de habilidades e spell slots
    items/           # Armas, armaduras, consumiveis
    effects/         # Buffs, debuffs, status ailments (Strategy pattern)
    elements/        # Sistema elemental
    progression/     # Level up, talentos, subclasses
  ui/                # Camada visual (futuro - NUNCA importada por core/)
tests/
  core/
    test_attributes/
    test_characters/
    test_classes/
    test_combat/
    test_skills/
    test_items/
    test_effects/
    ...
data/                # JSONs/YAMLs de balanceamento (stats, formulas, classes)
```

## Principios SOLID (OBRIGATORIO)

### S - Single Responsibility
- Cada classe/modulo tem UMA unica razao para mudar.
- Funcoes com no maximo **20 linhas**. Se passar, extrair em funcoes menores.
- Teste do "rewrite reason": se 2+ mudancas externas independentes forcariam reescrever uma funcao, ela tem responsabilidades demais.

### O - Open/Closed
- Aberto para extensao, fechado para modificacao.
- **PROIBIDO** usar cadeias de `isinstance()` ou `if tipo == "guerreiro"` para diferenciar classes.
- Usar **polimorfismo**: cada classe implementa seu proprio comportamento via metodos abstratos/protocolos.
- Adicionar nova classe/skill/efeito = criar novo arquivo, NAO modificar os existentes.

### L - Liskov Substitution
- Subclasses devem poder substituir a classe pai sem quebrar comportamento.
- Se `Fighter` herda de `Character`, qualquer codigo que funciona com `Character` deve funcionar com `Fighter`.
- Se um override muda o contrato do metodo pai, o design esta errado - refatorar.

### I - Interface Segregation
- Interfaces/Protocols pequenos e focados (max 5 metodos).
- Nao forcar classes a implementar metodos que nao usam.
- Exemplo: `Healable`, `Buffable`, `Damageable` como protocolos separados, NAO um unico `CombatEntity` gigante.

### D - Dependency Inversion
- Modulos de alto nivel dependem de abstracoes (Protocol/ABC), NAO de implementacoes concretas.
- **Injecao de dependencia** via construtor. NUNCA instanciar dependencias dentro da classe.
- Isso permite mockar tudo nos testes facilmente.

## Clean Code (OBRIGATORIO)

### Nomes
- Nomes revelam intencao: `calculate_physical_damage()`, NAO `calc()` ou `proc()`
- Classes: PascalCase (`Fighter`, `ActionPointSystem`)
- Funcoes/variaveis: snake_case (`calculate_damage`, `hp_regen_rate`)
- Constantes: UPPER_SNAKE_CASE (`MAX_PARTY_SIZE = 4`, `BASE_CRIT_CHANCE = 0.05`)
- Sem abreviacoes cripticas. `strength` ou `str_value`, nao `s` ou `x`

### Funcoes
- Max **20 linhas** por funcao
- Max **3 parametros**. Se precisar de mais, criar dataclass/NamedTuple
- Max **3 niveis de indentacao** (usar guard clauses/early returns)
- Sem magic numbers: todo numero literal deve ser uma constante nomeada

### Classes
- Max **200 linhas** por classe
- Max **10 metodos** por classe (sem contar properties)
- Se a classe crescer, extrair responsabilidades em classes menores

### DRY
- Nenhuma logica duplicada. Se 2 lugares fazem a mesma coisa, extrair em funcao/classe compartilhada.
- Dados de balanceamento em `data/`, NAO hardcoded no codigo.

### Comentarios
- Codigo deve ser auto-explicativo. Comentarios so para o "por que", nunca para o "o que".
- Se precisa de comentario para explicar o que o codigo faz, refatorar o codigo.

### Error Handling
- Enumerar failure modes explicitamente em docstrings
- Nao usar `except Exception` generico - capturar excecoes especificas
- Nao usar exceptions para controle de fluxo normal (ex: retornar `None` se nao encontrar, nao `raise NotFoundError`)

## TDD - Test Driven Development (OBRIGATORIO)

### Workflow
1. **RED**: Escrever o teste PRIMEIRO. Ele deve falhar.
2. **GREEN**: Escrever o MINIMO de codigo para o teste passar.
3. **REFACTOR**: Melhorar o codigo mantendo os testes verdes.

### Regras
- **Nenhum codigo de logica sem teste correspondente.**
- Testes sao documentacao viva: nomes descritivos tipo `test_fighter_overdrive_consumes_all_action_points()`
- Cada teste testa UMA coisa. Sem asserts multiplos testando coisas diferentes.
- Usar fixtures do pytest para setup compartilhado.
- Mockar dependencias externas (DI facilita isso).

### Estrutura de teste
```python
def test_<o_que_esta_sendo_testado>_<cenario>_<resultado_esperado>():
    # Arrange - preparar dados
    # Act - executar acao
    # Assert - verificar resultado
```

## Convencoes de Codigo
- Type hints obrigatorios em todas as funcoes publicas
- Docstrings em funcoes e classes publicas (estilo Google)
- Sem imports circulares (a arquitetura em camadas previne isso)
- `src/core/` NUNCA importa de `src/ui/` (dependencia unidirecional)

## Comandos
```bash
# Rodar todos os testes
pytest

# Rodar testes com cobertura
pytest --cov=src

# Rodar testes de um modulo especifico
pytest tests/core/test_combat/

# Rodar apenas testes que falharam na ultima vez
pytest --lf

# Rodar o jogo (futuro)
python -m src.main
```

## Design Patterns Recomendados
- **Strategy**: Para diferentes tipos de dano, efeitos de buff/debuff, comportamento de IA
- **Observer**: Para eventos de combate (on_hit, on_crit, on_death, on_buff)
- **Factory**: Para criacao de personagens, skills, itens
- **State**: Para estados de combate (turno do jogador, turno inimigo, selecao de alvo)
- **Composite**: Para efeitos compostos (buff que aplica varios sub-efeitos)
- **Template Method**: Para fluxo de turno (pre-turno → acao → pos-turno) onde cada classe customiza partes

## Sistema de Combate (Core do MVP)
- **Action Economy**: Acao Normal + Acao Bonus + Reacao por turno
- **Posicionamento**: Front line / Back line
- **Ordem de turno**: Baseada em Speed
- **Tipos de dano**: Fisico (corte/perfuracao/contusao) e Magico (8+ elementos)
- **Dano**: `(dado_arma + mods) * mod_ataque` vs `defesa_alvo`
- **Defesa Fisica**: `(DEX + CON + STR) * def_fisica_mod`
- **Defesa Magica**: `(CON + WIS + INT) * def_magica_mod`

## Referencia Rapida - Formulas de Balanceamento
- **HP lvl1**: `((hit_dice + CON + vida_mod) * 2) * mod_hp`
- **Mana lvl1**: `dado_mana * MIND * 10`
- **Bonus de atributo**: Cada +1 da bonus incremental; thresholds EXTRAS em 18, 22, 26 (tier 1) e 30, 32 (tier 2)
- **Regen HP**: `CON * nivel * constante`
- **Regen Mana**: `MIND * nivel * constante`
- **CA**: `CA_armadura + DEX + nivel`
- **Reducao dano fisico**: `CA / 4` (base, varia por classe)

## Status do Projeto
- [ ] Setup do projeto (pyproject.toml, pytest config, estrutura de pastas)
- [ ] Sistema de atributos (7 primarios + derivados)
- [ ] Classe base Character
- [ ] Engine de combate por turnos (action economy)
- [ ] 13 classes com mecanicas unicas
- [ ] Sistema de subclasses (escolha no lvl 3)
- [ ] Sistema de habilidades (spell slots com custo customizavel)
- [ ] Sistema de buffs/debuffs/status ailments
- [ ] Sistema elemental (8+ elementos com efeitos on-hit)
- [ ] Sistema de equipamento (armas, armaduras, acessorios, consumiveis)
- [ ] Progressao (level up 1-10, talentos, aumento de atributos)
- [ ] IA de inimigos (dificuldade baseada em comportamento, nao so stats)
- [ ] UI/Rendering (Pygame)

## Workflow de Desenvolvimento (Ralph Loop Adaptado)

Usamos um loop incremental inspirado no conceito de Ralph Loop para evitar "context rot":

### A cada sessao de trabalho:
1. **LER** `docs/PROGRESS.md` para saber o estado atual do projeto
2. **LER** `docs/REQUISITOS_FUNCIONAIS.md` para saber o objetivo da task atual
3. **EXECUTAR** a proxima task pendente seguindo TDD (Red → Green → Refactor)
4. **ATUALIZAR** `docs/PROGRESS.md` com o que foi feito, arquivos criados, notas
5. **RODAR** `pytest` para garantir que tudo continua verde

### Regras do loop:
- Uma task por vez. Nao pular etapas.
- Cada task deve terminar com todos os testes passando.
- Se uma task for grande demais, quebrar em sub-tasks no PROGRESS.md.
- Decisoes de design importantes devem ser anotadas nas "Notas" da task.
- O PROGRESS.md e a fonte de verdade do estado do projeto.

## Documentos de Design Originais
Os documentos de design originais estao em `Coisas interessantes/` e `Coisas interessantes/Tudo o q estava no notion/`. Consultar para detalhes de:
- Classes e subclasses: `Classes/`
- Balanceamento numerico: `AA parte numerica/`
- Mecanicas de combate: `DO JOOJ/MEcanicas de jogo/`
- Status e atributos: `DO JOOJ/Status.txt`
- Armas e itens: `DO JOOJ/Armas/`
- Ideias gerais: `Ideias soltas/`
