# Plano de Implementacao - Task 2.22: Animacoes de Combate

## Visao Geral

Sistema de animacoes baseado em particulas e shapes geometricos para feedback visual de combate.
Zero assets externos — tudo com Pygame primitives (lines, circles, rects, alpha surfaces).

**Principio**: Cada animacao e uma classe pura com `update(dt_ms)`, `draw(surface)` e `is_done`.
O `AnimationManager` gerencia o ciclo de vida. O `AnimationFactory` mapeia eventos para animacoes.
A `CombatScene` integra tudo — pausa quando ha animacao blocking.

---

## Arquitetura de Arquivos

```
src/ui/animations/
  __init__.py              # Ja existe (vazio)
  animation_manager.py     # Step 1: spawn/update/draw/has_active/has_blocking
  floating_text.py         # Step 2: texto flutuante com fade (-136 HP, +45 HP)
  slash_effect.py          # Step 3: linha diagonal cruzando o alvo (ataque fisico)
  magic_burst.py           # Step 4: circulos/particulas expandindo (cor por elemento)
  heal_particles.py        # Step 5: particulas verdes subindo
  poison_bubbles.py        # Step 6: bolhas roxas oscilando (DoT tick)
  buff_aura.py             # Step 7: rect pulsante ao redor do card
  card_shake.py            # Step 8: offset oscilante no card
  death_fade.py            # Step 9: overlay escurecendo gradualmente
  animation_factory.py     # Step 10: dispatch EventType -> lista de animacoes

tests/ui/test_animations/
  __init__.py                     # Ja existe (vazio)
  test_animation_manager.py       # Ja existe (10 testes, RED phase)
  test_floating_text.py           # Step 2
  test_slash_effect.py            # Step 3
  test_magic_burst.py             # Step 4
  test_heal_particles.py          # Step 5
  test_poison_bubbles.py          # Step 6
  test_buff_aura.py               # Step 7
  test_card_shake.py              # Step 8
  test_death_fade.py              # Step 9
  test_animation_factory.py       # Step 10
```

**Modificacoes em arquivos existentes (Steps 11-12):**
- `src/ui/scenes/combat_scene.py` — integrar AnimationManager
- `src/ui/colors.py` — adicionar cores de elementos (ELEMENT_FIRE, etc)

---

## Mapeamento EventType -> Animacao

| EventType | Animacao(s) | Blocking | Duracao | Posicao |
|-----------|-------------|----------|---------|---------|
| DAMAGE (fisico) | SlashEffect + CardShake + FloatingText(vermelho) | Sim | 400ms | No card do alvo |
| DAMAGE (magico) | MagicBurst(cor_elemento) + FloatingText(vermelho) | Sim | 500ms | No card do alvo |
| HEAL | HealParticles + FloatingText(verde) | Sim | 400ms | No card do alvo |
| BUFF | BuffAura(verde) | Nao | 600ms | No card do alvo |
| DEBUFF | BuffAura(vermelho) | Nao | 600ms | No card do alvo |
| AILMENT | PoisonBubbles(roxo) | Nao | 500ms | No card do alvo |
| DEATH | DeathFade | Nao | 800ms | No card do alvo |
| SKIP_TURN | nenhuma | - | - | - |

---

## Steps de Implementacao

### Step 1: AnimationManager (TDD)
**Arquivo prod**: `src/ui/animations/animation_manager.py`
**Arquivo teste**: `tests/ui/test_animations/test_animation_manager.py` (JA EXISTE - 10 testes)

**O que faz**: Lista de animacoes ativas. spawn() adiciona, update() ticka e remove finalizadas, draw() desenha todas. Properties has_active e has_blocking.

**API**:
```python
class AnimationManager:
    def spawn(self, animation) -> None
    def update(self, dt_ms: int) -> None
    def draw(self, surface) -> None
    @property
    def has_active(self) -> bool
    @property
    def has_blocking(self) -> bool
```

**Reflexao**: Puro Python, sem Pygame. Os testes ja existem com FakeAnimation que implementa o protocol. E o alicerce — tudo depende disso. Faz sentido ser primeiro.

