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
- **Status**: CONCLUIDA
- **Descricao**: Criar framework generico de efeitos temporarios com duracao em turnos (Strategy pattern)
- **Criterio de aceite**: Effect base class com apply/tick/expire, EffectManager que gerencia efeitos ativos num personagem, integracao com turno (tick no inicio do turno, expire automatico)
- **Dependencias**: Nenhuma (base para tudo da Fase 2)
- **Arquivos criados**:
  - `src/core/effects/modifiable_stat.py` - ModifiableStat enum (9 stats derivados modificaveis)
  - `src/core/effects/stat_modifier.py` - StatModifier frozen dataclass (flat + percent)
  - `src/core/effects/tick_result.py` - TickResult frozen dataclass (damage, healing, mana_change)
  - `src/core/effects/stacking.py` - StackingPolicy enum (REPLACE, STACK, REFRESH)
  - `src/core/effects/effect.py` - Effect ABC com Template Method lifecycle (apply/tick/expire)
  - `src/core/effects/effect_manager.py` - EffectManager com stacking rules e modifier aggregation
  - `tests/core/test_effects/test_modifiable_stat.py` - 9 testes
  - `tests/core/test_effects/test_stat_modifier.py` - 7 testes
  - `tests/core/test_effects/test_tick_result.py` - 5 testes
  - `tests/core/test_effects/test_stacking.py` - 3 testes
  - `tests/core/test_effects/test_effect.py` - 20 testes
  - `tests/core/test_effects/test_effect_manager.py` - 30 testes
- **Notas**: 468 testes totais (394+74). Effect ABC define lifecycle hooks (on_apply, _do_tick, on_expire, get_modifiers). EffectManager gerencia stacking (REPLACE/STACK/REFRESH), tick_all, aggregate_modifier. Guard contra on_expire duplo via _expire_handled flag. StatModifier formula: final = (base + flat) * (1.0 + percent/100). PERMANENT_DURATION = -1 para efeitos sem expiracao.

#### Task 2.1 - Buffs e Debuffs (RF05.1, RF05.2)
- **Status**: CONCLUIDA
- **Descricao**: Implementar buffs flat/percentuais e debuffs com duracao em turnos
- **Criterio de aceite**: Buff que modifica stats (ex: +2 STR, +10% ataque), debuff que reduz stats, stacking rules, duracao em turnos com expire automatico
- **Dependencias**: Task 2.0
- **Arquivos criados**:
  - `src/core/effects/effect_category.py` - EffectCategory enum (BUFF, DEBUFF)
  - `src/core/effects/stat_buff.py` - StatBuff(Effect) com validacao, nome e stacking key auto-gerados
  - `src/core/effects/stat_debuff.py` - StatDebuff(Effect) espelho com validacao invertida
  - `src/core/effects/buff_factory.py` - 4 factory functions ergonomicas (create_flat_buff, etc)
  - `tests/core/test_effects/test_effect_category.py` - 3 testes
  - `tests/core/test_effects/test_stat_buff.py` - 22 testes (criacao, validacao, properties, behavior, manager)
  - `tests/core/test_effects/test_stat_debuff.py` - 22 testes (espelho do buff)
  - `tests/core/test_effects/test_buff_factory.py` - 16 testes (4 factories x 4 testes)
- **Notas**: 531 testes totais (468+63). StatBuff valida flat/percent >= 0, StatDebuff valida <= 0. Nomes auto-gerados ("Physical Attack Up"/"Down"). Stacking keys auto-gerados ("buff_speed"/"debuff_speed", com source opcional). Factory de debuff recebe valores positivos e nega internamente. _format_stat_name e _validate_duration compartilhados entre StatBuff e StatDebuff. Escopo: apenas stat buffs/debuffs. Buffs comportamentais (Haste, Angel Idol, Moral) ficam para tasks futuras.

#### Task 2.2 - Status Ailments (RF05.3)
- **Status**: CONCLUIDA
- **Descricao**: Implementar status ailments (DoTs, CC, debuffs de recurso)
- **Criterio de aceite**: DoTs (Burn, Poison, Bleed), CC (Freeze, Paralysis), debuffs de recurso (Amnesia, Sickness), aplicacao e remocao funcionando
- **Dependencias**: Task 2.0
- **Arquivos modificados**:
  - `src/core/effects/effect_category.py` - Adicionado AILMENT ao enum
  - `src/core/effects/tick_result.py` - Adicionado skip_turn: bool = False
  - `src/core/effects/modifiable_stat.py` - Adicionado HEALING_RECEIVED
- **Arquivos criados**:
  - `src/core/effects/ailments/__init__.py` - Package marker
  - `src/core/effects/ailments/status_ailment.py` - StatusAilment ABC (category=AILMENT, stacking_key=ailment_{id})
  - `src/core/effects/ailments/dot_ailment.py` - DotAilment ABC (damage_per_tick, _do_tick)
  - `src/core/effects/ailments/cc_ailment.py` - CcAilment ABC (is_crowd_control)
  - `src/core/effects/ailments/debuff_ailment.py` - DebuffAilment ABC (modifier validation, get_modifiers)
  - `src/core/effects/ailments/resource_lock_ailment.py` - ResourceLockAilment ABC (blocks_mana/aura)
  - `src/core/effects/ailments/poison.py` - Poison DoT
  - `src/core/effects/ailments/virus.py` - Virus DoT (Poison potencializado)
  - `src/core/effects/ailments/bleed.py` - Bleed DoT
  - `src/core/effects/ailments/burn.py` - Burn DoT + reducao de cura (HEALING_RECEIVED)
  - `src/core/effects/ailments/scorch.py` - Scorch DoT + reducao de MAX_HP (cumulativo)
  - `src/core/effects/ailments/freeze.py` - Freeze CC (skip_turn=True + HEALING_RECEIVED)
  - `src/core/effects/ailments/paralysis.py` - Paralysis CC (chance-based skip, random injetavel)
  - `src/core/effects/ailments/cold.py` - Cold debuff (SPEED)
  - `src/core/effects/ailments/weakness.py` - Weakness debuff (PHYS_DEF + MAG_DEF)
  - `src/core/effects/ailments/injury.py` - Injury debuff (PHYS_ATK + MAG_ATK)
  - `src/core/effects/ailments/sickness.py` - Sickness debuff (HEALING_RECEIVED)
  - `src/core/effects/ailments/amnesia.py` - Amnesia lock (blocks mana skills)
  - `src/core/effects/ailments/curse.py` - Curse lock (blocks aura skills)
  - `src/core/effects/ailments/ailment_factory.py` - 13 factory functions
  - `tests/core/test_effects/test_ailments/` - 19 arquivos de teste
- **Notas**: 703 testes totais (531+172). Hierarquia: StatusAilment -> DotAilment/CcAilment/DebuffAilment/ResourceLockAilment -> 13 concretos. 3 arquivos existentes modificados (1 campo/membro cada). Burn e Scorch combinam DoT + get_modifiers (dual behavior). Freeze sempre pula turno. Paralysis com random injetavel para testes deterministicos. Weakness/Injury afetam ambos phys+mag. TickResult.skip_turn e ModifiableStat.HEALING_RECEIVED preparados para integracao com combat engine (Task 2.4).

#### Task 2.3 - Sistema Elemental (RF04.1 + RF04.2)
- **Status**: CONCLUIDA
- **Descricao**: Implementar enum de elementos, efeitos on-hit por elemento, fraquezas/resistencias
- **Criterio de aceite**: ElementType enum (10 elementos), cada elemento com efeito on-hit, ElementalDamageResult com fraqueza/resistencia modificando dano
- **Dependencias**: Task 2.2 (efeitos on-hit aplicam ailments)
- **Arquivos criados**:
  - `src/core/elements/element_type.py` - ElementType enum (10 elementos: FIRE, WATER, ICE, LIGHTNING, EARTH, HOLY, DARKNESS, CELESTIAL, PSYCHIC, FORCE)
  - `src/core/elements/elemental_profile.py` - ElementalProfile frozen dataclass (fraquezas/resistencias via multiplier 0.0-2.0)
  - `src/core/elements/elemental_damage.py` - ElementalDamageResult wrapping DamageResult + resolve_elemental_damage()
  - `src/core/elements/on_hit/__init__.py` - Package marker
  - `src/core/elements/on_hit/on_hit_result.py` - OnHitResult frozen dataclass (effects, self_effects, bonus_damage, party_healing, breaks_shield)
  - `src/core/elements/on_hit/on_hit_config.py` - OnHitConfig + EffectSpec frozen dataclasses + load_on_hit_configs() do JSON
  - `src/core/elements/on_hit/on_hit_generator.py` - generate_on_hit() com dispatch table de factories
  - `src/core/effects/ailments/confusion.py` - Confusion CcAilment (redirects_target=True, nao pula turno)
  - `data/elements/elemental_profiles.json` - Profiles de fraqueza/resistencia (neutral, fire_creature, undead, etc)
  - `data/elements/on_hit_defaults.json` - Config data-driven dos 10 on-hits elementais
  - `tests/core/test_elements/` - 6 arquivos de teste
  - `tests/core/test_effects/test_ailments/test_confusion.py` - 12 testes do Confusion
