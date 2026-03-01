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
- **Status**: CONCLUIDA
- **Descricao**: Implementar classe Cleric com divindade, cura, buffs
- **Criterio de aceite**: Cleric cura, buffa, divindade da elemento ao ataque basico
- **Arquivos criados**:
  - `src/core/classes/cleric/divinity.py` - Divinity enum (7 divindades) + DivinityConfig frozen + load_divinity_configs()
  - `src/core/classes/cleric/holy_power.py` - HolyPower (resource: gain/spend, limite 5)
  - `src/core/classes/cleric/cleric.py` - Cleric(Character) com Divinity, HolyPower, Healing, Channel Divinity
  - `data/classes/cleric.json` - ClassModifiers do Clerigo (d8, atk_mag 8, def_mag 4)
  - `data/classes/cleric_divinities.json` - Config de 7 divindades (healing_bonus: Holy=1.3, Chaos=0.8)
  - `tests/core/test_classes/test_cleric/test_divinity.py` - 11 testes
  - `tests/core/test_classes/test_cleric/test_holy_power.py` - 12 testes
  - `tests/core/test_classes/test_cleric/test_cleric.py` - 37 testes (LSP, stats, divinity, healing, channel divinity)
- **Notas**: 347 testes totais (287+60). Cleric herda de Character (LSP verificado). Posicao default BACK. Divindade define healing_bonus (Holy 1.3x, Chaos 0.8x). HolyPower ganho ao curar (+1 por heal), gasto em Channel Divinity (custo 3). Healing: gasta 30 mana, cura target por WIS*3*divinity_bonus. Channel Divinity: toggle self-buff, magical_attack e magical_defense *1.3. Cleric.py ~90 linhas, 6 metodos.

### Task 1.11 - Mock Battle (Integracao)
- **Status**: CONCLUIDA
- **Descricao**: Rodar uma batalha completa Fighter+Mage+Cleric vs inimigos simples
- **Criterio de aceite**: Combate roda, acoes processadas, alguem vence
- **Arquivos criados**:
  - `src/core/combat/dispatch_handler.py` - DispatchTurnHandler (mapeia nome->handler, Strategy+Composite)
  - `tests/core/test_combat/test_dispatch_handler.py` - 4 testes (dispatch, fallback, multiplos handlers)
  - `tests/core/test_combat/test_mock_battle.py` - 9 testes integracao (combate completo, eventos, mecanicas)
- **Notas**: 360 testes totais (347+13). DispatchTurnHandler resolve o problema de handlers por classe sem isinstance (respeita OCP). Mock battle: Fighter(front/melee) + Mage(back/barrier+magic) + Cleric(back/heal+magic) vs 3 Goblins. Combate roda ate vitoria/derrota, eventos registram todas as classes, Mage cria barrier no round 1, Cleric cura aliados feridos e ganha holy power. Handlers de teste inline (MageCombatHandler, ClericCombatHandler) - IA real vem em RF09.

---

## Fase Atual: FASE 2 - Profundidade

### Bloco A - Sistemas Base (antes das classes)

#### Task 2.0 - Effects Framework (base para Buffs/Debuffs/Ailments)
- **Status**: PENDENTE
- **Descricao**: Criar framework generico de efeitos temporarios com duracao em turnos (Strategy pattern)
- **Criterio de aceite**: Effect base class com apply/tick/expire, EffectManager que gerencia efeitos ativos num personagem, integracao com turno (tick no inicio do turno, expire automatico)
- **Dependencias**: Nenhuma (base para tudo da Fase 2)

#### Task 2.1 - Buffs e Debuffs (RF05.1, RF05.2)
- **Status**: PENDENTE
- **Descricao**: Implementar buffs flat/percentuais e debuffs com duracao em turnos
- **Criterio de aceite**: Buff que modifica stats (ex: +2 STR, +10% ataque), debuff que reduz stats, stacking rules, duracao em turnos com expire automatico
- **Dependencias**: Task 2.0

#### Task 2.2 - Status Ailments (RF05.3)
- **Status**: PENDENTE
- **Descricao**: Implementar status ailments (DoTs, CC, debuffs de recurso)
- **Criterio de aceite**: DoTs (Burn, Poison, Bleed), CC (Freeze, Paralysis), debuffs de recurso (Amnesia, Sickness), aplicacao e remocao funcionando
- **Dependencias**: Task 2.0