**Testes ja escritos**:
1. `test_starts_empty` — sem animacoes = has_active False, has_blocking False
2. `test_spawn_adds_animation` — spawn torna has_active True
3. `test_spawn_blocking_sets_has_blocking` — blocking=True → has_blocking True
4. `test_spawn_non_blocking_no_has_blocking` — blocking=False → has_active True, has_blocking False
5. `test_update_ticks_all_animations` — update ticka todas simultaneamente
6. `test_update_removes_finished` — animacao finalizada e removida
7. `test_draw_calls_all` — draw chama draw em todas as ativas
8. `test_blocking_clears_when_done` — blocking finaliza, non-blocking continua → has_blocking False
9. `test_multiple_blocking` — 2 blockings, 1 finaliza → has_blocking True ate ambas acabarem
10. `test_spawn_multiple_then_clear` — todas finalizam → has_active False

**Implementacao**: ~25 linhas. Lista interna, loop de update com filter, any() para properties.

---

### Step 2: FloatingText (TDD)
**Arquivo prod**: `src/ui/animations/floating_text.py`
**Arquivo teste**: `tests/ui/test_animations/test_floating_text.py`

**O que faz**: Texto (ex: "-136", "+45 HP") que sobe devagar e desaparece com fade. Sempre non-blocking.

**API**:
```python
class FloatingText:
    def __init__(self, text: str, x: int, y: int, color: tuple, duration_ms: int = 800):
        self.blocking = False  # sempre
    def update(self, dt_ms: int) -> None
    def draw(self, surface: pygame.Surface) -> None
    @property
    def is_done(self) -> bool
```

**Comportamento**:
- Posicao y diminui ao longo do tempo (sobe ~30px total)
- Alpha vai de 255 → 0 (fade out)
- is_done quando elapsed >= duration_ms

**Reflexao**: Non-blocking por design — numeros flutuando nao devem travar o fluxo. Precisa de pygame.Surface com alpha (SRCALPHA) para o fade. O draw usa font.render() com a cor + alpha surface. Sem dependencia de outros steps.

**Testes planejados**:
1. `test_starts_not_done` — recem-criado nao esta done
2. `test_done_after_duration` — apos duration_ms, is_done True
3. `test_not_done_before_duration` — antes de duration, is_done False
4. `test_is_non_blocking` — blocking sempre False
5. `test_y_decreases_over_time` — posicao y diminui (sobe)
6. `test_alpha_decreases_over_time` — opacidade diminui

**Nota sobre testes Pygame**: draw() precisa de pygame.Surface real. Podemos testar update/is_done sem Pygame (logica pura de posicao/alpha). Para draw, ou mockamos surface ou usamos `pygame.Surface((1,1))` com pygame.init() no conftest.

**Decisao**: Separar logica (posicao, alpha, is_done) do rendering (draw). Testar logica pura sem Pygame. Draw testamos indiretamente na integracao visual (Step 12).

---

### Step 3: SlashEffect (TDD)
**Arquivo prod**: `src/ui/animations/slash_effect.py`
**Arquivo teste**: `tests/ui/test_animations/test_slash_effect.py`

**O que faz**: Linha diagonal que cruza o card do alvo (canto superior-esquerdo → inferior-direito). Blocking.

**API**:
```python
class SlashEffect:
    def __init__(self, x: int, y: int, width: int, height: int, duration_ms: int = 300):
        self.blocking = True
    def update(self, dt_ms: int) -> None
    def draw(self, surface: pygame.Surface) -> None
    @property
    def is_done(self) -> bool
    @property
    def progress(self) -> float  # 0.0 → 1.0
```

**Comportamento**:
- Desenha linha de (x, y) ate (x+width, y+height), mas so ate `progress` do comprimento
- progress = elapsed / duration_ms (clamp 0-1)
- Linha branca/amarela grossa (width=3), talvez com trail (2a linha mais fina atrasada)
- is_done quando progress >= 1.0

**Reflexao**: Blocking porque e o principal feedback de "ataque fisico aconteceu". Curto (300ms) pra nao arrastar. A posicao (x, y, width, height) vem do card rect do alvo — o AnimationFactory vai passar isso.