- **Arquivos modificados**:
  - `src/core/effects/ailments/ailment_factory.py` - Adicionado create_confusion() (+5 linhas)
  - `tests/core/test_effects/test_ailments/test_ailment_factory.py` - Adicionado TestCreateConfusion (+2 testes)
- **Notas**: 811 testes totais (703+108). Abordagem DATA-DRIVEN para on-hits: configs em JSON, dispatch table de factories no generator. Nenhuma classe por elemento - cada on-hit e composicao de ailments/buffs existentes. **Decisao catalogada**: Se no futuro algum elemento precisar de logica condicional complexa, podemos extrair para classes concretas com OnHitProvider Protocol sem quebrar o existente. ElementalDamageResult WRAPS DamageResult (OCP - resolve_damage() e DamageResult intocados). ElementType separado de Divinity do Cleric (conceitos diferentes, mapeamento futuro). Confusion e unico ailment novo (CcAilment com redirects_target, diferente de Freeze/Paralysis). Darkness reusa Burn mecanicamente (description distingue).

#### Task 2.4 - Integracao Effects + Combat Engine

- **Status**: CONCLUIDA
- **Descricao**: Integrar EffectManager no loop de combate (tick/expire por turno) e elemental no dano
- **Criterio de aceite**: Efeitos tickam no inicio do turno, expiram automaticamente, dano elemental aplica efeitos on-hit, mock battle com elementos
- **Dependencias**: Tasks 2.0-2.3
- **Arquivos modificados**:
  - `src/core/characters/character.py` - EffectManager composicao interna, ElementalProfile kwarg, _apply_effect_modifiers(), 8 stat properties modificadas
  - `src/core/combat/combat_engine.py` - Effect tick phase no inicio do turno, _execute_handler() extraido, _log_skip(), effect_log property
  - `src/core/combat/combat_log.py` - 5 novos EventTypes (EFFECT_APPLY, EFFECT_TICK, EFFECT_EXPIRE, ELEMENTAL_DAMAGE, SKIP_TURN)
  - `src/core/combat/log_formatter.py` - 5 novos templates de texto
- **Arquivos criados**:
  - `src/core/combat/effect_phase.py` - Funcoes puras: process_effect_ticks(), apply_tick_results(), should_skip_turn(), EffectLogEntry dataclass
  - `src/core/combat/elemental_attack.py` - ElementalAttackOutcome, resolve_elemental_attack(), apply_on_hit_effects()
  - `tests/core/test_characters/test_character_effects.py` - 18 testes (EffectManager, stat modifiers, subclass interaction)
  - `tests/core/test_combat/test_effect_phase.py` - 21 testes (tick processing, apply results, skip turn)
  - `tests/core/test_combat/test_combat_log_effects.py` - 10 testes (novos EventTypes + formatter templates)
  - `tests/core/test_combat/test_combat_engine_effects.py` - 16 testes (DoT, CC, duration, buffs, regressao)
  - `tests/core/test_combat/test_elemental_attack.py` - 14 testes (resistencia, on-hit, apply effects)
  - `tests/core/test_combat/test_mock_battle_elemental.py` - 12 testes (batalha 3v3 com elementos, DoT, Freeze, party healing)
- **Notas**: 902 testes totais (811+91). EffectLogEntry separado de CombatLogEntry para evitar import circular (combat_engine → effect_phase → combat_log → combat_engine). Stat modifier order: base → effect_mods → class_multiplier. Efeitos tickam no INICIO do turno (DoT antes de agir, CC impede acao). CombatEngine NAO sabe de elementos (SRP) - handlers decidem tipo de ataque. elemental_attack.py conecta damage + resistencia + on-hit em funcoes puras. Character class body = 198 linhas (<200).

### Bloco B - Armas e Progressao (C-lite, antes das classes)

#### Task 2.5 - Sistema de Armas (RF07.1)
- **Status**: CONCLUIDA
- **Descricao**: Weapon base, dados de dano por tipo, categorias (simples/marcial/magica), armas normais e elementais
- **Dependencias**: Tasks 2.0-2.3 (armas elementais usam ElementType)
- **Arquivos criados**:
  - `src/core/items/damage_kind.py` - DamageKind enum (SLASHING, PIERCING, BLUDGEONING)
  - `src/core/items/weapon_type.py` - WeaponType enum (SWORD, DAGGER, BOW, STAFF, HAMMER, LANCE, MACE, FIST)
  - `src/core/items/weapon_category.py` - WeaponCategory enum (SIMPLE, MARTIAL, MAGICAL)
  - `src/core/items/weapon_rarity.py` - WeaponRarity enum (COMMON, UNCOMMON, RARE, LEGENDARY)
  - `src/core/items/weapon.py` - Weapon frozen dataclass + from_dict() (Enum[name] parsing)
  - `src/core/items/weapon_loader.py` - load_weapons() usando resolve_data_path()
  - `src/core/items/weapon_proficiency.py` - can_equip() + FIGHTER/MAGE/CLERIC/DEFAULT proficiencies
  - `data/weapons/weapons.json` - 15 armas (11 common + 4 uncommon elementais)
  - `tests/core/test_items/conftest.py` - Fixtures compartilhadas (LONGSWORD, ARCANE_STAFF, make_attrs, make_item_config)
  - `tests/core/test_items/test_damage_kind.py` - 4 testes
  - `tests/core/test_items/test_weapon_type.py` - 4 testes
  - `tests/core/test_items/test_weapon_category.py` - 4 testes
  - `tests/core/test_items/test_weapon_rarity.py` - 4 testes
  - `tests/core/test_items/test_weapon.py` - 13 testes (criacao, frozen, from_dict, defaults, invalid)
  - `tests/core/test_items/test_weapon_loader.py` - 8 testes
  - `tests/core/test_items/test_weapon_proficiency.py` - 9 testes
  - `tests/core/test_items/test_weapon_equip.py` - 10 testes (equip/unequip, LSP subclasses)
  - `tests/core/test_items/test_weapon_stats.py` - 10 testes (weapon_die routing)
  - `tests/core/test_items/test_weapon_combat_integration.py` - 7 testes (armed vs unarmed, elemental, battle)
- **Arquivos modificados**:
  - `src/core/characters/character_config.py` - Adicionado weapon: Weapon | None = None
  - `src/core/characters/character.py` - Adicionado _weapon no __init__
  - `src/core/characters/combat_stats_mixin.py` - weapon property, equip/unequip, _get_weapon_die() routing
- **Notas**: 1035 testes totais (902+133), 100% cobertura (1752 stmts). weapon_die routing: arma PHYSICAL adiciona die a physical_attack, MAGICAL a magical_attack, sem arma = 0 (backward-compatible). Proficiencias genericas por classe (FIGHTER={SIMPLE,MARTIAL}, MAGE={SIMPLE,MAGICAL}, CLERIC={SIMPLE}). Refactor gate: weapon methods movidos de Character para CombatStatsMixin (Character ficou com 10 metodos, dentro do limite). Conftest compartilhado eliminou duplicacao nos 3 test files.

