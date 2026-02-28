# Progresso do Projeto - RPG Turno

## Como usar este arquivo
Este arquivo e o "cerebro persistente" do projeto. A cada sessao de trabalho:
1. Ler este arquivo para saber o estado atual
2. Ler o PRD (REQUISITOS_FUNCIONAIS.md) para saber o objetivo
3. Executar a proxima task pendente
4. Atualizar este arquivo com o que foi feito

---

## Fase Atual: FASE 1 - Core Engine (MVP)

## Tasks da Fase 1

### Task 1.0 - Setup do Projeto

- **Status**: CONCLUIDA
- **Descricao**: Criar pyproject.toml, configurar pytest, criar estrutura de pastas src/core/ e tests/
- **Criterio de aceite**: `pytest` roda sem erros, imports funcionam
- **Arquivos criados**: `pyproject.toml`, `.gitignore`, `legacy/` (codigo C++ antigo movido), `src/core/` (attributes, characters, classes, combat, skills, items, effects, elements, progression), `tests/core/` (test_attributes, test_characters, test_classes, test_combat), `data/`
- **Notas**: Python 3.12.7, pytest 8.4.2. Codigo C++ antigo movido para `legacy/`. `Coisas interessantes/` adicionado ao .gitignore.

### Task 1.1 - Sistema de Atributos (RF01)

- **Status**: CONCLUIDA
- **Descricao**: Implementar os 7 atributos primarios, thresholds de bonus, atributos derivados
- **Criterio de aceite**: Testes passando para calculo de bonus em todos os thresholds, stats derivados calculados corretamente
- **Arquivos criados**:
  - `src/core/attributes/attribute_types.py` - Enum AttributeType (7 atributos)
  - `src/core/attributes/attributes.py` - Container Attributes (get/set/increase/decrease)
  - `src/core/attributes/threshold_calculator.py` - ThresholdCalculator (bonus extras nos marcos)
  - `src/core/attributes/derived_stats.py` - Funcoes puras: HP, Mana, Ataque, Defesa, Regen
  - `data/attributes/thresholds.json` - Dados de threshold por atributo (Tier 1: 18/22/26, Tier 2: 30/32)
  - `tests/core/test_attributes/test_attribute_types.py` - 8 testes
  - `tests/core/test_attributes/test_attributes.py` - 9 testes
  - `tests/core/test_attributes/test_threshold_calculator.py` - 13 testes
  - `tests/core/test_attributes/test_derived_stats.py` - 11 testes
- **Notas**: 41 testes passando. Thresholds corrigidos para valores originais (18/22/26/30/32 ao inves de 4/6/8/10/11). Bonus de threshold sao EXTRAS cumulativos alem do scaling incremental por ponto. REQUISITOS_FUNCIONAIS.md e CLAUDE.md atualizados com valores corretos.

### Task 1.2 - Classe Base Character (RF02)
- **Status**: PENDENTE
- **Descricao**: Criar classe base Character com atributos, HP, Mana, posicao (front/back)
- **Criterio de aceite**: Character instanciavel com stats, calcula HP/Mana/derivados corretamente
- **Arquivos criados**: (preencher ao completar)
- **Notas**: (preencher ao completar)

### Task 1.3 - Action Economy Basica (RF03.1)
- **Status**: PENDENTE
- **Descricao**: Implementar sistema de acao normal + acao bonus + reacao por turno
- **Criterio de aceite**: Personagem pode usar 1 acao + 1 bonus + 1 reacao por turno, sistema reseta entre turnos
- **Arquivos criados**: (preencher ao completar)
- **Notas**: (preencher ao completar)

### Task 1.4 - Ordem de Turnos (RF03.2)
- **Status**: PENDENTE
- **Descricao**: Implementar sistema de iniciativa baseado em Speed
- **Criterio de aceite**: Combatentes ordenados por speed, empates resolvidos
- **Arquivos criados**: (preencher ao completar)
- **Notas**: (preencher ao completar)