**Testes planejados**:
1. `test_starts_not_done` — progress 0, is_done False
2. `test_done_after_duration` — apos duration, is_done True
3. `test_progress_halfway` — metade do tempo = ~0.5
4. `test_is_blocking` — blocking True
5. `test_progress_clamped_at_one` — update alem do duration nao passa de 1.0

---

### Step 4: MagicBurst (TDD)
**Arquivo prod**: `src/ui/animations/magic_burst.py`
**Arquivo teste**: `tests/ui/test_animations/test_magic_burst.py`

**O que faz**: Circulos concentricos expandindo do centro do card. Cor baseada no elemento. Blocking.

**API**:
```python
class MagicBurst:
    def __init__(self, cx: int, cy: int, color: tuple, duration_ms: int = 500):
        self.blocking = True
    def update(self, dt_ms: int) -> None
    def draw(self, surface: pygame.Surface) -> None
    @property
    def is_done(self) -> bool
```

**Comportamento**:
- 3 circulos concentricos com raios crescentes (progress * max_radius)
- Raios defasados: circulo 1 = progress*40, circulo 2 = progress*28, circulo 3 = progress*16
- Alpha diminui com progress (fade out)
- Cor do elemento (ver tabela de cores)

**Cores por Elemento**:
```
FIRE:      (255, 120, 30)   laranja
ICE:       (130, 200, 255)  azul claro
LIGHTNING: (255, 255, 100)  amarelo
HOLY:      (255, 255, 200)  branco quente
DARKNESS:  (100, 50, 150)   roxo escuro
Default:   (200, 200, 255)  branco azulado
```

**Reflexao**: Blocking porque magia e um evento importante. 500ms > slash (300ms) porque magias sao mais "dramaticas". Circulos concentricos sao simples de desenhar com `pygame.draw.circle()`. O fade precisa de alpha surface.

**Testes planejados**:
1. `test_starts_not_done`
2. `test_done_after_duration`
3. `test_is_blocking`
4. `test_radius_increases_over_time` — raio interno cresce com elapsed
5. `test_stores_color` — cor passada no construtor e preservada

---

### Step 5: HealParticles (TDD)
**Arquivo prod**: `src/ui/animations/heal_particles.py`
**Arquivo teste**: `tests/ui/test_animations/test_heal_particles.py`

**O que faz**: Particulas verdes (pequenos circulos) subindo a partir da base do card. Blocking.

**API**:
```python
class HealParticles:
    def __init__(self, x: int, y: int, width: int, height: int, duration_ms: int = 400):
        self.blocking = True
    def update(self, dt_ms: int) -> None
    def draw(self, surface: pygame.Surface) -> None
    @property
    def is_done(self) -> bool
```

**Comportamento**:
- 8-12 particulas com posicoes x aleatorias dentro do card width
- Cada particula sobe (y diminui) com velocidade ligeiramente diferente
- Fade out gradual
- Cor: verde claro (80, 255, 80) com variacao

**Reflexao**: Blocking porque heal e informacao critica (jogador quer ver quem foi curado). As particulas sao seedadas no construtor (posicoes fixas dado o seed) para reproducibilidade? Nao — aleatoriedade visual e ok, nao afeta logica. Testar apenas is_done/update, nao posicoes exatas das particulas.

**Testes planejados**:
1. `test_starts_not_done`
2. `test_done_after_duration`
3. `test_is_blocking`
4. `test_not_done_before_duration`
5. `test_creates_particles` — internamente tem lista de particulas (len > 0)

---

### Step 6: PoisonBubbles (TDD)
**Arquivo prod**: `src/ui/animations/poison_bubbles.py`
**Arquivo teste**: `tests/ui/test_animations/test_poison_bubbles.py`

**O que faz**: Bolhas roxas que sobem oscilando (sine wave horizontal) ao redor do card. Non-blocking.