#### Task 2.6 - Level Up e Progressao (RF08.1, RF08.2)
- **Status**: CONCLUIDA
- **Descricao**: XP, level 1-10, pontos de atributo, HP/mana scaling, proficiency bonus = nivel
- **Dependencias**: Bloco A
- **Arquivos criados**:
  - `data/progression/xp_table.json` - Thresholds XP para levels 1-10 (0, 100, 300, ..., 4500)
  - `data/progression/attribute_points.json` - Pontos fisicos/mentais por nivel (pares ganham pontos, impares reservados para subclasses)
  - `src/core/progression/xp_table.py` - XpTable frozen dataclass + level_for_xp() + load_xp_table()
  - `src/core/progression/level_up_result.py` - LevelUpResult frozen dataclass (new_level, physical/mental points)
  - `src/core/progression/attribute_point_config.py` - LevelAttributePoints frozen + get_points_for_level() + load_attribute_points()
  - `src/core/progression/level_up_system.py` - LevelUpSystem orquestrador (gain_xp, distribute_physical/mental_points)
  - `tests/core/test_progression/conftest.py` - Fixtures compartilhadas (SIMPLE_MODS, EMPTY_THRESHOLDS, make_attrs)
  - `tests/core/test_progression/test_xp_table.py` - 13 testes
  - `tests/core/test_progression/test_attribute_point_config.py` - 12 testes
  - `tests/core/test_progression/test_level_up_result.py` - 4 testes
  - `tests/core/test_progression/test_level_up_system.py` - 15 testes
  - `tests/core/test_progression/test_character_hooks.py` - 10 testes
  - `tests/core/test_progression/test_level_up_integration.py` - 10 testes (Fighter/Mage/Cleric level up)
- **Arquivos modificados**:
  - `src/core/attributes/derived_stats.py` - HP acumulativo: `base * (level+1) * mod_hp`, regen scaling com level
  - `src/core/characters/character.py` - `_set_level()` + `on_level_up()` hook (Template Method), removidos `add_effect`/`has_active_effects` (delegacao desnecessaria)
  - `src/core/characters/combat_stats_mixin.py` - `proficiency_bonus` property, level passado para regen
  - `src/core/classes/fighter/action_points.py` - `update_limit(level)` method
  - `src/core/classes/fighter/fighter.py` - `on_level_up()` override (atualiza AP limit)
  - `tests/core/test_attributes/test_derived_stats.py` - Testes de HP acumulativo e regen scaling
  - `tests/core/test_characters/test_character.py` - Adaptado para HP acumulativo e effect_manager direto
- **Notas**: 1103 testes totais (1035+68), 100% cobertura (1872 stmts). HP formula: `(hit_dice + CON + vida_mod) * (level+1) * mod_hp` (level 1 = base*2, backward-compatible). Regen: `CON * level * mod`. Proficiency bonus = level. XP table data-driven do JSON (sem formula nos docs). LevelUpSystem externo ao Character (SRP — Character nao sabe de XP). Pontos de atributo: fisicos (STR/DEX/CON) e mentais (INT/WIS/CHA/MIND), distribuicao livre dentro da categoria. Niveis impares = 0 pontos (reservados para subclasses/talentos). on_level_up() como Template Method hook: Fighter atualiza AP limit, base e noop.

### Bloco C - 10 Classes Restantes (RF02.3)

#### Task 2.7 - Barbarian (Barbaro)
- **Status**: CONCLUIDA
- **Descricao**: Barra de Furia, dano por HP perdido, fury passiva (ataque e regen)
- **Dependencias**: Task 2.1 (Furia = buff), Task 2.5 (armas)
- **Arquivos criados**:
  - `src/core/classes/barbarian/__init__.py` - Package marker
  - `src/core/classes/barbarian/fury_config.py` - FuryConfig frozen dataclass + load_fury_config()
  - `src/core/classes/barbarian/fury_bar.py` - FuryBar resource (gain/spend/decay/update_max)
  - `src/core/classes/barbarian/barbarian.py` - Barbarian(Character) com fury, missing HP bonus, overrides
  - `data/classes/barbarian.json` - ClassModifiers (d12, high phys atk/def, low mana)
  - `data/classes/barbarian_fury.json` - Config de furia (ratios, bonuses, decay)
  - `tests/core/test_classes/test_barbarian/test_fury_config.py` - 9 testes
  - `tests/core/test_classes/test_barbarian/test_fury_bar.py` - 16 testes
  - `tests/core/test_classes/test_barbarian/test_barbarian.py` - 29 testes (LSP, fury on damage, fury on attack, decay, atk bonus, missing HP bonus, regen bonus, level up)
- **Notas**: 1157 testes totais (1103+54), 99% cobertura (1958 stmts). Barbarian herda de Character (LSP verificado). FuryBar: max = 25% do max_hp, ganha fury ao receber dano (10% do dano) e ao atacar (+5 flat), decai 3/turno. Fury passiva: escala linear ate +30% physical_attack e +20% hp_regen no max. Missing HP bonus: +25% physical_attack quando quase morto (linear com % de HP faltando). physical_attack override combina fury_mult * missing_mult. on_level_up recalcula fury max. Dados de balanceamento em JSON. Barbarian.py ~73 linhas, 7 metodos. Refactor gate: PASSED (1 MEDIUM corrigido: unused import).

#### Task 2.8 - Paladin (Paladino)
- **Status**: CONCLUIDA
- **Descricao**: Divine Favor, Auras (PROTECTION/ATTACK/VITALITY), Glimpse of Glory
- **Dependencias**: Task 2.1 (auras = buffs)
- **Arquivos criados**:
  - `src/core/classes/paladin/__init__.py` - Package marker
  - `src/core/classes/paladin/divine_favor.py` - DivineFavor resource (gain/spend/max_stacks)
  - `src/core/classes/paladin/aura.py` - Aura enum + AuraModifier frozen + load_aura_modifiers()
  - `src/core/classes/paladin/glory_config.py` - GloryConfig frozen + load_glory_config()
  - `src/core/classes/paladin/paladin.py` - Paladin(Character) com auras, favor, glory
  - `data/classes/paladin.json` - ClassModifiers (d10, balanced atk/def)
  - `data/classes/paladin_auras.json` - Multiplicadores por aura (NONE/PROTECTION/ATTACK/VITALITY)
  - `data/classes/paladin_glory.json` - Config de Glimpse of Glory (custo, duracao, boost)
  - `tests/core/test_classes/test_paladin/test_divine_favor.py` - 9 testes
  - `tests/core/test_classes/test_paladin/test_aura.py` - 11 testes
  - `tests/core/test_classes/test_paladin/test_glory_config.py` - 5 testes
  - `tests/core/test_classes/test_paladin/test_paladin.py` - 41 testes (LSP, stats, auras, favor, glory, duration)
- **Notas**: 1225 testes totais (1157+66+2 extras do barbarian coverage), 100% cobertura (2090 stmts). Paladin herda de Character (LSP verificado). DivineFavor: max 10 stacks, ganha +1 ao proteger/buffar/curar aliados (API pronta, handlers futuros). Aura: apenas 1 ativa por vez, PROTECTION +15% def, ATTACK +15% atk, VITALITY +15% regen. Glimpse of Glory: custo 5 favor, dobra bonus da aura (15%->30%), dura 3 turnos, auto-desativa. Aura afetando party = fora do escopo (combat handler futuro). Refactor gate: GloryConfig extraido para arquivo proprio (HIGH corrigido). Paladin.py ~100 linhas, 10 metodos.

#### Task 2.9 - Ranger
- **Status**: CONCLUIDA
- **Descricao**: Foco Predatorio (stack crit), Marca do Cacador (debuff no alvo)
- **Dependencias**: Task 2.1 (marca = debuff)
- **Arquivos criados**:
  - `src/core/classes/ranger/__init__.py` - Package marker
  - `src/core/classes/ranger/predatory_focus_config.py` - PredatoryFocusConfig frozen + loader
  - `src/core/classes/ranger/predatory_focus.py` - PredatoryFocus resource (gain/lose/decay)
  - `src/core/classes/ranger/hunters_mark.py` - HuntersMark + HuntersMarkConfig + loader
  - `src/core/classes/ranger/ranger.py` - Ranger(Character) com focus, mark, crit bonuses
  - `data/classes/ranger.json` - ClassModifiers (d10, atk 8/8, def 3/3)
  - `data/classes/ranger_focus.json` - Focus config (20 stacks, +2/hit, -4/miss, 2% crit/stack)
  - `data/classes/ranger_mark.json` - Mark config (20% armor penetration)
  - `tests/core/test_classes/test_ranger/` - 4 arquivos, 63 testes
