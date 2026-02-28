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

- **Status**: CONCLUIDA
- **Descricao**: Criar classe base Character com atributos, HP, Mana, posicao (front/back)
- **Criterio de aceite**: Character instanciavel com stats, calcula HP/Mana/derivados corretamente
- **Arquivos criados**:
  - `src/core/characters/position.py` - Enum Position (FRONT/BACK)
  - `src/core/characters/class_modifiers.py` - ClassModifiers dataclass (frozen, from_json)
  - `src/core/characters/character.py` - Character base class (184 linhas, 7 metodos + 11 properties)
  - `data/classes/fighter.json` - Modificadores do Guerreiro
  - `tests/core/test_characters/test_position.py` - 3 testes
  - `tests/core/test_characters/test_class_modifiers.py` - 4 testes
  - `tests/core/test_characters/test_character.py` - 38 testes
- **Notas**: 86 testes totais passando (41 atributos + 45 characters). Character usa DI para Attributes, ClassModifiers e ThresholdCalculator. Stats derivados recalculam com threshold bonuses. Morto nao pode ser curado. ClassModifiers carrega de JSON. 184 linhas (<200), 7 metodos (<10).

### Task 1.3 - Action Economy Basica (RF03.1)

- **Status**: CONCLUIDA
- **Descricao**: Implementar sistema de acao normal + acao bonus + reacao por turno
- **Criterio de aceite**: Personagem pode usar 1 acao + 1 bonus + 1 reacao por turno, sistema reseta entre turnos
- **Arquivos criados**:
  - `src/core/combat/action_economy.py` - ActionType enum + ActionEconomy class
  - `tests/core/test_combat/test_action_economy.py` - 18 testes
- **Notas**: 104 testes totais. ActionEconomy e componente separado do Character (composicao, nao heranca). has_actions considera apenas ACTION e BONUS_ACTION (reacao e passiva). PROACTIVE_ACTIONS como frozenset para extensibilidade.

### Task 1.4 - Ordem de Turnos (RF03.2)

- **Status**: CONCLUIDA
- **Descricao**: Implementar sistema de iniciativa baseado em Speed
- **Criterio de aceite**: Combatentes ordenados por speed, empates resolvidos
- **Arquivos criados**:
  - `src/core/combat/turn_order.py` - Combatant Protocol + TurnOrder (get_order/next/reset)
  - `tests/core/test_combat/test_turn_order.py` - 12 testes
  - Adicionado `speed` property ao Character (= DEX)
- **Notas**: 117 testes totais. TurnOrder depende de Protocol Combatant (DI), nao de Character diretamente. Empates resolvidos por nome (alfabetico). Mortos excluidos da ordem. Iteracao via next() com reset() entre rodadas.

### Task 1.5 - Posicionamento Front/Back (RF03.3)
- **Status**: CONCLUIDA
- **Descricao**: Implementar sistema de front/back line com regras de targeting
- **Criterio de aceite**: Melee so atinge front (exceto AOE), ranged atinge ambos, movimentacao funciona
- **Arquivos criados**:
  - `src/core/combat/targeting.py` - AttackRange enum + Targetable Protocol + get_valid_targets()
  - `tests/core/test_combat/test_targeting.py` - 15 testes
- **Notas**: 132 testes totais. Melee so atinge front line; se nenhum front vivo, fallback para back. Ranged atinge qualquer posicao. Targetable Protocol separado do Combatant (ISP). Movimentacao ja existia via Character.change_position(). Funcao pura get_valid_targets (2 params, sem estado).

### Task 1.6 - Ataque e Defesa Basicos (RF03.4, RF03.5)
- **Status**: CONCLUIDA
- **Descricao**: Implementar calculo de dano fisico/magico e defesa fisica/magica
- **Criterio de aceite**: Dano calculado corretamente com mods, defesa reduz dano, critico funciona
- **Arquivos criados**:
  - `src/core/combat/damage.py` - DamageType enum, DamageResult frozen dataclass, resolve_damage(), calculate_crit_chance()
  - `tests/core/test_combat/test_damage.py` - 26 testes
- **Notas**: 158 testes totais. Dano = max(1, attack_power - defense). Critico multiplica attack ANTES de subtrair defesa (default 2x). Crit chance = 5% base + bonus de thresholds (DEX crit_chance_pct). DamageResult imutavel. DamageType (PHYSICAL/MAGICAL) preparado para uso futuro no combat engine. Funcoes puras sem estado.

### Task 1.7 - Combat Engine Loop (RF03)
- **Status**: CONCLUIDA
- **Descricao**: Integrar tudo num loop de combate: iniciativa → turnos → acoes → resolucao
- **Criterio de aceite**: Combate roda do inicio ao fim (vitoria/derrota), turnos processados corretamente
- **Arquivos criados**:
  - `src/core/combat/combat_engine.py` - CombatEngine, CombatResult, CombatEvent, TurnContext, TurnHandler Protocol
  - `src/core/combat/basic_attack_handler.py` - BasicAttackHandler (melee fisico padrao)
  - `tests/core/test_combat/test_combat_engine.py` - 23 testes