**API**:
```python
class PoisonBubbles:
    def __init__(self, x: int, y: int, width: int, height: int, duration_ms: int = 500):
        self.blocking = False
    def update(self, dt_ms: int) -> None
    def draw(self, surface: pygame.Surface) -> None
    @property
    def is_done(self) -> bool
```

**Comportamento**:
- 5-8 bolhas (circulos de raio 3-6px)
- Sobem com oscilacao horizontal (sin(elapsed * freq + phase))
- Cor: roxo (180, 140, 255) com variacao de alpha
- Fade out no final

**Reflexao**: Non-blocking porque DoT ticks sao frequentes e travar a cada um seria irritante. Similar a HealParticles mas com oscilacao horizontal. Mesma abordagem de testes (logica pura, nao posicoes exatas).

**Testes planejados**:
1. `test_starts_not_done`
2. `test_done_after_duration`
3. `test_is_non_blocking`
4. `test_creates_bubbles`

---

### Step 7: BuffAura (TDD)
**Arquivo prod**: `src/ui/animations/buff_aura.py`
**Arquivo teste**: `tests/ui/test_animations/test_buff_aura.py`

**O que faz**: Retangulo/borda que pulsa ao redor do card do personagem. Verde para buff, vermelho para debuff. Non-blocking.

**API**:
```python
class BuffAura:
    def __init__(self, x: int, y: int, width: int, height: int, color: tuple, duration_ms: int = 600):
        self.blocking = False
    def update(self, dt_ms: int) -> None
    def draw(self, surface: pygame.Surface) -> None
    @property
    def is_done(self) -> bool
```

**Comportamento**:
- Borda ao redor do card que pulsa (alpha oscila com sin())
- 2-3 pulsacoes durante a duracao
- Cor passada como parametro (verde para BUFF, vermelho para DEBUFF)

**Reflexao**: Non-blocking para nao travar o fluxo em buffs/debuffs que sao frequentes. A pulsacao e meramente decorativa. Cor parametrizada permite reusar para BUFF e DEBUFF (verde vs vermelho). Rect pulsante = `pygame.draw.rect()` com alpha variavel.

**Testes planejados**:
1. `test_starts_not_done`
2. `test_done_after_duration`
3. `test_is_non_blocking`
4. `test_stores_color`

---

### Step 8: CardShake (TDD)
**Arquivo prod**: `src/ui/animations/card_shake.py`
**Arquivo teste**: `tests/ui/test_animations/test_card_shake.py`

**O que faz**: Retorna offset (dx, dy) oscilante para o card do alvo tremer ao receber dano. Blocking.

**API**:
```python
class CardShake:
    def __init__(self, intensity: int = 6, duration_ms: int = 300):
        self.blocking = True
    def update(self, dt_ms: int) -> None
    @property
    def offset(self) -> tuple[int, int]  # (dx, dy) para aplicar no card
    def draw(self, surface: pygame.Surface) -> None  # noop (efeito via offset)
    @property
    def is_done(self) -> bool
```

**Comportamento**:
- offset oscila rapidamente: dx/dy = intensity * sin(elapsed * freq) com decay
- Decai ao longo da duracao (tremer forte → parar)
- draw() e noop — o efeito e aplicado pelo Battlefield que desloca o card

**Reflexao**: Diferente das outras animacoes, CardShake nao desenha nada — ele produz um offset que o Battlefield aplica na posicao do card. Isso cria uma questao: como o Battlefield sabe do offset?

**Opcoes**:
1. CardShake tem referencia ao nome do personagem + AnimationManager expoe offsets → Battlefield consulta
2. CardShake desenha diretamente movendo pixels → complicado
3. CardShake e um conceito que vive no Battlefield, nao no AnimationManager → quebra padrao

**Decisao**: Opcao 1. CardShake guarda `target_name: str`. AnimationManager expoe `get_shake_offset(name) -> (int, int)` que agrega offsets de todos CardShakes ativos para aquele nome. Battlefield chama isso antes de desenhar cada card.

**Revisao**: Isso adiciona complexidade ao AnimationManager. Alternativa mais simples: CardShake.draw() redesenha o card numa posicao tremida (recebe o snapshot + fonts). Mas isso acopla CardShake ao CharacterCard.