- **Notas**: 1288 testes totais, 100% cobertura. PredatoryFocus: stacks que crescem ao acertar (+2), perdem ao errar (-4), decaem por turno (-1). Cada stack da +2% crit chance, +5% crit damage, +0.5% physical_attack. HuntersMark: marca 1 alvo, 20% armor penetration. Crit bonuses expostos como properties para o combat handler. Refactor gate: PASSED (0 issues).

#### Task 2.10 - Monk (Monge)
- **Status**: CONCLUIDA
- **Descricao**: Barra Equilibrium (Vitalidade/Destruicao), multi-hit, debuffs
- **Dependencias**: Task 2.1
- **Arquivos criados**:
  - `src/core/classes/monk/__init__.py` - Package marker
  - `src/core/classes/monk/equilibrium_config.py` - EquilibriumConfig frozen (15 campos) + loader
  - `src/core/classes/monk/equilibrium_bar.py` - EquilibriumState enum + EquilibriumBar resource
  - `src/core/classes/monk/monk.py` - Monk(Character) com equilibrium, multi-hit, crit/debuff bonuses
  - `data/classes/monk.json` - ClassModifiers (d10, atk 6/5, def 4/4)
  - `data/classes/monk_equilibrium.json` - Equilibrium config (100 max, zones 33/67, bonuses)
  - `tests/core/test_classes/test_monk/` - 4 arquivos, 81 testes
- **Notas**: 1369 testes totais, 100% cobertura (2343 stmts). EquilibriumBar bidirecional: 0=full Vitality, 50=center, 100=full Destruction. Tres zonas: Vitality (+20% def, +15% regen), Balanced (+8% atk/def), Destruction (+25% atk, +15% crit, +1 hit). Intensidades escalam linearmente dentro de cada zona. Multi-hit: base 2, +1 em Destruction (3 total). mod_atk_physical=6 (menor que Fighter/Barbarian) porque multi-hit compensa. Debuff chance exposta pro combat handler (max 30%). Refactor gate: PASSED (0 issues).

#### Task 2.11 - Sorcerer (Feiticeiro)
- **Status**: CONCLUIDA
- **Descricao**: Metamagia, Overcharged, Rotacao de Mana
- **Dependencias**: Task 2.0
- **Arquivos criados**:
  - `src/core/classes/sorcerer/__init__.py` - Package marker
  - `src/core/classes/sorcerer/overcharged_config.py` - OverchargedConfig frozen + loader
  - `src/core/classes/sorcerer/mana_rotation.py` - ManaRotationConfig frozen + ManaRotation resource bar
  - `src/core/classes/sorcerer/sorcerer.py` - Sorcerer(Character) com overcharged, metamagia, mana rotation
  - `data/classes/sorcerer.json` - ClassModifiers (d6, atk_mag 12, def_fis 2, mana 14)
  - `data/classes/sorcerer_overcharged.json` - Config overcharged (1.8x atk, 40 mana/turno, 5% self-damage, 15 metamagic cost, 10% born_of_magic)
  - `data/classes/sorcerer_mana_rotation.json` - Config rotacao (8% gain, 5 decay, 20% max)
  - `tests/core/test_classes/test_sorcerer/` - 4 arquivos, 67 testes
- **Notas**: 1436 testes totais (1369+67), 100% cobertura (2466 stmts). Sorcerer herda de Character (LSP verificado). Posicao default BACK (glass cannon). Overcharged: 1.8x magical_attack + 40 mana/turno + 5% max_hp self-damage, auto-desativa se mana insuficiente. Metamagia: troca elemento do ataque por 15 mana, consume_metamagic() retorna e limpa. Born of Magic passiva: +10% magical_attack permanente. Mana Rotation: 8% do dano magico vira mana, armazena ate 20% do max_mana, decai 5/turno. on_level_up recalcula rotation max. Refactor gate: PASSED (1 HIGH corrigido: unused import).

#### Task 2.12 - Warlock (Bruxo)
- **Status**: CONCLUIDA
- **Descricao**: Insanidade (double-edged resource), Familiares, Sede Insaciavel, Life Drain, Spell Ramping
- **Dependencias**: Task 2.0
- **Arquivos criados**:
  - `src/core/classes/warlock/__init__.py` - Package marker
  - `src/core/classes/warlock/insanity_bar.py` - InsanityBar resource (0-100, gain/decay/ratio)
  - `src/core/classes/warlock/insatiable_thirst.py` - InsatiableThirst (5 stacks below 50% HP, buff CON turnos)
  - `src/core/classes/warlock/familiar.py` - FamiliarType enum (IMP/RAVEN/SPIDER/SHADOW_CAT) + FamiliarConfig + loader
  - `src/core/classes/warlock/warlock_config.py` - WarlockConfig frozen (11 fields: insanity, thirst, passives)
  - `src/core/classes/warlock/warlock.py` - Warlock(Character) com insanidade, sede, familiar, life drain, spell ramp
  - `data/classes/warlock.json` - ClassModifiers (d8, atk_mag 9, def_fis 3, def_mag 4, mana 8)
  - `data/classes/warlock_config.json` - Config insanidade/sede/passivas (11 params)
  - `data/classes/warlock_familiars.json` - 4 familiares com stat_bonus_type e stat_bonus_pct
  - `tests/core/test_classes/test_warlock/` - 4 arquivos, 88 testes
- **Notas**: 1524 testes totais (1436+88), 100% cobertura (2668 stmts). InsanityBar double-edged: +40% magical_attack no max MAS -25% magical_defense. Gain: +10 por cast, 5% do dano recebido. Decay: 3/turno. InsatiableThirst: 1 stack/turno abaixo de 50% HP, trigger em 5 stacks, buff dura CON turnos (+20% atk, +20% regen, +15% def_fis). 4 familiares com bonus passivo (IMP=+10% mag_atk, RAVEN=+8% speed, SPIDER=+5% debuff, SHADOW_CAT=+7% mag_def). Life Drain: 15% do bleed damage vira HP. Spell Ramping: register_cast → proxima skill +15% + CHA*0.005 bonus. Refactor gate: PASSED (1 HIGH corrigido: magic number 0.005 movido para warlock_config.json como spell_ramp_cha_scaling).

#### Task 2.13 - Druid (Druida)
- **Status**: CONCLUIDA
- **Descricao**: Transformacoes (ShapeShift), condicoes de campo, passivas naturais
- **Dependencias**: Tasks 2.1, 2.3 (campo = buff/debuff elemental)
- **Arquivos criados**:
  - `src/core/classes/druid/__init__.py` - Package marker
  - `src/core/classes/druid/animal_form.py` - AnimalForm enum (HUMANOID/BEAR/WOLF/EAGLE/SERPENT) + AnimalFormModifier frozen + loader
  - `src/core/classes/druid/field_condition.py` - FieldConditionType enum (SNOW/RAIN/SANDSTORM/FOG) + FieldConditionConfig frozen + loader
  - `src/core/classes/druid/druid_config.py` - DruidConfig frozen (6 campos) + loader
  - `src/core/classes/druid/druid.py` - Druid(Character) com shapeshift, field conditions, passivas
  - `data/classes/druid.json` - ClassModifiers (d8, atk_phys 5, atk_mag 7, def 4/5, mana 10, regen 5/5)
  - `data/classes/druid_forms.json` - 5 formas com 6 multiplicadores cada
  - `data/classes/druid_fields.json` - 4 condicoes de campo com resistencia/vulnerabilidade elemental
  - `data/classes/druid_config.json` - Config passivas (transform_mana_cost, field_mana_cost, healing/regen/nature bonuses)
  - `tests/core/test_classes/test_druid/` - 3 arquivos, 82 testes (19 animal_form + 15 field_condition + 48 druid)