### Task 1.5 - Posicionamento Front/Back (RF03.3)
- **Status**: PENDENTE
- **Descricao**: Implementar sistema de front/back line com regras de targeting
- **Criterio de aceite**: Melee so atinge front (exceto AOE), ranged atinge ambos, movimentacao funciona
- **Arquivos criados**: (preencher ao completar)
- **Notas**: (preencher ao completar)

### Task 1.6 - Ataque e Defesa Basicos (RF03.4, RF03.5)
- **Status**: PENDENTE
- **Descricao**: Implementar calculo de dano fisico/magico e defesa fisica/magica
- **Criterio de aceite**: Dano calculado corretamente com mods, defesa reduz dano, critico funciona
- **Arquivos criados**: (preencher ao completar)
- **Notas**: (preencher ao completar)

### Task 1.7 - Combat Engine Loop (RF03)
- **Status**: PENDENTE
- **Descricao**: Integrar tudo num loop de combate: iniciativa → turnos → acoes → resolucao
- **Criterio de aceite**: Combate roda do inicio ao fim (vitoria/derrota), turnos processados corretamente
- **Arquivos criados**: (preencher ao completar)
- **Notas**: (preencher ao completar)

### Task 1.8 - Fighter (Guerreiro) (RF02.3)
- **Status**: PENDENTE
- **Descricao**: Implementar classe Fighter com pontos de acao, estancias, skills basicas
- **Criterio de aceite**: Fighter tem mecanicas unicas funcionando, herda de Character sem quebrar
- **Arquivos criados**: (preencher ao completar)
- **Notas**: (preencher ao completar)

### Task 1.9 - Mage (Mago) (RF02.3)
- **Status**: PENDENTE
- **Descricao**: Implementar classe Mage com overcharge, ataque basico gera mana, barreiras
- **Criterio de aceite**: Mage tem mecanicas unicas funcionando
- **Arquivos criados**: (preencher ao completar)
- **Notas**: (preencher ao completar)

### Task 1.10 - Cleric (Clerigo) (RF02.3)
- **Status**: PENDENTE
- **Descricao**: Implementar classe Cleric com divindade, cura, buffs
- **Criterio de aceite**: Cleric cura, buffa, divindade da elemento ao ataque basico
- **Arquivos criados**: (preencher ao completar)
- **Notas**: (preencher ao completar)

### Task 1.11 - Mock Battle (Integracao)
- **Status**: PENDENTE
- **Descricao**: Rodar uma batalha completa Fighter+Mage+Cleric vs inimigos simples
- **Criterio de aceite**: Combate roda, acoes processadas, alguem vence
- **Arquivos criados**: (preencher ao completar)
- **Notas**: (preencher ao completar)

---

## Historico de Sessoes

### Sessao 1 - 2026-02-27
- Leitura completa de todos os docs de design (~60 arquivos)
- Criado CLAUDE.md com principios SOLID e Clean Code
- Criado docs/REQUISITOS_FUNCIONAIS.md (11 RFs, 4 fases)
- Criado docs/PROGRESS.md (este arquivo)
- **Decisoes**: Python 3.12+ com pytest, escopo completo focando em combate primeiro, TDD obrigatorio

### Sessao 2 - 2026-02-28

- Codigo C++ antigo movido para `legacy/`, `Coisas interessantes/` no .gitignore
- Task 1.0 concluida: pyproject.toml, estrutura de pastas, pytest funcionando
- Task 1.1 concluida: 41 testes passando (atributos primarios, thresholds, derivados)
- Correcao dos thresholds nos docs (eram 4/6/8/10/11, agora 18/22/26/30/32)
- **Decisoes**: Thresholds sao bonus EXTRAS cumulativos (cada +1 no atributo ja da bonus incremental). Funcoes de stats derivados recebem modificadores de classe via DI (nao hardcoded). Dados de threshold em JSON.
