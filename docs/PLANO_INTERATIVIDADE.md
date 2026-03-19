# Plano Mestre - Sistema de Interatividade do Jogador

## Visao Geral

Este plano transforma o RPG Turno de uma **simulacao automatica** em um **jogo jogavel**.
Atualmente o combate roda via `TurnHandler` (IA/script) e a UI apenas reproduz um replay gravado.
O objetivo e criar um loop onde o jogador **controla a party em tempo real** durante o combate,
com feedback visual rico, atalhos de teclado fluidos e QTE opcional para potenciar skills.

O plano esta dividido em **6 etapas incrementais**, cada uma entregando valor jogavel.
Cada etapa pode ser commitada independentemente com todos os testes passando.

---

## Mudanca Arquitetural Central

### De Replay para Real-Time

**Hoje** o fluxo e:
```
CombatEngine.run_combat()          # roda TUDO de uma vez
  -> BattleRecorder grava replay   # snapshots + events
    -> CombatScene reproduz        # animacao pos-facto
```

**Depois** o fluxo sera:
```
InteractiveCombatScene gerencia o loop
  -> Para cada turno de personagem da party:
     -> Mostra menu de acoes (aguarda input)
     -> Jogador escolhe acao + alvo
     -> Executa acao via ActionResolver (gera CombatEvents)
     -> Anima resultado
  -> Para cada turno de inimigo:
     -> IA decide via TurnHandler existente
     -> Anima resultado
  -> Proximo turno (TurnOrder)
```

### Ponto de Extensao: `TurnHandler` Protocol

O `TurnHandler` Protocol (`combat_engine.py:71-74`) ja e o ponto de extensao perfeito.
A mudanca central e que **o CombatEngine NAO roda sozinho** — a `InteractiveCombatScene`
orquestra turno a turno, chamando o engine passo-a-passo.

Para isso, o `CombatEngine` precisa de um metodo novo:
```python
def execute_single_turn(self, combatant_name: str) -> TurnStepResult:
    """Executa um unico turno (effects + handler) e retorna resultado."""
```

Isso permite que a Scene controle o ritmo: pausa pra input do jogador,
depois chama `execute_single_turn` com a acao escolhida.

### Separacao Player vs AI

```
InteractiveCombatScene
  |
  |-- turno de membro da party? --> PlayerActionMenu (aguarda input)
  |                                   |-> PlayerTurnHandler (executa acao escolhida)
  |
  |-- turno de inimigo? -----------> AiTurnHandler (decide automaticamente)
  |                                   |-> Anima resultado
  |
  |-- verifica vitoria/derrota
  |-- proximo turno
```

O `DispatchTurnHandler` existente (`dispatch_handler.py`) ja suporta esse modelo:
basta mapear nomes de party members para `PlayerTurnHandler` e usar `AiTurnHandler` como default.

---

## Etapa 1 — Player Action Menu + Command System

**Objetivo**: Quando chegar a vez de um personagem da party, o jogo pausa e mostra
um menu de acoes. O jogador escolhe com teclado. A acao e executada e animada.

### 1.1 Estado de Turno na Scene

Nova state machine na `InteractiveCombatScene`:

```python
class TurnPhase(Enum):
    EFFECT_TICK = auto()      # animando ticks de efeitos (DoT, regen)
    WAITING_INPUT = auto()    # esperando jogador escolher (party turn)
    EXECUTING_ACTION = auto() # resolvendo acao + animando
    AI_TURN = auto()          # inimigo agindo (automatico + animacao)
    ROUND_END = auto()        # checando vitoria/derrota
    COMBAT_OVER = auto()      # resultado final
```

### 1.2 Menu Hierarquico (estilo FF / Sistema de Atalhos)

O menu segue a estrutura definida no doc de design original (`Sistema de atalhos.txt`):