- **Notas**: 1606 testes totais (1524+82), 100% cobertura (2790 stmts). ShapeShift: transform(form) custa mana, revert_form() gratis, stats multiplicados pela forma ativa (BEAR: +30% def/-20% speed, WOLF: +25% phys_atk, EAGLE: +30% speed/+20% mag_atk, SERPENT: +15% mag_atk). Field Conditions: cria condicao de campo com custo de mana, tick auto-decrementa, cada condicao tem resistencia e vulnerabilidade elemental. Passivas: heal() override +15%, hp_regen/mana_regen +10%, nature_atk_bonus +8% magical_attack. Refactor gate: PASSED (0 CRITICAL, 0 HIGH).

#### Task 2.14 - Rogue (Ladino)
- **Status**: CONCLUIDA
- **Descricao**: Stealth (invisibilidade + crit garantido), passivas (crit, poison, speed), uso livre de itens
- **Dependencias**: Task 2.0
- **Arquivos criados**:
  - `src/core/classes/rogue/__init__.py` - Package marker
  - `src/core/classes/rogue/stealth.py` - Stealth state tracker (binario on/off, guaranteed_crit)
  - `src/core/classes/rogue/rogue_config.py` - RogueConfig frozen (6 campos) + loader
  - `src/core/classes/rogue/rogue.py` - Rogue(Character) com stealth, passivas, speed override
  - `data/classes/rogue.json` - ClassModifiers (d8, atk_phys 8, atk_mag 4, def 4/3, mana 6, regen 3/3)
  - `data/classes/rogue_config.json` - Config passivas (crit_bonus_per_dex, poison, speed, skill_slots, crit_speed_boost)
  - `tests/core/test_classes/test_rogue/` - 2 arquivos, 43 testes (10 stealth + 33 rogue)
- **Notas**: 1649 testes totais (1606+43), 100% cobertura (2912 stmts). Stealth: enter/break toggle, guaranteed_crit quando stealthed, take_damage override quebra stealth automaticamente (LSP preservado). Passivas config-driven: crit_bonus = DEX * 0.005, poison_damage +15%, speed +10% permanente, +1 skill slot, crit_speed_boost +15% por 2 turnos apos crit. free_item_use=True como interface (sistema de itens deferred). Speed override: base + passive(10%) + crit_boost(15% temporario). Refactor gate: PASSED (0 CRITICAL, 0 HIGH).

#### Task 2.15 - Bard (Bardo)
- **Status**: CONCLUIDA
- **Descricao**: Embalo Musical (stacking buff resource), passivas de buff/debuff effectiveness, speed
- **Dependencias**: Task 2.1 (embalo = buff stacking)
- **Arquivos criados**:
  - `src/core/classes/bard/__init__.py` - Package marker
  - `src/core/classes/bard/musical_groove.py` - MusicalGrooveConfig frozen (10 campos) + MusicalGroove resource bar
  - `src/core/classes/bard/bard_config.py` - BardConfig frozen (4 campos) + loader
  - `src/core/classes/bard/bard.py` - Bard(Character) com groove, passivas, speed override
  - `data/classes/bard.json` - ClassModifiers (d8, atk_phys 4, atk_mag 6, def 4/5, mana 8, regen 4/4)
  - `data/classes/bard_groove.json` - MusicalGroove config (10 stacks, bonuses, crescendo)
  - `data/classes/bard_config.json` - Passivas config (speed, buff/debuff effectiveness, bonus actions)
  - `tests/core/test_classes/test_bard/` - 2 arquivos, 51 testes (22 musical_groove + 29 bard)
- **Notas**: 1700 testes totais (1649+51), 100% cobertura (3039 stmts). MusicalGroove: stacks 0-10, +1/skill, -1/turno. Bonuses escalantes: buff (+2%/stack=20% max), debuff (+1.5%/stack=15% max), speed (+1%/stack=10% max), crit (+0.5%/stack=5% max). Crescendo: ao atingir max stacks, +25% buff/debuff bonus por 2 turnos, reset para 5 stacks. Passivas config-driven: speed +10%, buff_effectiveness +15%, debuff_effectiveness +10%, +1 bonus action. NPC recruitment deferred (party system nao existe). Refactor gate: PASSED (0 CRITICAL, 0 HIGH).

#### Task 2.16 - Artificer (Artifice)
- **Status**: CONCLUIDA
- **Descricao**: Traje Tecmagis, potencializa itens ativos, suporte/mana
- **Dependencias**: Task 2.0
- **Arquivos criados**:
  - `src/core/classes/artificer/__init__.py`
  - `src/core/classes/artificer/tech_suit.py` - TechSuitConfig frozen + TechSuit calculator (mana ratio → multipliers)
  - `src/core/classes/artificer/artificer_config.py` - ArtificerConfig frozen (3 passivas) + loader
  - `src/core/classes/artificer/artificer.py` - Artificer(Character), 4 stat overrides + scroll_potentiation
  - `data/classes/artificer.json` - ClassModifiers (d8, mana=10, atk_mag=8, regen_mana=6)
  - `data/classes/artificer_suit.json` - TechSuit config (atk=0.20, phys_def=0.15, mag_def=0.20)
  - `data/classes/artificer_config.json` - Passivas (mana_regen=0.20, mag_def=0.10, scroll=0.15)
  - `tests/core/test_classes/test_artificer/__init__.py`
  - `tests/core/test_classes/test_artificer/test_tech_suit.py` - 15 testes
  - `tests/core/test_classes/test_artificer/test_artificer.py` - 24 testes
- **Notas**: TechSuit como calculator stateless (padrao mais simples que resource bar). Item potentiation e mana share deferred.

### Bloco D - Equipamento Restante

#### Task 2.17 - Armaduras e Acessorios (RF07.2, RF07.3)
- **Status**: CONCLUIDA
- **Descricao**: Armaduras leve/media/pesada, acessorios com buffs, limite por CHA
- **Dependencias**: Task 2.5 (sistema de armas base)
- **Arquivos criados**:
  - `src/core/items/item_rarity.py` - ItemRarity enum (COMMON, UNCOMMON, RARE, LEGENDARY)
  - `src/core/items/armor_weight.py` - ArmorWeight enum (LIGHT, MEDIUM, HEAVY)
  - `src/core/items/accessory_type.py` - AccessoryType enum (AMULET, RING, CLOAK, BRACELET)
  - `src/core/items/stat_bonus.py` - StatBonus frozen dataclass + from_dict
  - `src/core/items/armor.py` - Armor frozen dataclass + from_dict (CA, HP, mana, def bonuses)
  - `src/core/items/accessory.py` - Accessory frozen dataclass + from_dict (tuple[StatBonus])
  - `src/core/items/armor_loader.py` - load_armors() from JSON
  - `src/core/items/accessory_loader.py` - load_accessories() from JSON
  - `src/core/items/armor_proficiency.py` - frozensets por classe + can_equip_armor()
  - `src/core/items/accessory_slots.py` - calculate_accessory_slots() (2 base + CHA thresholds)
  - `src/core/characters/equipment_mixin.py` - EquipmentMixin (equip/unequip, bonus aggregation)
  - `data/armors/armors.json` - 6 armaduras (2 light, 2 medium, 2 heavy)
  - `data/accessories/accessories.json` - 4 acessorios
  - 12 arquivos de teste (77 testes novos)
- **Arquivos modificados**: character.py, character_config.py, combat_stats_mixin.py, modifiable_stat.py
- **Notas**: Armor slot unico (set completo). Accessory slots = 2 + CHA thresholds. Proficiency: ALL (Fighter/Paladin), LIGHT+MEDIUM (Cleric/Barbarian/Ranger/Druid/Artificer), LIGHT (demais). Actives/passives especiais deferred.