**Decisao final**: Manter simples. CardShake.draw() e noop (nao desenha nada visual proprio). O offset e exposto como property. O AnimationFactory retorna CardShake junto com SlashEffect para DAMAGE. Na integracao (Step 11), o CombatScene/Battlefield consulta os shakes ativos. Isso e mais limpo que forcar CardShake a saber de CharacterCard.

**Testes planejados**:
1. `test_starts_not_done`
2. `test_done_after_duration`
3. `test_is_blocking`
4. `test_offset_nonzero_during_animation` — offset nao e (0,0) durante a animacao
5. `test_offset_zero_when_done` — apos finalizar, offset e (0,0)
6. `test_draw_is_noop` — draw nao faz nada (nao crasha)

---

### Step 9: DeathFade (TDD)
**Arquivo prod**: `src/ui/animations/death_fade.py`
**Arquivo teste**: `tests/ui/test_animations/test_death_fade.py`

**O que faz**: Overlay escuro que cobre gradualmente o card do personagem morto. Non-blocking.

**API**:
```python
class DeathFade:
    def __init__(self, x: int, y: int, width: int, height: int, duration_ms: int = 800):
        self.blocking = False
    def update(self, dt_ms: int) -> None
    def draw(self, surface: pygame.Surface) -> None
    @property
    def is_done(self) -> bool
    @property
    def alpha(self) -> int  # 0 → 180 (nao chega a 255 para manter visivel)
```

**Comportamento**:
- Rect preto semi-transparente sobre o card
- Alpha cresce de 0 ate ~180 ao longo da duracao
- Nao cobre 100% para o card morto ainda ser identificavel (DEAD_COLOR ja escurece)

**Reflexao**: Non-blocking porque morte e consequencia, nao acao. O jogador ja viu o dano que matou. 800ms e suficiente para o efeito dramatico. O overlay fica depois que a animacao acaba? Nao — o card ja muda para DEAD_COLOR via snapshot. O fade e so a transicao visual.

**Testes planejados**:
1. `test_starts_not_done`
2. `test_done_after_duration`
3. `test_is_non_blocking`
4. `test_alpha_starts_at_zero`
5. `test_alpha_increases_over_time`
6. `test_alpha_capped` — nao passa de max_alpha (180)

---

### Step 10: AnimationFactory (TDD)
**Arquivo prod**: `src/ui/animations/animation_factory.py`
**Arquivo teste**: `tests/ui/test_animations/test_animation_factory.py`

**O que faz**: Dispatch table que recebe CombatEvent + posicao do card e retorna lista de animacoes correspondentes.

**API**:
```python
class AnimationFactory:
    def create(self, event: CombatEvent, target_rect: tuple[int, int, int, int]) -> list:
        """Retorna lista de animacoes para o evento."""
```

**target_rect**: (x, y, width, height) do card do personagem alvo. O Battlefield/CombatScene fornece isso.

**Dispatch**:
```python
_DISPATCH = {
    EventType.DAMAGE: _create_damage_animations,
    EventType.HEAL: _create_heal_animations,
    EventType.BUFF: _create_buff_animations,
    EventType.DEBUFF: _create_debuff_animations,
    EventType.AILMENT: _create_ailment_animations,
}
```

**Logica de DAMAGE**: Checar se evento tem element (magico) ou nao (fisico):
- Fisico: SlashEffect + CardShake + FloatingText(vermelho, f"-{value}")
- Magico: MagicBurst(cor_do_elemento) + FloatingText(vermelho, f"-{value}")

**Logica de HEAL**: HealParticles + FloatingText(verde, f"+{value}")

**Logica de BUFF/DEBUFF**: BuffAura(cor)

**Logica de AILMENT**: PoisonBubbles

**Reflexao**: Segue o padrao de dispatch table do projeto (SkillEffectApplier, ConsumableEffectApplier). Extensivel — adicionar novo tipo de animacao = nova funcao, sem modificar as existentes.

**Problema**: CombatEvent tem `damage: DamageResult | None`. DamageResult tem `element: Element | None`. Quando element e None, e dano fisico. Quando tem element, e magico. Isso e suficiente para o dispatch.