```
NIVEL 0 - Selecao de Personagem (so se quiser trocar ordem manual)
  [1-4] seleciona membro da party (highlight visual no card)
  [Enter] confirma personagem selecionado

NIVEL 1 - Tipo de Acao
  [1] Acao Normal    (ataque, skill)          -- consome ACTION
  [2] Acao Bonus     (mover, mudar estancia)  -- consome BONUS_ACTION
  [3] Reacao         (defender, preparar)      -- consome REACTION
  [4] Item           (consumivel)             -- consome ACTION

NIVEL 2 - Opcoes Especificas (depende do nivel 1)
  Se [1] Acao Normal:
    [1] Ataque Basico
    [2] Skill 1  (nome + custo mana)
    [3] Skill 2
    ...
    [N] Skills ready da skill_bar

  Se [2] Acao Bonus:
    [1] Mover (Front <-> Back)
    [2] Mudar Estancia (Fighter)  -- so aparece se a classe tem
    [3] Ativar/Desativar Aura (Paladin)
    [4] Toggle Overcharge (Mage)
    ...classe-especificas via polimorfismo

  Se [3] Reacao:
    [1] Defender (reduz dano no proximo ataque recebido)
    [2] Preparar Contra-Ataque
    ...deferred para implementacao futura, comecar com Defender

  Se [4] Item:
    [1] Pocao de HP
    [2] Pocao de Mana
    ...itens do inventario

NIVEL 3 - Selecao de Alvo (quando aplicavel)
  [1-N] seleciona alvo (inimigos ou aliados, conforme TargetType da acao)
  Alvos validos filtrados por get_valid_targets() + TargetType da skill
  Alvos SELF e ALL_* nao pedem selecao (auto-resolve)
```

**Navegacao**:
- `Esc` volta um nivel (cancel)
- `Enter` confirma (redundante com numero, para quem prefere)
- Numeros sao atalho direto (1-9)
- Todo o menu e navegavel apenas por teclado (RF10.3: "Pode ser jogado apenas pelo teclado")

### 1.3 Arquivos Novos

```
src/core/combat/
  turn_step.py              # TurnStepResult dataclass, execute_single_turn logic
  player_action.py          # PlayerAction frozen dataclass (action_type, skill, target, item)
  action_resolver.py        # Resolve PlayerAction -> list[CombatEvent] (logica pura, sem UI)

src/ui/
  input/
    __init__.py
    menu_state.py           # MenuLevel enum + MenuState (nivel atual, opcoes, selecionado)
    action_menu.py          # ActionMenu - monta opcoes baseado no personagem + action economy
    target_selector.py      # TargetSelector - filtra alvos validos, highlight visual
    key_bindings.py         # Mapeamento tecla -> acao (configuravel, default numerico)

  components/
    action_panel.py         # Renderiza menu de acoes (retangulos com texto, highlight)
    action_economy_bar.py   # Barra visual [ACAO v] [BONUS v] [REACAO v]
    turn_indicator.py       # Highlight visual no card do personagem ativo

  scenes/
    interactive_combat.py   # Nova scene: orquestra combate turno-a-turno com input
```

### 1.4 Arquivos Modificados

```
src/core/combat/combat_engine.py
  - Novo metodo: prepare_turn(combatant) -> TurnSetupResult
    (faz effect tick, retorna se pode agir, context)
  - Novo metodo: resolve_action(context, events) -> CombatResult | None
    (aplica eventos, checa vitoria/derrota)
  - run_round() e run_combat() continuam funcionando para IA vs IA (backward-compatible)

src/ui/layout.py
  - Novas constantes: ACTION_PANEL_*, TARGET_PANEL_*, ECONOMY_BAR_*

src/ui/colors.py
  - Novas cores: MENU_*, HIGHLIGHT_*, SELECTED_*
```

### 1.5 Fluxo Detalhado de um Turno do Jogador

```
1. TurnOrder.next() retorna "Fighter" (party member)
2. InteractiveCombatScene detecta: e da party -> TurnPhase.EFFECT_TICK
3. Roda effect ticks (DoT, regen) com animacao
4. Se personagem pode agir (nao CC'd):
   a. TurnPhase.WAITING_INPUT
   b. Mostra ActionPanel com opcoes do nivel 1
   c. Mostra ActionEconomyBar: [ACAO v] [BONUS v] [REACAO v]
   d. Mostra TurnIndicator no card do Fighter (highlight pulsante)
5. Jogador pressiona [1] (Acao Normal):
   a. ActionMenu avanca para nivel 2 (lista de ataques/skills)
   b. Mostra: [1] Ataque Basico  [2] Cleave (30mp)  [3] Shield Bash (20mp)
6. Jogador pressiona [1] (Ataque Basico):
   a. ActionMenu avanca para nivel 3 (selecao de alvo)
   b. TargetSelector mostra alvos validos (melee -> front line)
   c. Cards dos alvos validos ficam highlighted
   d. Mostra: [1] Goblin A  [2] Goblin B
7. Jogador pressiona [2] (Goblin B):
   a. PlayerAction criado: (ACTION, basic_attack, target=goblin_b)
   b. TurnPhase.EXECUTING_ACTION
   c. ActionResolver resolve: dano, crit, etc -> list[CombatEvent]
   d. Eventos aplicados ao estado do combate
   e. Animacoes spawned (slash, shake, floating text)
8. Animacoes terminam
9. ActionEconomy ainda tem BONUS_ACTION disponivel?
   -> Se sim, volta para WAITING_INPUT (nivel 1, sem ACTION disponivel)
   -> Se nao (ou jogador pressiona [Esc] / [End Turn]), proximo turno
10. Proximo combatente
```