#### Task 2.18 - Sistema de Skills/Habilidades (RF06)
- **Status**: CONCLUIDA
- **Descricao**: Spell slots com custo customizavel, cooldowns, progressao de skills, barra de skills
- **Dependencias**: Task 2.0 (classes base)
- **Arquivos criados**:
  - `src/core/skills/skill_effect_type.py` - SkillEffectType enum (DAMAGE, HEAL, BUFF, DEBUFF, APPLY_AILMENT)
  - `src/core/skills/target_type.py` - TargetType enum (SELF, SINGLE_ALLY, SINGLE_ENEMY, ALL_ALLIES, ALL_ENEMIES)
  - `src/core/skills/skill_effect.py` - SkillEffect frozen dataclass + from_dict
  - `src/core/skills/skill.py` - Skill frozen dataclass + from_dict (descriptivo, sem execucao)
  - `src/core/skills/skill_loader.py` - load_skills() from JSON
  - `src/core/skills/spell_slot.py` - SpellSlot frozen + funcoes puras (budget de custo)
  - `src/core/skills/cooldown_tracker.py` - CooldownTracker mutavel (tick, reset, is_ready)
  - `src/core/skills/skill_bar.py` - SkillBar composicao (SpellSlots + CooldownTracker)
  - `src/core/skills/skill_slots_calculator.py` - calculate_skill_slots (base 3 + INT thresholds)
  - `data/skills/skills.json` - 10 skills genericas
  - 10 arquivos de teste (94 testes novos)
- **Arquivos modificados**: thresholds.json (+skill_slots em INT), character.py, character_config.py
- **Notas**: 1910 testes totais, 100% cobertura. SpellSlot como budget imutavel (add retorna novo). CooldownTracker.tick() iteration-safe. SkillBar.ready_skills filtra por cooldown. Execucao de skills no combate deferred para proxima task.

#### Task 2.19 - Consumiveis e Inventario (RF07.4, RF07.5)
- **Status**: CONCLUIDA
- **Descricao**: Pocoes, itens de combate, inventario com slots
- **Dependencias**: Task 2.17
- **Arquivos criados**:
  - `src/core/items/consumable_effect_type.py` - ConsumableEffectType enum (HEAL_HP, HEAL_MANA, DAMAGE, BUFF, CLEANSE, FLEE)
  - `src/core/items/consumable_category.py` - ConsumableCategory enum (HEALING, DEFENSE, OFFENSIVE, CLEANSE, ESCAPE)
  - `src/core/items/consumable_effect.py` - ConsumableEffect frozen dataclass + from_dict
  - `src/core/items/consumable.py` - Consumable frozen dataclass + from_dict (descriptivo, sem execucao)
  - `src/core/items/consumable_loader.py` - load_consumables() from JSON
  - `src/core/items/inventory_slot.py` - InventorySlot frozen (consumable + quantity)
  - `src/core/items/inventory.py` - Inventory mutavel (add/remove, stacking, max 20 slots)
  - `data/consumables/consumables.json` - 6 consumiveis (health/mana potion, molotov, turtle shell, antidote, smoke bomb)
  - 7 arquivos de teste (58 testes novos)
- **Arquivos modificados**: nenhum
- **Notas**: 1968 testes totais. ConsumableEffect separado de SkillEffect (Open/Closed). Inventario nao integrado ao Character (vive externo, party-level). Rogue.free_item_use ja existe. Execucao de consumiveis deferred para combat handler.

### Bloco E - Integracao e Visualizacao

#### Task 2.20 - Mock Battle v2 (Integracao Fase 2)
- **Status**: CONCLUIDA
- **Descricao**: Batalha completa com elementos, buffs/debuffs, mais classes, equipamento
- **Criterio de aceite**: Combate com 6+ classes, efeitos elementais, buffs/debuffs ativos, combat log mostrando tudo
- **Dependencias**: Todas as tasks anteriores

#### Task 2.21 - Pygame Minimo (Preview Visual)
- **Status**: CONCLUIDA
- **Descricao**: Visualizacao basica do Mock Battle v2 com Pygame. Shapes coloridos como placeholder (sem sprites), barras de HP/Mana, log de combate, efeitos ativos visiveis. Roda a batalha automaticamente (sem input do jogador ainda).
- **Criterio de aceite**: Janela Pygame mostra batalha rodando em tempo real, personagens como retangulos coloridos, barras de vida, texto de acoes/efeitos
- **Dependencias**: Task 2.20
- **Notas**: Primeira dependencia externa alem do pytest (pygame). Tudo em src/ui/ (core/ NAO importa ui/). Assets reais ficam para Fase 4. Wireframe de referencia em `Coisas interessantes/WhatsApp Image 2022-05-26 at 21.25.41.jpeg`.

#### Task 2.22 - Animacoes de Combate (Visual Polish)
- **Status**: PENDENTE
- **Descricao**: Sistema de animacoes baseado em particulas e shapes para feedback visual de acoes de combate (ataque, magia, cura, veneno, buffs, morte). Zero assets externos — tudo com geometria e particulas Pygame.
- **Criterio de aceite**: Cada tipo de evento tem animacao visual distinta, CombatScene espera animacao acabar antes de avancar pro proximo evento, floating damage/heal numbers visiveis
- **Dependencias**: Task 2.21
- **Notas**: Ver plano detalhado abaixo.

**Arquitetura de Animacoes:**

```
src/ui/
  animations/
    __init__.py
    animation.py              # Animation Protocol (update/draw/is_done)
    animation_manager.py      # Gerencia animacoes ativas, update/draw all
    floating_text.py          # Numeros de dano/heal flutuando pra cima (+fade)
    slash_effect.py           # Linha diagonal que cruza o alvo (ataque fisico)
    magic_burst.py            # Circulos/particulas expandindo (cor por elemento)
    heal_particles.py         # Particulas verdes subindo no alvo
    poison_bubbles.py         # Bolhas roxas ao redor do personagem (DoT tick)
    buff_aura.py              # Aura pulsante ao redor do card (verde=buff, vermelho=debuff)
    card_shake.py             # Shake no card do alvo ao receber dano
    death_fade.py             # Card escurece gradualmente ao morrer
    animation_factory.py      # Dispatch table: EventType -> Animation
```

**Animation Protocol:**
```python
class Animation(Protocol):
    def update(self, dt_ms: int) -> None: ...
    def draw(self, surface: pygame.Surface) -> None: ...
    @property
    def is_done(self) -> bool: ...
```

**AnimationManager:**
- Lista de animacoes ativas
- `spawn(animation)`: adiciona nova
- `update(dt_ms)`: ticka todas, remove as finalizadas
- `draw(surface)`: desenha todas
- `has_active`: True se alguma animacao rodando
- `has_blocking`: True se alguma animacao blocking (CombatScene espera)

**Integracao com CombatScene:**
- Ao avancar evento, spawna animacao via `animation_factory`
- `update()`: se `has_blocking`, NAO avanca timer de proximo evento
- `draw()`: desenha animacoes SOBRE o battlefield (layer acima)
- Animacoes nao-blocking (floating text, aura) podem rodar em paralelo

**Mapeamento EventType -> Animacao:**
| EventType | Animacao | Blocking | Duracao |
|-----------|----------|----------|---------|
| DAMAGE (fisico) | SlashEffect + CardShake + FloatingText(vermelho) | Sim | 400ms |
| DAMAGE (magico/skill) | MagicBurst(cor do elemento) + FloatingText(vermelho) | Sim | 500ms |
| HEAL | HealParticles + FloatingText(verde) | Sim | 400ms |
| BUFF | BuffAura(verde) | Nao | 600ms |
| DEBUFF | BuffAura(vermelho) | Nao | 600ms |
| AILMENT | PoisonBubbles(roxo) | Nao | 500ms |
| EFFECT_TICK (DoT) | PoisonBubbles + FloatingText(roxo) | Nao | 400ms |
| DEATH | DeathFade | Nao | 800ms |
| SKIP_TURN | nenhuma | Nao | - |

**Cores por Elemento (MagicBurst):**
- FIRE: (255, 120, 30) laranja
- ICE: (130, 200, 255) azul claro
- LIGHTNING: (255, 255, 100) amarelo
- HOLY: (255, 255, 200) branco quente
- DARKNESS: (100, 50, 150) roxo escuro
- Default: (200, 200, 255) branco azulado

**Steps TDD:**
1. Animation Protocol + AnimationManager (puro Python, testavel)
2. FloatingText (posicao, velocidade, fade, is_done)
3. SlashEffect (linha start->end, progresso, is_done)
4. MagicBurst (particulas expandindo, cor, is_done)
5. HealParticles (particulas subindo, fade, is_done)
6. PoisonBubbles (bolhas oscilando, is_done)
7. BuffAura (rect pulsante, cor, is_done)
8. CardShake (offset oscilante, is_done)
9. DeathFade (alpha decrescente, is_done)
10. AnimationFactory (dispatch EventType -> animacoes)
11. Integrar AnimationManager no CombatScene
12. Teste visual manual (run_battle_visual.py)

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