**Problema 2**: CombatEvent nao tem info de "quem morreu". Morte acontece como consequencia de DAMAGE mas nao tem EventType.DEATH.
**Solucao**: A morte e detectada pelo snapshot — quando um personagem muda de is_alive=True para False entre snapshots, o CombatScene gera a animacao de DeathFade. Isso e feito na integracao (Step 11), nao no factory.

**Testes planejados**:
1. `test_damage_physical_creates_slash_and_text` — DAMAGE sem element → SlashEffect, FloatingText
2. `test_damage_magical_creates_burst_and_text` — DAMAGE com element → MagicBurst, FloatingText
3. `test_heal_creates_particles_and_text` — HEAL → HealParticles, FloatingText
4. `test_buff_creates_aura_green` — BUFF → BuffAura(verde)
5. `test_debuff_creates_aura_red` — DEBUFF → BuffAura(vermelho)
6. `test_ailment_creates_poison` — AILMENT → PoisonBubbles
7. `test_unknown_event_returns_empty` — FLEE/SKIP → lista vazia
8. `test_text_shows_value` — FloatingText contem o valor do dano/heal

---

### Step 11: Integrar AnimationManager no CombatScene
**Arquivo modificado**: `src/ui/scenes/combat_scene.py`
**Sem testes unitarios novos** — integracao visual testada no Step 12

**Mudancas**:

1. **__init__**: Criar `self._anim_manager = AnimationManager()` e `self._anim_factory = AnimationFactory()`

2. **update()**: Se `_anim_manager.has_blocking`, NAO avancar timer. Sempre chamar `_anim_manager.update(dt_ms)`.
```python
def update(self, dt_ms: int) -> bool:
    if self._finished or not self._running:
        return self._running
    self._anim_manager.update(dt_ms)
    if self._anim_manager.has_blocking:
        return self._running  # espera animacao acabar
    self._timer_ms += dt_ms
    if self._timer_ms >= layout.EVENT_DELAY_MS:
        self._timer_ms = 0
        self._advance_event()
    return self._running
```

3. **_advance_event()**: Apos adicionar evento ao log, spawnar animacoes via factory.
```python
def _advance_event(self) -> None:
    ...
    event = self._replay.events[self._event_index]
    self._update_round(event.round_number)
    self._add_event_to_log(event)
    self._spawn_animations(event)  # NOVO
    self._event_index += 1
    ...
```

4. **_spawn_animations()**: Resolver target_rect do evento, chamar factory, spawnar cada animacao.
```python
def _spawn_animations(self, event: CombatEvent) -> None:
    target_rect = self._battlefield.get_card_rect(event.target_name)
    if target_rect is None:
        return
    animations = self._anim_factory.create(event, target_rect)
    for anim in animations:
        self._anim_manager.spawn(anim)
```

5. **draw()**: Chamar `_anim_manager.draw(surface)` APOS battlefield (layer acima).
```python
def draw(self, surface: pygame.Surface) -> None:
    surface.fill(colors.BG_DARK)
    self._draw_round_indicator(surface)
    self._battlefield.draw(surface, self._fonts)
    self._anim_manager.draw(surface)  # NOVO — sobre o battlefield
    self._log_panel.draw(surface, self._fonts.medium)
    ...
```

6. **Battlefield.get_card_rect()**: Novo metodo que retorna (x, y, w, h) de um personagem pelo nome.
```python
# Em src/ui/components/battlefield.py
def get_card_rect(self, name: str) -> tuple[int, int, int, int] | None:
    for i, snap in enumerate(self._snapshot.characters):
        if snap.name == name:
            x = _pick_x(snap.position, snap.is_party)
            start_y = layout.PARTY_START_Y if snap.is_party else layout.ENEMY_START_Y
            # precisa do indice dentro do time, nao global
            ...
```