- **Notas**: 181 testes totais. CombatEngine integra TurnOrder + ActionEconomy + Targeting + Damage. TurnHandler Protocol (Strategy pattern) para DI de decisao de acao. BasicAttackHandler como handler concreto padrao. Suporta: rodadas, vitoria/derrota/empate, eventos registrados, mortos pulados, combate encerra mid-round. MAX_ROUNDS=100 para safety. Engine ~100 linhas, 2 metodos publicos.

### Task 1.8 - Fighter (Guerreiro) (RF02.3)
- **Status**: CONCLUIDA
- **Descricao**: Implementar classe Fighter com pontos de acao, estancias, skills basicas
- **Criterio de aceite**: Fighter tem mecanicas unicas funcionando, herda de Character sem quebrar
- **Arquivos criados**:
  - `src/core/classes/fighter/stance.py` - Stance enum + StanceModifier + load_stance_modifiers()
  - `src/core/classes/fighter/action_points.py` - ActionPoints (gain/spend/on_turn_end, limite por nivel)
  - `src/core/classes/fighter/fighter.py` - Fighter(Character) com AP, Stances, overrides de atk/def
  - `data/classes/fighter_stances.json` - Multiplicadores de estancia (atk/def)
  - `tests/core/test_classes/test_fighter/test_stance.py` - 11 testes
  - `tests/core/test_classes/test_fighter/test_action_points.py` - 17 testes
  - `tests/core/test_classes/test_fighter/test_fighter.py` - 24 testes (inclui LSP)
- **Notas**: 233 testes totais. Fighter herda de Character (LSP verificado). Estancias modificam atk/def via multiplicadores (OFFENSIVE +20%atk/-20%def, DEFENSIVE inverso). AP limite por nivel (lvl1=2, lvl5=10). Ganho passivo +1 se nao gastou no turno. Dados de estancia em JSON (data/). Stance modifiers carregados uma vez no modulo.

### Task 1.9 - Mage (Mago) (RF02.3)
- **Status**: CONCLUIDA
- **Descricao**: Implementar classe Mage com overcharge, ataque basico gera mana, barreiras
- **Criterio de aceite**: Mage tem mecanicas unicas funcionando
- **Arquivos criados**:
  - `src/core/classes/mage/overcharge.py` - OverchargeConfig frozen dataclass + load_overcharge_config()
  - `src/core/classes/mage/barrier.py` - Barrier (resource class: add/absorb, eficiencia 2:1)
  - `src/core/classes/mage/mage.py` - Mage(Character) com Overcharge, Barrier, mana generation
  - `data/classes/mage.json` - ClassModifiers do Mago (d6, mana 12, atk_mag 10, def_fis 2)
  - `data/classes/mage_overcharge.json` - Config de overcharge (1.5x atk, 30 mana/turno)
  - `tests/core/test_classes/test_mage/test_overcharge.py` - 6 testes
  - `tests/core/test_classes/test_mage/test_barrier.py` - 12 testes
  - `tests/core/test_classes/test_mage/test_mage.py` - 36 testes (LSP, stats, barrier, overcharge, mana gen)
- **Notas**: 287 testes totais (233+54). Mage herda de Character (LSP verificado). Posicao default BACK (glass cannon). Overcharge toggle: ativa/desativa, multiplica magical_attack 1.5x, custa 30 mana/turno, auto-desativa se mana insuficiente. Barrier: gasta mana para criar (eficiencia 2:1), absorve dano antes do HP via take_damage override. Mana por ataque basico: MIND * 3. Dados de balanceamento em JSON (data/). Mage.py ~90 linhas, 7 metodos.

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
- Task 1.2 concluida: 45 testes novos (86 total). Character com DI, ClassModifiers frozen, Position enum.
- **Decisoes**: ClassModifiers agrupa 10+ mods numa dataclass frozen (respeita max 3 params). Threshold bonuses somam de todos os atributos e modificam os mods da classe. Morto nao revive com heal. Weapon die = 0 por enquanto (armas sao task futura).
- Task 1.3 concluida: 18 testes novos (104 total). ActionEconomy como componente separado em combat/.
- **Decisoes**: ActionEconomy e composicao (nao acoplado ao Character). has_actions ignora REACTION (e passiva, nao proativa). PROACTIVE_ACTIONS como frozenset.
- Task 1.4 concluida: 13 testes novos (117 total). TurnOrder com Protocol Combatant, speed property no Character.
- **Decisoes**: TurnOrder usa Protocol Combatant (DI), nao depende de Character. Speed = DEX por enquanto. Empates por nome. Mortos excluidos automaticamente.