### Sessao 5 - 2026-03-02

- Task 2.5 concluida: 133 testes novos (1035 total), 100% cobertura (1752 stmts)
- Sistema de armas completo: 4 enums, Weapon frozen dataclass, JSON loader, proficiencias, integracao Character
- 15 armas no JSON: 11 common (sword, dagger, bow, staff, hammer, lance, mace) + 4 uncommon elementais (fire, ice, lightning, holy)
- weapon_die routing integrado no CombatStatsMixin: arma PHYSICAL soma em physical_attack, MAGICAL em magical_attack
- Refactor gate: weapon methods movidos de Character para CombatStatsMixin, conftest.py compartilhado para test_items
- **Decisoes**: Weapon como frozen dataclass com from_dict() (Enum[name] parsing, sem jsonschema). Proficiencias genericas por enquanto (frozenset de WeaponCategory). weapon/equip/unequip no CombatStatsMixin (junto do weapon_die routing). TYPE_CHECKING guards para evitar circular imports.

### Sessao 6 - 2026-03-03

- Task 2.6 concluida: 68 testes novos (1103 total), 100% cobertura (1872 stmts)
- Sistema de progressao completo: XP table, level 1-10, pontos de atributo, HP/regen scaling, proficiency bonus
- Modulo `src/core/progression/` criado (4 arquivos), `data/progression/` (2 JSONs)
- HP acumulativo: `base * (level+1) * mod_hp`, regen scaling: `CON * level * mod`
- Template Method hook: `on_level_up()` no Character, Fighter override atualiza AP limit
- Refactor gate: extraido conftest.py, removido dead code (LEVEL_1_HP_MULTIPLIER, ZERO_POINTS), removidas delegacoes desnecessarias (add_effect/has_active_effects), monkey-patch substituido por unittest.mock.patch
- **Decisoes**: LevelUpSystem externo ao Character (SRP — Character nao sabe de XP). XP table data-driven do JSON. Niveis impares = 0 pontos (reservados para subclasses/talentos). Proficiency bonus = level (property no CombatStatsMixin). add_effect/has_active_effects removidos do Character (pura delegacao, callers ja usavam effect_manager direto).

### Sessao 7 - 2026-03-04

- Task 2.7 concluida: 54 testes novos (1157 total), 99% cobertura (1958 stmts)
- Barbarian completo: FuryBar resource, FuryConfig frozen, Barbarian(Character) com fury + missing HP bonus
- FuryBar: max = 25% max_hp, gain on damage (10%), gain on attack (+5), decay 3/turno
- Fury passiva: +30% physical_attack e +20% hp_regen no max (linear scaling)
- Missing HP bonus: +25% physical_attack linear com HP faltando
- on_level_up recalcula fury max (acompanha max_hp)
- Refactor gate: PASSED (1 MEDIUM corrigido: unused import FuryConfig)
- **Decisoes**: FuryBar como resource separado (mesmo padrao de ActionPoints). Fury NAO e buff do EffectManager - e estado interno da classe (como Stance do Fighter). Berserk/perda de controle fica para RF09 (IA). physical_attack override combina 2 multiplicadores (fury + missing HP). Dados de balanceamento em 2 JSONs (barbarian.json + barbarian_fury.json).

### Sessao 8 - 2026-03-05

- Task 2.8 (Paladin) commitada na sessao anterior, PROGRESS atualizado
- Task 2.9 concluida: 63 testes novos (1288 total), 100% cobertura (2207 stmts)
- Ranger completo: PredatoryFocus (stack crit +2%/stack, +5% crit dmg/stack), HuntersMark (20% armor pen)
- Focus: gain +2/hit, lose -4/miss, decay -1/turn, +0.5% physical_attack/stack
- Refactor gate: PASSED (0 issues)
- Task 2.10 concluida: 81 testes novos (1369 total), 100% cobertura (2343 stmts)
- Monk completo: EquilibriumBar bidirecional (0=Vitality, 50=center, 100=Destruction)
- Tres zonas: Vitality (+20% def), Balanced (+8% atk/def), Destruction (+25% atk, +15% crit, +1 hit)
- Multi-hit: base 2, +1 em Destruction. mod_atk_physical=6 (compensado por multi-hit)
- Refactor gate: PASSED (0 issues)
- **Decisoes**: EquilibriumBar como resource bidirecional (diferente de FuryBar unidirecional). Intensidades lineares dentro das zonas. Balanced = bonus fixo (recompensa manter equilibrio). Debuff chance exposta como property (combat handler aplica). Ranger: crit bonuses como properties (combat handler consulta). HuntersMark usa string-based target tracking.

### Sessao 9 - 2026-03-05

- Task 2.11 concluida: 67 testes novos (1436 total), 100% cobertura (2466 stmts)
- Sorcerer completo: Overcharged (1.8x atk + mana cost + self-damage), Metamagia (troca elemento por mana), Mana Rotation (8% do dano magico vira mana)
- Born of Magic passiva: +10% magical_attack permanente
- ManaRotation: resource bar (gain on magic damage, decay per turn, max = 20% max_mana)
- Overcharged vs Mage Overcharge: mais dano (1.8x vs 1.5x), mais custo (40 vs 30 mana), E self-damage (5% max_hp)
- Refactor gate: PASSED (1 HIGH corrigido: unused import OverchargedConfig)
- **Decisoes**: Overcharged self-damage = % do max_hp fixo (CON influencia indiretamente via max_hp). Metamagia custa mana (15) para evitar spam. ManaRotation como resource bar separado (mesmo padrao FuryBar). OverchargedConfig agrupa configs de overcharged + metamagia + born_of_magic (todos do Sorcerer, evita 3 config files). Mana nao escala com level, entao rotation max nao muda no level up (mas on_level_up recalcula para future-proofing).

### Sessao 10 - 2026-03-05

- Task 2.12 concluida: 88 testes novos (1524 total), 100% cobertura (2668 stmts)
- Warlock completo: InsanityBar (double-edged: +40% atk / -25% def), InsatiableThirst (5 stacks → buff CON turnos), 4 Familiares com passivas
- Life Drain: 15% do bleed damage → HP. Spell Ramping: +15% + CHA scaling na proxima skill
- Refactor gate: PASSED (1 HIGH corrigido: magic number 0.005 → spell_ramp_cha_scaling no config)
- **Decisoes**: InsanityBar como resource double-edged (padrao FuryBar mas com penalidade). Familiares como Enum + FamiliarConfig JSON (ativo deferred para skills). InsatiableThirst como counter simples (5 stacks trigger, CON duracao). Spell Ramping implementado agora (nao deferred). WarlockConfig agrupa 11 params (insanity + thirst + passives).

### Sessao 11 - 2026-03-05