### 1.6 Regras de Disponibilidade

O menu so mostra opcoes que o jogador pode de fato usar:

- **Acao Normal**: so aparece se `action_economy.is_available(ACTION)` e True
- **Skills**: so aparecem as de `skill_bar.ready_skills` com `mana_cost <= current_mana`
- **Acao Bonus**: so aparece se `action_economy.is_available(BONUS_ACTION)` e True
- **Mover**: so aparece se tem alguem vivo na outra posicao (faz sentido tatico)
- **Estancia/Aura/Overcharge**: so aparece se a classe do personagem tem essa mecanica
  (polimorfismo — cada classe expoe `get_bonus_actions() -> list[BonusActionOption]`)
- **Item**: so aparece se inventario tem itens usaveis E action economy permite
- **Reacao**: so aparece se `action_economy.is_available(REACTION)` e True
- **Opcoes grayed-out**: opcoes que existem mas nao podem ser usadas (ex: skill em cooldown)
  aparecem em cinza com motivo (ex: "Cleave [CD: 2 turnos]")

### 1.7 Atalhos Rapidos (CS:GO Style)

O sistema de numeros JA e o sistema de atalhos. Exemplo de sequencia rapida:

```
Turno do Fighter:
  [1] -> Acao Normal
  [1] -> Ataque Basico
  [1] -> Goblin A

Total: "1-1-1" em <1 segundo = ataque rapido no primeiro alvo
```

Jogadores experientes decoram sequencias:
- `1-1-1` = ataque basico no primeiro alvo
- `1-2-1` = primeira skill no primeiro alvo
- `2-1` = mover posicao
- `4-1-1` = primeiro item no primeiro aliado

Isso da a sensacao de "buy menu do CS" que o doc original descreve.

---

## Etapa 2 — Timeline Visual de Turnos

**Objetivo**: Barra horizontal no topo mostrando a ordem de turnos do round atual,
com destaque no personagem ativo. Estilo Octopath Traveler / FFX.

### 2.1 Design Visual

```
+--[Fighter]--[Goblin A]--[Mage]--[Goblin B]--[Cleric]--[Goblin C]--+
     ^^^^^
     ATIVO (highlight amarelo, tamanho maior)
```

- Cada slot e um mini-card (48x28px) com nome abreviado e cor (party=azul, enemy=vermelho)
- Personagem ativo: borda amarela + scale 1.2x + bounce sutil
- Personagens mortos: riscados / acinzentados
- Posicao: topo da tela, acima do battlefield (Y=4, centrado horizontalmente)

### 2.2 Informacoes no Timeline

- **Hover/select** (futuro): mostra tooltip com HP% e efeitos ativos
- **Previsao**: se um efeito de speed buff/debuff mudaria a ordem, mostrar fantasma
- **Round counter**: "Round 3" ao lado esquerdo do timeline

### 2.3 Arquivos Novos

```
src/ui/components/
  turn_timeline.py          # TurnTimeline component
    - __init__(turn_order: list[str], party_names: set[str])
    - set_active(name: str)
    - set_dead(name: str)
    - draw(surface, fonts)

src/ui/layout.py            # Novas constantes TIMELINE_*
```

### 2.4 Integracao

- `InteractiveCombatScene` cria `TurnTimeline` com a ordem de `TurnOrder.get_order()`
- A cada turno, chama `set_active(combatant.name)`
- A cada morte, chama `set_dead(name)`
- Timeline redesenhada todo frame (simples, sem animacao complexa)
- Mover o ROUND_INDICATOR para dentro do TurnTimeline (limpa o layout)

### 2.5 Ajuste de Layout

O timeline vai no topo, empurrando o battlefield um pouco pra baixo:

```
Y=0  a Y=36:  TurnTimeline (36px de altura)
Y=40 a Y=480: Battlefield (ajustado)
Y=500 a Y=710: CombatLogPanel + ActionPanel
```

O `ActionPanel` (menu de acoes) pode compartilhar espaco com o `CombatLogPanel`:
- Quando esperando input: ActionPanel visivel, LogPanel reduzido (3-4 linhas)
- Quando executando/animando: ActionPanel oculto, LogPanel completo (9 linhas)

---

## Etapa 3 — Preview de Dano e Tooltips

**Objetivo**: Antes de confirmar uma acao, o jogador ve uma previsao do resultado.
Reduz frustacao de "errar o clique" e melhora decisao tatica.

### 3.1 Preview de Ataque

Quando o jogador esta no nivel 3 (selecao de alvo) e um alvo esta highlighted:

```
+----------------------------------+
|  Longsword -> Goblin A           |
|  Dano estimado: 45 ~ 60         |
|  Crit chance: 15%               |
|  Tipo: Fisico (Corte)           |
|  FRAQUEZA: Fogo! (se aplicavel) |
+----------------------------------+
```

A previsao aparece como tooltip flutuante ao lado do card do alvo.

### 3.2 Preview de Skill

```
+----------------------------------+
|  Fireball -> Goblin B            |
|  Custo: 30 MP                   |
|  Dano estimado: 80 ~ 110       |
|  Tipo: Magico (Fogo)            |
|  Efeito: Burn (3 turnos, DoT)   |
|  RESISTENCIA: -50% (se aplic.)  |
+----------------------------------+
```

### 3.3 Preview de Cura

```
+----------------------------------+
|  Heal -> Mage                    |
|  Custo: 30 MP                   |
|  Cura estimada: 65 ~ 80        |
|  HP atual: 120/300 (40%)        |
+----------------------------------+
```

### 3.4 Calculo do Preview

Funcoes puras em `src/core/combat/damage_preview.py`:

```python
@dataclass(frozen=True)
class DamagePreview:
    min_damage: int
    max_damage: int
    crit_chance_pct: float
    damage_type: DamageType
    element: ElementType | None
    weakness: bool
    resistance: bool
    resistance_mult: float

def preview_basic_attack(attacker, target) -> DamagePreview: ...
def preview_skill(skill, attacker, target) -> SkillPreview: ...
def preview_heal(skill, caster, target) -> HealPreview: ...
```

**Calculo**: Usa as mesmas formulas de `resolve_damage()` mas sem o random do crit.
- `min_damage` = dano sem crit - defesa
- `max_damage` = dano com crit - defesa
- `crit_chance` = `calculate_crit_chance(bonus)`

### 3.5 Arquivos Novos

```
src/core/combat/
  damage_preview.py         # Funcoes puras de previsao de dano/cura

src/ui/components/
  tooltip.py                # Tooltip generico (posicao, texto, cor de fundo)
  damage_tooltip.py         # Especializado para preview de dano/cura
```

### 3.6 Integracao

- `TargetSelector` recebe o resultado do preview e passa para `DamageTooltip`
- Tooltip renderizado ACIMA do card do alvo (ou ao lado se nao couber)
- Tooltip aparece instantaneamente ao mover entre alvos
- Tooltip some ao pressionar Esc ou confirmar

---

## Etapa 4 — Acoes de Classe Especificas (Bonus Actions)

**Objetivo**: Cada classe expoe suas acoes bonus unicas no menu, usando polimorfismo.

### 4.1 Protocol para Acoes de Classe

```python
# src/core/characters/class_actions.py

@dataclass(frozen=True)
class ClassActionOption:
    action_id: str           # ex: "change_stance", "toggle_overcharge"
    display_name: str        # ex: "Stance: Offensive", "Overcharge: ON"
    action_type: ActionType  # BONUS_ACTION na maioria
    is_available: bool       # False se recurso insuficiente, etc
    unavailable_reason: str  # ex: "Mana insuficiente" (quando is_available=False)
    description: str         # tooltip curto

class ClassActionProvider(Protocol):
    def get_class_actions(self) -> list[ClassActionOption]: ...
    def execute_class_action(self, action_id: str) -> list[CombatEvent]: ...
```

### 4.2 Implementacao por Classe

Cada classe implementa `ClassActionProvider` com suas acoes unicas:

| Classe | Bonus Actions |
|--------|---------------|
| **Fighter** | Mudar Estancia (Offensive/Balanced/Defensive) |
| **Mage** | Toggle Overcharge, Criar Barreira |
| **Cleric** | Toggle Channel Divinity |
| **Barbarian** | (nenhuma — fury e passiva) |
| **Paladin** | Mudar Aura (None/Protection/Attack/Vitality), Glimpse of Glory |
| **Ranger** | Marcar Alvo (Hunter's Mark) |
| **Monk** | Shift Equilibrium (Vitality/Destruction direction) |
| **Sorcerer** | Toggle Overcharged, Metamagia (trocar elemento) |
| **Warlock** | Invocar/Trocar Familiar |
| **Druid** | Shapeshift (Bear/Wolf/Eagle/Serpent), Criar Field Condition |
| **Rogue** | Entrar Stealth |
| **Bard** | (groove e passivo, nenhuma acao bonus extra) |
| **Artificer** | (suit e passivo) |

### 4.3 Integracao com Menu

O `ActionMenu` no nivel 2 de Acao Bonus faz:

```python
options = []
options.append(("Mover", move_action))
if isinstance(combatant, ClassActionProvider):  # NO! Usar Protocol check
if hasattr(combatant, 'get_class_actions'):
    for action in combatant.get_class_actions():
        options.append((action.display_name, action))
```

**Nota SOLID**: NAO usar isinstance. O Character base pode ter um metodo
`get_class_actions()` que retorna `[]` por default, e cada subclasse faz override.
Isso respeita Liskov — qualquer Character pode ser perguntado sobre class actions.

### 4.4 Arquivos Novos

```
src/core/characters/
  class_actions.py          # ClassActionOption dataclass + Protocol

src/core/classes/fighter/
  fighter.py                # Adicionar get_class_actions() + execute_class_action()
  (idem para cada classe que tem bonus actions)
```

### 4.5 Defend / Prepare Reaction

A opcao "Reacao" no menu principal (nivel 1, opcao [3]):

- **Defender**: Aplica buff temporario "Guarding" que reduz dano recebido em 50%
  ate o proximo turno. Consome REACTION.
- **Preparar Contra-Ataque**: Se atacado ate o proximo turno, realiza ataque automatico
  no atacante. Consome REACTION.

Ambas sao implementadas como Effects (StatBuff ou novo GuardEffect) aplicados ao personagem,
que expiram no inicio do proximo turno dele.

---

## Etapa 5 — QTE (Quick-Time Events)

**Objetivo**: Apos escolher uma skill, aparece uma sequencia WASD que o jogador pode tentar.
Acertar da bonus. Errar ou ignorar executa a skill normalmente (sem bonus).

### 5.1 Design (baseado no doc original QTE.txt + Legend Online)

**Trigger**: Ao confirmar uma SKILL (nao ataque basico, nao item).

**Fluxo**:
```
1. Jogador confirma skill + alvo
2. Tela mostra sequencia WASD (ex: W-A-S-D-W-S)
3. Timer visual (barra diminuindo)
4. Jogador digita a sequencia
5. Resultado:
   - PERFEITO (100% em tempo): bonus de 25% no efeito
   - BOM (>= 80% correto): bonus de 15%
   - OK (>= 50% correto): bonus de 5%
   - FALHA (< 50% ou timeout): sem bonus (skill executa normal)
```

### 5.2 Scaling de Dificuldade

Comprimento da sequencia baseado no `slot_cost` da skill (proxy de poder):

| slot_cost | Sequencia | Tempo | Exemplo |
|-----------|-----------|-------|---------|
| 1-2       | 3 teclas  | 2.0s  | W-A-S |
| 3-4       | 4 teclas  | 2.5s  | W-S-A-D |
| 5-6       | 5 teclas  | 3.0s  | W-A-D-S-W |
| 7-8       | 6 teclas  | 3.5s  | D-W-A-S-D-W |

Configuravel via JSON (`data/qte/qte_config.json`):
```json
{
  "tiers": [
    {"min_cost": 1, "max_cost": 2, "sequence_length": 3, "time_ms": 2000},
    {"min_cost": 3, "max_cost": 4, "sequence_length": 4, "time_ms": 2500},
    {"min_cost": 5, "max_cost": 6, "sequence_length": 5, "time_ms": 3000},
    {"min_cost": 7, "max_cost": 99, "sequence_length": 6, "time_ms": 3500}
  ],
  "perfect_bonus": 0.25,
  "good_bonus": 0.15,
  "ok_bonus": 0.05,
  "good_threshold": 0.8,
  "ok_threshold": 0.5
}
```

### 5.3 Visual do QTE

```
+------------------------------------------+
|                                          |
|        [W]  [A]  [S]  [D]  [W]  [S]     |
|         v    v    v                      |
|        [OK] [OK] [OK] [ ]  [ ]  [ ]     |
|                                          |
|  ████████████░░░░░░  Timer: 2.1s        |
|                                          |
+------------------------------------------+
```

- Sequencia aparece no centro da tela
- Cada tecla acertada fica verde e faz um "pop" visual
- Tecla errada fica vermelha, toca som de erro, sequencia continua
- Timer e barra visual que diminui
- Ao acabar o tempo, para onde estiver
- O jogador pode pular o QTE inteiro pressionando `Enter` (executa sem bonus)

### 5.4 Opcionalidade do QTE

**IMPORTANTE**: QTE e SEMPRE opcional.
- Pode ser desabilitado no menu de opcoes (config global)
- Pode ser pulado por skill pressionando Enter
- Skills de cura/buff tambem podem ter QTE (bonus na potencia da cura/buff)
- Em dificuldades mais altas, QTE pode ser obrigatorio para bonus maximo

### 5.5 Arquivos Novos

```
src/core/combat/
  qte_sequence.py           # QteSequence frozen dataclass, generate_sequence()
  qte_result.py             # QteGrade enum (PERFECT/GOOD/OK/FAIL), QteResult dataclass
  qte_evaluator.py          # evaluate_qte(sequence, inputs, time) -> QteResult
  qte_config.py             # QteConfig frozen dataclass + loader

src/ui/
  components/
    qte_display.py          # Renderiza sequencia WASD, timer bar, feedback visual
  input/
    qte_input_handler.py    # Captura WASD em tempo real, valida contra sequencia

data/qte/
  qte_config.json           # Config de tiers, bonus, thresholds
```

### 5.6 Integracao com ActionResolver

Apos o QTE, o `ActionResolver` recebe o `QteResult` e aplica o multiplicador:

```python
def resolve_skill(
    skill: Skill,
    caster: Character,
    targets: list[Character],
    qte_result: QteResult | None = None,   # None = QTE desabilitado
) -> list[CombatEvent]:
    multiplier = qte_result.bonus_multiplier if qte_result else 1.0
    # aplica multiplier ao dano/cura/efeito
```

---

## Etapa 6 — IA de Inimigos (RF09)

**Objetivo**: Inimigos com comportamentos distintos ao inves de sempre atacar o primeiro alvo.

### 6.1 Personalidades de IA

```python
class AiBehavior(Enum):
    AGGRESSIVE = auto()    # Foca no alvo com menos HP
    DEFENSIVE = auto()     # Prioriza auto-buff/heal quando ferido
    OPPORTUNIST = auto()   # Ataca alvos com debuffs/CC, explora fraquezas
    RANDOM = auto()        # Aleatorio (inimigos fracos)
    SUPPORT = auto()        # Buffa/cura aliados
    BOSS = auto()          # Fases de HP, mecanicas especiais
```

### 6.2 Design por Personalidade

**AGGRESSIVE**:
- Target selection: menor HP% entre alvos validos
- Prefere skills de dano se disponivel
- Ignora defesa propria

**DEFENSIVE**:
- Se HP < 50%: tenta curar (se tiver skill) ou defender
- Se HP > 50%: ataque normal
- Prioriza buffs de defesa

**OPPORTUNIST**:
- Checa fraquezas elementais dos alvos
- Prioriza alvos com debuffs ativos (vulnerability window)
- Usa skills de CC em alvos perigosos (casters)

**SUPPORT**:
- Prioriza buff em aliado mais forte
- Cura aliado com menor HP%
- So ataca se nao tiver skill de suporte pronta

**BOSS** (complexo):
- Fases de HP (100-75%, 75-50%, 50-25%, 25-0%)
- Cada fase desbloqueia skills novas
- Ataque carregado: telegrafado 1 turno antes (evento especial no log)
- Invocacao de adds (criar novos inimigos mid-combat)
- Thresholds de HP mudam comportamento (fica agressivo quando baixo)

### 6.3 Arquivos Novos

```
src/core/combat/
  ai/
    __init__.py
    ai_behavior.py          # AiBehavior enum
    ai_evaluator.py         # Funcoes puras: score_target(), pick_best_action()
    ai_turn_handler.py      # AiTurnHandler(TurnHandler) - decide baseado em behavior
    behavior_configs.py     # Config por behavior (thresholds, prioridades)
    boss_phase.py           # BossPhase tracking, threshold triggers

data/ai/
  behaviors.json            # Config de prioridades por behavior
  boss_phases.json          # Fases de boss (ex: Dragon phase 1/2/3)
```

### 6.4 Integracao

O `DispatchTurnHandler` mapeia inimigos para `AiTurnHandler`:

```python
ai_handlers = {
    "Goblin A": AiTurnHandler(AiBehavior.AGGRESSIVE, skills=[...]),
    "Goblin B": AiTurnHandler(AiBehavior.RANDOM, skills=[]),
    "Orc Shaman": AiTurnHandler(AiBehavior.SUPPORT, skills=[heal, buff]),
    "Dragon": AiTurnHandler(AiBehavior.BOSS, phases=[...]),
}
dispatch = DispatchTurnHandler(
    handlers={**player_handlers, **ai_handlers},
    default=BasicAttackHandler(),
)
```

### 6.5 Telegrafando Acoes de Boss

Bosses com ataque carregado:
```
Round 3: "Dragon se prepara para Breath of Fire!" (evento especial, sem dano)
Round 4: "Dragon usa Breath of Fire!" (AOE massivo)
```

O telegrama aparece como evento no log + animacao especial (aura vermelha pulsante no boss).
Isso da ao jogador 1 turno pra reagir (defender, buffar, curar preventivamente).

---

## Ordem de Implementacao e Dependencias

```
Etapa 1 (Player Action Menu)
  |
  +---> Etapa 2 (Timeline)        -- independente, pode ser paralela
  |
  +---> Etapa 3 (Preview de Dano) -- depende do menu (nivel 3 de selecao)
  |
  +---> Etapa 4 (Class Actions)   -- depende do menu (nivel 2 de bonus)
  |
  +---> Etapa 5 (QTE)             -- depende do menu + ActionResolver
  |
  +---> Etapa 6 (IA de Inimigos)  -- independente do menu, mas melhor depois
```

**Etapa 1 e pre-requisito de tudo.** As etapas 2-4 podem ser feitas em qualquer ordem
apos a 1. A etapa 5 depende de 1 e 3. A etapa 6 e a mais independente.

**Sugestao de execucao**:
1. Etapa 1 (obrigatoria primeiro — sem isso nao tem jogo)
2. Etapa 2 (rapida, melhora muito o feedback)
3. Etapa 3 (qualidade de vida antes de expandir acoes)
4. Etapa 4 (profundidade tatica — bonus actions de classe)
5. Etapa 6 (inimigos inteligentes — faz as taticas valerem a pena)
6. Etapa 5 (QTE — cereja do bolo, polish final)

---

## Resumo de Impacto

| Etapa | Arquivos Novos (est.) | Testes Novos (est.) | Impacto no Jogador |
|-------|----------------------|--------------------|--------------------|
| 1 - Menu | ~10 | ~80-100 | **Transforma simulacao em jogo** |
| 2 - Timeline | ~2 | ~15-20 | Feedback de ordem de turnos |
| 3 - Preview | ~4 | ~30-40 | Decisao tatica informada |
| 4 - Class Actions | ~14 (1 por classe) | ~60-80 | Profundidade das classes |
| 5 - QTE | ~6 | ~40-50 | Skill expression mecanica |
| 6 - IA | ~6 | ~50-70 | Inimigos desafiadores |
| **TOTAL** | **~42** | **~275-360** | **Jogo completo e jogavel** |

---

## Principios de Design

1. **Keyboard-first**: Tudo navegavel por teclado, mouse como fallback futuro
2. **Informacao visivel**: O jogador nunca precisa adivinhar o que uma acao faz
3. **Acao reversivel**: Esc cancela qualquer escolha ate a confirmacao final
4. **Zero frustacao**: Preview de dano evita arrependimento, acoes grayed-out evitam clicks invalidos
5. **Recompensa maestria**: Atalhos rapidos + QTE recompensam jogadores dedicados
6. **Backward-compatible**: CombatEngine continua funcionando para IA vs IA / testes / replay
7. **Core puro**: Toda logica de resolucao de acao fica em `src/core/`, sem Pygame
8. **SOLID**: Novas acoes = novos arquivos, nao modificar os existentes (OCP)