**Reflexao sobre Battlefield.get_card_rect()**: O Battlefield atualmente calcula posicoes on-the-fly no draw(). Para get_card_rect funcionar, precisamos ou: (a) duplicar a logica de posicionamento, ou (b) cachear as posicoes no draw(). Opcao (b) e melhor — ao desenhar, guardar um dict nome → rect. Mas draw() e chamado depois de update(), entao o cache pode estar desatualizado no primeiro frame.

**Decisao**: Opcao (a) — extrair a logica de posicionamento em funcao pura `_calculate_card_positions(snapshot) -> dict[str, tuple]`. Tanto draw() quanto get_card_rect() usam essa funcao. Ou mais simples: get_card_rect recalcula sempre (e O(n) com n=7 personagens, irrelevante).

**Morte**: Detectar morte comparando snapshots consecutivos:
```python
def _check_deaths(self, round_number: int) -> None:
    prev = _find_snapshot(self._replay, round_number - 1)
    curr = _find_snapshot(self._replay, round_number)
    if prev is None or curr is None:
        return
    for p, c in zip(prev.characters, curr.characters):
        if p.is_alive and not c.is_alive:
            rect = self._battlefield.get_card_rect(c.name)
            if rect:
                self._anim_manager.spawn(DeathFade(*rect))
```

---

### Step 12: Teste Visual + Commit
**Sem arquivo novo** — rodar `python scripts/run_battle_visual.py` e verificar visualmente.

**Checklist**:
- [ ] Ataque fisico: linha diagonal + shake + numero vermelho
- [ ] Ataque magico: burst colorido + numero vermelho
- [ ] Heal: particulas verdes + numero verde
- [ ] Buff: aura verde pulsante
- [ ] Debuff: aura vermelha pulsante
- [ ] Ailment: bolhas roxas
- [ ] Morte: card escurece
- [ ] CombatScene pausa durante animacoes blocking
- [ ] Non-blocking animacoes rodam em paralelo
- [ ] ESC fecha sem crash
- [ ] `pytest` — suite completa verde

---

## Dependencias entre Steps

```
Step 1 (AnimationManager)
  |
  +-- Step 2 (FloatingText)
  +-- Step 3 (SlashEffect)
  +-- Step 4 (MagicBurst)
  +-- Step 5 (HealParticles)
  +-- Step 6 (PoisonBubbles)
  +-- Step 7 (BuffAura)
  +-- Step 8 (CardShake)
  +-- Step 9 (DeathFade)
  |
  +-- Step 10 (AnimationFactory) -- depende de Steps 2-9
        |
        +-- Step 11 (Integracao CombatScene) -- depende de Step 10
              |
              +-- Step 12 (Teste Visual)
```

Steps 2-9 sao independentes entre si e podem ser feitos em qualquer ordem.
Step 10 precisa de todos os tipos de animacao implementados.
Step 11 precisa do factory pronto.
Step 12 e puro teste manual.

---

## Estimativa de Complexidade

| Step | Linhas prod | Linhas teste | Pygame? |
|------|-------------|-------------|---------|
| 1 | ~25 | ~60 (existem) | Nao |
| 2 | ~40 | ~30 | Sim (draw) |
| 3 | ~35 | ~25 | Sim (draw) |
| 4 | ~45 | ~25 | Sim (draw) |
| 5 | ~50 | ~25 | Sim (draw) |
| 6 | ~50 | ~20 | Sim (draw) |
| 7 | ~35 | ~20 | Sim (draw) |
| 8 | ~35 | ~30 | Nao (draw noop) |
| 9 | ~30 | ~25 | Sim (draw) |
| 10 | ~60 | ~40 | Nao |
| 11 | ~40 (delta) | 0 | Sim |
| 12 | 0 | 0 | Sim |
| **Total** | **~445** | **~300** | |

---

## Notas Adicionais

- **Nenhum arquivo em src/core/ sera modificado** — animacoes sao 100% camada UI
- **Testes de logica pura** (is_done, progress, alpha) nao precisam de pygame.init()
- **Testes de draw** sao indiretamente cobertos pelo teste visual (Step 12)
- **CardShake e especial**: nao desenha nada, produz offset. Integracao via Battlefield
- **Morte nao tem EventType**: detectada via diff de snapshots entre rounds