- Task 2.13 concluida: 82 testes novos (1606 total), 100% cobertura (2790 stmts)
- Druid completo: ShapeShift (5 formas com multiplicadores de stats), Field Conditions (4 condicoes com resistencia/vulnerabilidade elemental)
- Passivas: heal +15%, hp/mana regen +10%, nature_atk +8% magical_attack
- Formas: BEAR (+30% def, -20% speed), WOLF (+25% phys_atk), EAGLE (+30% speed, +20% mag_atk), SERPENT (+15% mag_atk)
- Refactor gate: PASSED (0 CRITICAL, 0 HIGH)
- Task 2.14 concluida: 43 testes novos (1649 total), 100% cobertura (2912 stmts)
- Rogue completo: Stealth (toggle + guaranteed crit), take_damage override (auto-break stealth)
- Passivas: crit_bonus (DEX*0.005), poison +15%, speed +10%, +1 skill slot, crit_speed_boost (+15% por 2 turnos)
- free_item_use=True como interface (sistema de itens deferred)
- Refactor gate: PASSED (0 CRITICAL, 0 HIGH)
- **Decisoes**: Stealth como componente binario (padrao PredatoryFocus). take_damage override preserva LSP (mesmo contrato, side effect adicional). free_item_use como property constante (combat handler checa). Crit speed boost como counter interno (on_crit seta, tick decrementa). Item system deferred — expor interface agora, implementar quando consumiveis existirem.
- Task 2.15 concluida: 51 testes novos (1700 total), 100% cobertura (3039 stmts)
- Bard completo: MusicalGroove (stacks 0-10, +1/skill, -1/turno, 4 bonuses escalantes, crescendo no max)
- Crescendo: +25% buff/debuff bonus por 2 turnos, reset para 5 stacks
- Passivas: speed +10%, buff_effectiveness +15%, debuff_effectiveness +10%, +1 bonus action
- NPC recruitment deferred (party system nao existe)
- Refactor gate: PASSED (0 CRITICAL, 0 HIGH)
- **Decisoes**: MusicalGroove como resource bar (padrao FuryBar/PredatoryFocus). Crescendo como trigger temporario (padrao InsatiableThirst). Buff/debuff effectiveness como properties passivas (combat handler aplica). NPC recruitment deferred completo. Posicao default BACK (support).
- Task 2.16 concluida: 39 testes novos (1739 total), 100% cobertura (3120 stmts)
- Artificer completo: TechSuit stateless calculator (mana ratio → stat multipliers)
- Bonuses at full mana: +20% atk, +15% phys_def, +20% mag_def (linear scaling)
- Passivas: mana_regen +20%, magical_defense +10%, scroll_potentiation +15%
- Item potentiation e mana share deferred (sistemas nao existem)
- Refactor gate: PASSED (0 CRITICAL, 0 HIGH)
- **Decisoes**: TechSuit como calculator stateless (padrao mais simples que resource bar — recebe ratio, retorna multiplier). Scroll potentiation como property constante (combat handler aplica). Mana share deferred. Posicao default BACK (support/mana).
- **BLOCO C COMPLETO**: Todas 10 classes restantes implementadas (Barbarian, Paladin, Ranger, Monk, Sorcerer, Warlock, Druid, Rogue, Bard, Artificer). Total: 13/13 classes.

### Sessao 12 - 2026-03-06

- Task 2.17 concluida: 77 testes novos (1816 total), 100% cobertura (3298 stmts)
- Armor system: frozen dataclass, 6 armaduras (light/medium/heavy), CA/HP/mana/defense bonuses
- Accessory system: frozen dataclass com StatBonus tuple, 4 acessorios, slot limit 2+CHA thresholds
- EquipmentMixin: novo mixin para equip/unequip armor/accessories, bonus aggregation
- Armor proficiency por classe: ALL (Fighter/Paladin), LIGHT+MEDIUM (Cleric/Barbarian/Ranger/Druid/Artificer), LIGHT (demais)
- Nova property armor_class: CA + DEX + level
- Refactor gate: PASSED (0 CRITICAL, 0 HIGH)
- Reorganizacao de tasks: RF06 Skills inserido como Task 2.18, Consumiveis movido para 2.19, Mock Battle para 2.20, Pygame para 2.21
- **Decisoes**: Armor slot unico (set completo, RF diz "sets completos"). Accessory slots = 2 base + CHA magic_item_slots thresholds. Bonus flat somados ANTES de effect modifiers. EquipmentMixin extraido para nao estourar CombatStatsMixin (164→179 linhas). ItemRarity separado de WeaponRarity (Open/Closed). Actives/passives especiais deferred.

### Sessao 13 - 2026-03-08

- Task 2.18 concluida: 94 testes novos (1910 total), 100% cobertura (3442 stmts)
- Skill system infra: SkillEffect/Skill frozen dataclasses, SpellSlot budget, CooldownTracker, SkillBar, skill_slots_calculator
- SpellSlot como budget imutavel (add retorna novo SpellSlot ou None). 10 skills genericas no JSON.
- INT thresholds: +skill_slots em todos os 5 marcos
- Character integrado com SkillBar opcional
- Refactor gate: PASSED (0 CRITICAL, 0 HIGH)
- Task 2.19 concluida: 58 testes novos (1968 total)
- Consumable system: ConsumableEffectType (6 tipos), ConsumableCategory (5 tipos), ConsumableEffect, Consumable frozen dataclasses
- Inventory: stacking (max_stack por item), 20 slots max, add/remove/query
- 6 consumiveis no JSON: health/mana potion, molotov, turtle shell, antidote, smoke bomb
- Refactor gate: PASSED (0 CRITICAL, 0 HIGH)
- **Decisoes**: ConsumableEffect separado de SkillEffect (Open/Closed). Inventario nao integrado ao Character (vive externo). Execucao de skills e consumiveis deferred para combat handler. **BLOCO D COMPLETO**: Equipment (armas, armaduras, acessorios), skills infra, consumiveis e inventario.
- Task 2.19b concluida: 59 testes novos (2027 total)
- CombatEvent expandido: EventType enum (10 tipos), damage opcional, value/description fields
- Inventory integrado ao Character via CharacterConfig
- TargetResolver: dispatch table TargetType → alvos concretos (front-line priority, alive filter)
- SkillEffectApplier: dispatch table SkillEffectType → handler (DAMAGE, HEAL, BUFF, DEBUFF, APPLY_AILMENT)
- ConsumableEffectApplier: dispatch table ConsumableEffectType → handler (HEAL_HP, HEAL_MANA, DAMAGE, BUFF, CLEANSE, FLEE)
- SkillHandler: TurnHandler que seleciona skill pronta com mana, executa efeitos, inicia cooldown
- ConsumableHandler: TurnHandler que seleciona consumivel com mana, executa efeitos, remove do inventario
- Cooldown tick integrado no combat loop (_tick_cooldowns antes do handler)
- Refactor gate: PASSED (0 CRITICAL, 0 HIGH)
- **Decisoes**: Dispatch table pattern para todos os appliers (extensivel sem modificar). Element presence determina defense type (element → magical, None → physical). Cleanse remove non-StatBuff effects (keeps buffs). Cooldown tick antes do handler (skill fica ready no mesmo turno que cooldown expira).

### Sessao 14 - 2026-03-10

- Task 2.20 concluida: Mock Battle v2 + combat fixes
- CompositeHandler: combina AttackHandler + SkillHandler + ConsumableHandler com prioridade
- DispatchTurnHandler usa CompositeHandler como fallback
- CombatLog: formata eventos/efeitos em texto legivel (LogFormatter + log_formatter)
- Mock battle script (scripts/run_battle.py): party 4 vs enemies 3, combate completo
- Fix: skill damage agora escala com attack stats (physical ou magical baseado em element)
- Fix: combat log descriptions e templates melhorados
- Refactor gate: PASSED
- Task 2.21 concluida: Pygame visual battle replay
- src/ui/ criado (core/ NUNCA importa de ui/)
- BattleRecorder: roda batalha round-by-round, captura snapshots (HP/Mana/Effects/is_alive)
- BattleReplay: dataclass frozen com snapshots + events + effect_log + result
- CombatScene: consome BattleReplay, avanca 1 evento a cada 1.5s
- Componentes visuais: HealthBar, CharacterCard, CombatLogPanel, Battlefield
- Game loop Pygame 1280x720, ESC para sair
- Entry point: scripts/run_battle_visual.py
- pygame-ce>=2.4 adicionado como dependencia
- Balance changes:
  - MANA_BASE_MULTIPLIER 10→5 (pools menores, mais gerenciaveis)
  - Custos de mana de skills divididos por 2 proporcionalmente
  - Consumiveis fisicos (potions, antidotes) com mana_cost=0
  - Skill heals escalam com magical_attack do caster (base_power + magical_attack)
  - Cura recebida escala com CON do alvo (+5% por ponto, CON_HEAL_BONUS_PER_POINT=0.05)
  - Poison buffado: 5→10 dano por tick
  - AI: skip wasteful heals (skills e consumables) quando todos com HP cheio
  - AI: skip wasteful cleanse quando sem efeitos negativos
  - Target resolver: SINGLE_ALLY escolhe aliado mais machucado (min HP ratio)
- docs/BALANCE_DECISIONS.md criado com todas as decisoes de balanceamento
- 2074 testes passando, 0 CRITICAL, 0 HIGH
- **Decisoes**: Consumable heals sao flat (nao escalam com stats). Skill heals escalam com magical_attack inteiro. CON bonus aplica ANTES de effect modifiers. DoT scaling com %HP maximo documentado como TODO futuro.