#### Task 2.3 - Sistema Elemental (RF04.1)
- **Status**: PENDENTE
- **Descricao**: Implementar enum de elementos, efeitos on-hit por elemento, fraquezas/resistencias
- **Criterio de aceite**: ElementType enum (10 elementos), cada elemento com efeito on-hit, DamageResult integrado com elemento, fraqueza/resistencia modificam dano
- **Dependencias**: Task 2.2 (efeitos on-hit aplicam ailments)

#### Task 2.4 - Integracao Effects + Combat Engine
- **Status**: PENDENTE
- **Descricao**: Integrar EffectManager no loop de combate (tick/expire por turno) e elemental no dano
- **Criterio de aceite**: Efeitos tickam no inicio do turno, expiram automaticamente, dano elemental aplica efeitos on-hit, mock battle com elementos
- **Dependencias**: Tasks 2.0-2.3

### Bloco B - 10 Classes Restantes (RF02.3)

#### Task 2.5 - Barbarian (Barbaro)
- **Status**: PENDENTE
- **Descricao**: Barra de Furia, dano por HP perdido, rage como buff temporal
- **Dependencias**: Task 2.1 (Furia = buff)

#### Task 2.6 - Paladin (Paladino)
- **Status**: PENDENTE
- **Descricao**: Divindade, Juramentos stack, Glimpse of Glory, auras como buffs persistentes
- **Dependencias**: Task 2.1 (auras = buffs)

#### Task 2.7 - Ranger
- **Status**: PENDENTE
- **Descricao**: Foco Predatorio (stack crit), Marca do Cacador (debuff no alvo)
- **Dependencias**: Task 2.1 (marca = debuff)

#### Task 2.8 - Monk (Monge)
- **Status**: PENDENTE
- **Descricao**: Barra Equilibrium (Vitalidade/Destruicao), multi-hit, debuffs
- **Dependencias**: Task 2.1

#### Task 2.9 - Sorcerer (Feiticeiro)
- **Status**: PENDENTE
- **Descricao**: Metamagia, Overcharged, Rotacao de Mana
- **Dependencias**: Task 2.0

#### Task 2.10 - Warlock (Bruxo)
- **Status**: PENDENTE
- **Descricao**: Insanidade (ailment proprio), Familiares, Sede Insaciavel
- **Dependencias**: Task 2.2 (insanidade = ailment)

#### Task 2.11 - Druid (Druida)
- **Status**: PENDENTE
- **Descricao**: Transformacoes, condicoes de campo
- **Dependencias**: Tasks 2.1, 2.3 (campo = buff/debuff elemental)

#### Task 2.12 - Rogue (Ladino)
- **Status**: PENDENTE
- **Descricao**: Usa itens sem gastar turno, mistura itens, utility
- **Dependencias**: Task 2.0

#### Task 2.13 - Bard (Bardo)
- **Status**: PENDENTE
- **Descricao**: Embalo Musical (stack buff), recruta NPCs, buff/debuff
- **Dependencias**: Task 2.1 (embalo = buff stacking)

#### Task 2.14 - Artificer (Artifice)
- **Status**: PENDENTE
- **Descricao**: Traje Tecmagis, potencializa itens ativos, suporte/mana
- **Dependencias**: Task 2.0

### Bloco C - Equipamento e Progressao

#### Task 2.15 - Sistema de Armas (RF07.1)
- **Status**: PENDENTE
- **Descricao**: Weapon base, dados de dano por tipo, proficiencia por classe, armas normais/magicas
- **Dependencias**: Bloco B (proficiencias por classe)

#### Task 2.16 - Armaduras e Acessorios (RF07.2, RF07.3)
- **Status**: PENDENTE
- **Descricao**: Armaduras leve/media/pesada, acessorios com buffs, limite por CHA
- **Dependencias**: Task 2.15

#### Task 2.17 - Consumiveis e Inventario (RF07.4, RF07.5)
- **Status**: PENDENTE
- **Descricao**: Pocoes, itens de combate, inventario com slots, equip/desequip
- **Dependencias**: Task 2.16

#### Task 2.18 - Level Up e Progressao (RF08.1, RF08.2)
- **Status**: PENDENTE
- **Descricao**: XP, level 1-10, pontos de atributo, HP/mana scaling, proficiency bonus = nivel
- **Dependencias**: Bloco B

#### Task 2.19 - Mock Battle v2 (Integracao Fase 2)
- **Status**: PENDENTE
- **Descricao**: Batalha completa com elementos, buffs/debuffs, mais classes, equipamento
- **Criterio de aceite**: Combate com 6+ classes, efeitos elementais, buffs/debuffs ativos, combat log mostrando tudo
- **Dependencias**: Todas as tasks anteriores

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
