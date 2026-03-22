# Design Patterns no RPG Turno - Guia Didatico

Documento de referencia sobre os padroes de projeto implementados no projeto,
onde estao no codigo, como funcionam e em quais outros cenarios cada padrao e util.

---

## Indice

1. [Template Method](#1-template-method)
2. [Strategy](#2-strategy)
3. [Dispatch Table (Strategy + Lookup)](#3-dispatch-table-strategy--lookup)
4. [Factory](#4-factory)
5. [Abstract Base Class (ABC) + Polimorfismo](#5-abstract-base-class-abc--polimorfismo)
6. [Protocol / Interface Segregation](#6-protocol--interface-segregation)
7. [State (Inline)](#7-state-inline)
8. [Value Object (Frozen Dataclasses)](#8-value-object-frozen-dataclasses)
9. [Dependency Injection](#9-dependency-injection)
10. [Memoization / Caching](#10-memoization--caching)

---

## 1. Template Method

### O que e?

O Template Method define o **esqueleto de um algoritmo** na classe base, delegando
passos especificos para as subclasses. A classe pai controla o *fluxo geral*;
as filhas customizam *partes* sem alterar a estrutura.

Pense assim: a receita de bolo e sempre "misturar → assar → decorar", mas cada
tipo de bolo muda os ingredientes e a decoracao. O Template Method e a receita.

### Onde esta no projeto?

**Arquivo:** `src/core/effects/effect.py` - classe `Effect`

```python
class Effect(ABC):
    """Lifecycle (Template Method):
        on_apply() -> tick() cada turno -> on_expire()
    """

    def tick(self) -> TickResult:
        """ESQUELETO FIXO: ninguem sobrescreve este metodo."""
        if self._expired:
            return TickResult()
        result = self._do_tick()          # <-- hook: subclasse sobrescreve
        self._decrement_duration()        # <-- passo fixo
        return result

    def _do_tick(self) -> TickResult:     # hook padrao (no-op)
        return TickResult()

    def on_apply(self) -> None: ...       # hook: chamado ao aplicar
    def on_expire(self) -> None: ...      # hook: chamado ao expirar
    def get_modifiers(self) -> list[StatModifier]: return []  # hook
```

**Subclasses concretas:**
- `src/core/effects/stat_buff.py` → `StatBuff` sobrescreve `get_modifiers()`
- `src/core/effects/stat_debuff.py` → `StatDebuff` sobrescreve `get_modifiers()`

O `tick()` nunca e sobrescrito. O fluxo e sempre:
1. Checar se expirou
2. Chamar `_do_tick()` (hook customizavel)
3. Decrementar duracao

### Como funciona na pratica?

Quando o `EffectManager` chama `effect.tick()` a cada turno, ele nao se importa
se o efeito e um buff, debuff, DoT (damage over time) ou HoT (heal over time).
O algoritmo e o mesmo pra todos. So o _conteudo_ do hook muda.

### Quando usar em outros projetos?

| Cenario | Exemplo |
|---------|---------|
| **Processar pedidos** | Fluxo: validar → calcular → cobrar → notificar. Cada tipo de pedido valida diferente |
| **Parsers de arquivos** | Fluxo: abrir → ler header → processar linhas → fechar. CSV, JSON, XML = hooks diferentes |
| **Game loops** | Fluxo: input → update → render. Cada cena (menu, batalha, mapa) sobrescreve os hooks |
| **ETL (dados)** | Fluxo: extract → transform → load. Cada fonte de dados muda extract e transform |
| **Testes automatizados** | Fluxo: setup → execute → assert → teardown. Frameworks como pytest usam isso (fixtures) |

### Regra de ouro

> Use Template Method quando o **fluxo geral** e fixo mas os **detalhes** variam.
> Se o fluxo inteiro muda, use Strategy.

---

## 2. Strategy

### O que e?

Strategy permite trocar o **algoritmo inteiro** em tempo de execucao. Em vez de
hardcodar uma logica dentro de uma classe, voce injeta um objeto que implementa
essa logica. Quer mudar o comportamento? Troca o objeto.

### Onde esta no projeto?

**Arquivos:**
- `src/core/combat/combat_engine.py` → define `TurnHandler` (Protocol) e `CombatEngine`
- `src/core/combat/basic_attack_handler.py` → estrategia concreta `BasicAttackHandler`

```python
# A INTERFACE (contrato)
class TurnHandler(Protocol):
    """Strategy: decide e executa a acao de um combatente no turno."""
    def execute_turn(self, context: TurnContext) -> list[CombatEvent]: ...

# O CONSUMIDOR (nao sabe qual estrategia vai receber)
class CombatEngine:
    def __init__(
        self,
        party: list[Character],
        enemies: list[Character],
        turn_handler: TurnHandler,    # <-- estrategia injetada
    ) -> None:
        self._handler = turn_handler

    def _execute_combatant_turn(self, combatant_proto):
        # ...monta o contexto...
        self._events.extend(self._handler.execute_turn(context))
        #                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        #                    chama a estrategia, seja qual for
```

O `CombatEngine` **nunca sabe** se esta usando `BasicAttackHandler`, uma IA
avancada, ou o input do jogador. Ele so chama `execute_turn()`.

### Como funciona na pratica?

```python
# Combate com IA basica (so ataque basico)
engine = CombatEngine(party, enemies, BasicAttackHandler())

# Combate com IA avancada (futuro - sem mudar CombatEngine!)
engine = CombatEngine(party, enemies, SmartAIHandler())

# Combate PvP controlado pelo jogador (futuro)
engine = CombatEngine(party, enemies, PlayerInputHandler())
```

### Quando usar em outros projetos?

| Cenario | Exemplo |
|---------|---------|
| **Ordenacao** | `sort(data, strategy=quicksort)` vs `sort(data, strategy=mergesort)` |
| **Autenticacao** | Login com senha, OAuth, biometrico = estrategias diferentes |
| **Pagamento** | Pix, cartao, boleto = cada um e uma strategy de `PaymentProcessor` |
| **Compressao** | ZIP, GZIP, LZ4 = estrategias de `Compressor` |
| **IA de jogos** | Inimigo agressivo, defensivo, evasivo = trocar strategy por dificuldade |
| **Notificacoes** | Email, SMS, push = estrategias de `Notifier` |

### Strategy vs Template Method

| | Template Method | Strategy |
|---|---|---|
| **O que varia** | Partes de um algoritmo fixo | O algoritmo inteiro |
| **Como varia** | Heranca (subclasses) | Composicao (objeto injetado) |
| **Quando decidir** | Compile time (classe escolhida) | Runtime (trocar objeto) |
| **Exemplo no projeto** | `Effect.tick()` com hooks | `CombatEngine` com `TurnHandler` |

---

## 3. Dispatch Table (Strategy + Lookup)

### O que e?

E uma variacao de Strategy onde voce tem um **mapa** de chaves para estrategias.
Em vez de uma estrategia unica, voce tem varias, e o sistema escolhe qual usar
baseado em algum criterio (nome, tipo, etc), com um fallback padrao.

### Onde esta no projeto?

**Arquivo:** `src/core/combat/dispatch_handler.py`

```python
class DispatchTurnHandler:
    def __init__(
        self,
        handlers: dict[str, TurnHandler],  # mapa: nome → estrategia
        default: TurnHandler,              # fallback
    ) -> None:
        self._handlers = handlers
        self._default = default

    def execute_turn(self, context: TurnContext) -> list[CombatEvent]:
        handler = self._handlers.get(context.combatant.name, self._default)
        #         ^^^^^^^^^^^^^^^^^^ lookup no mapa
        return handler.execute_turn(context)
```

### Como funciona na pratica?

```python
# Boss com IA especial, resto usa IA basica
handlers = {
    "Dragon Lord": BossAIHandler(),
    "Healer Minion": HealerAIHandler(),
}
dispatch = DispatchTurnHandler(handlers, default=BasicAttackHandler())
engine = CombatEngine(party, enemies, dispatch)
# Dragon Lord usa BossAIHandler
# Healer Minion usa HealerAIHandler
# Qualquer outro usa BasicAttackHandler
```

### Quando usar em outros projetos?

| Cenario | Exemplo |
|---------|---------|
| **Rotas de API** | `{"/users": UserHandler, "/items": ItemHandler}` |
| **Processador de eventos** | `{"click": on_click, "hover": on_hover}` |
| **Serializacao** | `{"json": JsonSerializer, "xml": XmlSerializer}` |
| **Comandos de chat** | `{"!help": help_cmd, "!ban": ban_cmd}` |

### Vantagem sobre if/elif

```python
# RUIM - cadeia de ifs (viola Open/Closed)
if name == "Dragon Lord":
    do_boss_stuff()
elif name == "Healer":
    do_heal_stuff()
else:
    do_basic_stuff()

# BOM - dispatch table (respeita Open/Closed)
handlers[name].execute(context)
# Adicionar comportamento novo = adicionar entrada no dict, nao mudar codigo
```

---

## 4. Factory

### O que e?

Factory encapsula a **logica de criacao** de objetos. Em vez de o chamador
saber todos os detalhes de como montar um objeto, ele pede pra factory e recebe
o objeto pronto. Isso centraliza regras de criacao e evita duplicacao.

### Onde esta no projeto?

#### 4a. Factory Functions (funcoes livres)

**Arquivo:** `src/core/effects/buff_factory.py`

```python
def create_flat_buff(
    stat: ModifiableStat, flat: int, duration: int,
) -> StatBuff:
    """Cria buff com modificacao flat. Ex: +10 Physical Attack por 3 turnos."""
    modifier = StatModifier(stat=stat, flat=flat)
    return StatBuff(modifier=modifier, duration=duration)

def create_flat_debuff(
    stat: ModifiableStat, flat: int, duration: int,
) -> StatDebuff:
    """Recebe valor positivo, nega internamente."""
    modifier = StatModifier(stat=stat, flat=-abs(flat))  # <-- encapsula a negacao
    return StatDebuff(modifier=modifier, duration=duration)
```

Sem a factory, todo lugar que cria um debuff precisaria lembrar de negar o valor.
Com a factory, `create_flat_debuff(SPEED, 5, 3)` faz certo automaticamente.

#### 4b. Factory Methods (classmethod)

**Arquivo:** `src/core/characters/class_modifiers.py`

```python
@dataclass(frozen=True)
class ClassModifiers:
    hit_dice: int
    mod_hp_flat: int
    # ...8+ campos

    @classmethod
    def from_json(cls, filepath: str) -> ClassModifiers:
        """Constroi ClassModifiers a partir de um arquivo JSON."""
        raw = json.loads(Path(filepath).read_text(encoding="utf-8"))
        return cls(**raw)
```

O `from_json` e um **construtor alternativo**. Ele sabe como transformar JSON nos
parametros certos. O chamador so faz `ClassModifiers.from_json("data/fighter.json")`.

### Quando usar em outros projetos?

| Cenario | Exemplo |
|---------|---------|
| **Conexoes de BD** | `ConnectionFactory.create("postgres", host, port)` - esconde driver details |
| **UI components** | `ButtonFactory.create("primary")` vs `ButtonFactory.create("danger")` |
| **Personagens de jogo** | `CharacterFactory.create_from_template("warrior_lvl5")` |
| **Notificacoes** | `NotificationFactory.create("email", recipient, body)` |
| **Objetos complexos** | Quando o construtor tem 5+ params e regras de validacao |
| **Desserializacao** | `from_json()`, `from_dict()`, `from_csv()` |

### Regra de ouro

> Use Factory quando a **criacao e complexa**, tem **regras escondidas**
> (como negar valores), ou quando voce quer **desacoplar** quem usa de quem cria.

---

## 5. Abstract Base Class (ABC) + Polimorfismo

### O que e?

ABC define um **contrato** que todas as subclasses devem cumprir. Se voce herdar
de uma ABC e nao implementar os metodos abstratos, o Python nem deixa instanciar.
Isso garante que toda subclasse tem as capacidades esperadas.

Polimorfismo e a consequencia: codigo que trabalha com a classe base funciona
automaticamente com qualquer subclasse.

### Onde esta no projeto?

**Contrato base:** `src/core/effects/effect.py`

```python
class Effect(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...        # toda subclasse DEVE ter nome

    @property
    @abstractmethod
    def stacking_key(self) -> str: ... # toda subclasse DEVE ter chave de stacking
```

**Subclasses que cumprem o contrato:**

`src/core/effects/stat_buff.py`:
```python
class StatBuff(Effect):
    @property
    def name(self) -> str:
        return f"{_format_stat_name(self._modifier.stat)} Up"

    @property
    def stacking_key(self) -> str:
        return f"buff_{self._modifier.stat.name.lower()}"
```

`src/core/effects/stat_debuff.py`:
```python
class StatDebuff(Effect):
    @property
    def name(self) -> str:
        return f"{_format_stat_name(self._modifier.stat)} Down"

    @property
    def stacking_key(self) -> str:
        return f"debuff_{self._modifier.stat.name.lower()}"
```

**Polimorfismo em acao:** `src/core/effects/effect_manager.py`

```python
class EffectManager:
    def add_effect(self, effect: Effect) -> None:
        # Nao importa se e StatBuff, StatDebuff, DoT, HoT...
        # Qualquer Effect funciona aqui. Isso e polimorfismo.
        policy = self._get_policy(effect.stacking_key)
        self._apply_stacking(effect, policy)

    def tick_all(self) -> list[TickResult]:
        for effect in list(self._effects):
            result = effect.tick()   # cada tipo de efeito faz seu tick diferente
```

**Hierarquia de personagens:** `src/core/characters/character.py` → `Fighter`, `Mage`, `Cleric`

```python
# Fighter sobrescreve respeitando LSP (Liskov Substitution)
class Fighter(Character):
    @property
    def physical_attack(self) -> int:
        base = super().physical_attack        # usa formula do pai
        return int(base * self._current_stance_mod.atk_multiplier)  # aplica stance

class Mage(Character):
    def take_damage(self, amount: int) -> int:
        remaining = self._barrier.absorb(amount)  # barreira absorve primeiro
        return super().take_damage(remaining)      # depois vai pro HP
```

Qualquer codigo que funciona com `Character` funciona com `Fighter` ou `Mage`.
Isso e **Liskov Substitution Principle** (LSP): subclasses nao quebram o contrato.

### Quando usar em outros projetos?

| Cenario | Exemplo |
|---------|---------|
| **Shapes (classico)** | `Shape` ABC com `area()` e `perimeter()`. `Circle`, `Rectangle` implementam |
| **Repositorios** | `Repository` ABC com `save()`, `find()`. `PostgresRepo`, `MongoRepo` implementam |
| **Transporte** | `Transport` ABC com `send()`. `EmailTransport`, `SMSTransport` implementam |
| **Plugins** | `Plugin` ABC com `activate()`, `deactivate()`. Cada plugin implementa |

---

## 6. Protocol / Interface Segregation

### O que e?

Protocols sao **contratos leves** baseados em estrutura ("se tem esses metodos, serve").
Diferente de ABC, nao precisa herdar explicitamente - se o objeto tem os metodos
certos, ele ja satisfaz o Protocol. Isso e chamado **duck typing estrutural**.

Interface Segregation significa: interfaces pequenas e focadas. Ninguem e forcado
a implementar metodo que nao usa.

### Onde esta no projeto?

O projeto tem **3 Protocols separados**, cada um com poucos metodos:

**`Combatant`** em `src/core/combat/turn_order.py`:
```python
@runtime_checkable
class Combatant(Protocol):
    @property
    def name(self) -> str: ...
    @property
    def speed(self) -> int: ...
    @property
    def is_alive(self) -> bool: ...
```
Usado por `TurnOrder` para ordenar turnos. So precisa de nome, speed e se ta vivo.

**`Targetable`** em `src/core/combat/targeting.py`:
```python
@runtime_checkable
class Targetable(Protocol):
    @property
    def is_alive(self) -> bool: ...
    @property
    def position(self) -> Position: ...
```
Usado por `get_valid_targets()`. So precisa saber se ta vivo e a posicao.

**`TurnHandler`** em `src/core/combat/combat_engine.py`:
```python
class TurnHandler(Protocol):
    def execute_turn(self, context: TurnContext) -> list[CombatEvent]: ...
```
Usado pelo `CombatEngine`. Metodo unico.

### Por que 3 Protocols e nao 1 interface gigante?

```python
# RUIM - interface monolitica
class CombatEntity(Protocol):
    name: str
    speed: int
    is_alive: bool
    position: Position
    hp: int
    mana: int
    def execute_turn(...): ...
    def take_damage(...): ...
    def apply_effect(...): ...

# BOM - interfaces segregadas
# TurnOrder so precisa de Combatant (name, speed, is_alive)
# Targeting so precisa de Targetable (is_alive, position)
# CombatEngine so precisa de TurnHandler (execute_turn)
```

Com ISP, cada modulo depende apenas do **minimo necessario**. `TurnOrder` nunca
precisa saber sobre `position` ou `mana`. Se adicionarmos mana no futuro,
`TurnOrder` nao muda.

### Quando usar em outros projetos?

| Cenario | Exemplo |
|---------|---------|
| **Logger** | `Loggable` Protocol com `log(msg)`. Qualquer classe que logar satisfaz |
| **Serializacao** | `Serializable` Protocol com `to_dict()`. Sem forcar heranca |
| **Cache** | `Cacheable` Protocol com `cache_key()`. Qualquer objeto cacheavel |
| **Eventos** | `EventHandler` Protocol com `handle(event)`. Qualquer subscriber |

### Protocol vs ABC - quando usar cada?

| | Protocol | ABC |
|---|---|---|
| **Heranca necessaria?** | Nao (duck typing) | Sim (heranca explicita) |
| **Enforcement** | Checado pelo type checker (mypy) | Checado em runtime (`TypeError`) |
| **Ideal pra** | Interfaces leves entre modulos | Hierarquias com logica compartilhada |
| **No projeto** | `Combatant`, `Targetable`, `TurnHandler` | `Effect` |

---

## 7. State (Inline)

### O que e?

O padrao State permite que um objeto **mude seu comportamento** quando seu estado
interno muda. Parece que o objeto trocou de classe. No projeto usamos a versao
"inline" (mais leve), onde o estado e um enum/flag e as properties reagem a ele.

### Onde esta no projeto?

#### Fighter - Estancias (Stance)

**Arquivos:**
- `src/core/classes/fighter/stance.py` - enum `Stance` + dados `StanceModifier`
- `src/core/classes/fighter/fighter.py` - comportamento muda com a stance

```python
# Os estados possiveis
class Stance(Enum):
    NORMAL = auto()
    OFFENSIVE = auto()     # +ataque, -defesa
    DEFENSIVE = auto()     # -ataque, +defesa

# Os multiplicadores vem do JSON (data driven!)
@dataclass(frozen=True)
class StanceModifier:
    atk_multiplier: float   # ex: 1.3 (offensive) ou 0.8 (defensive)
    def_multiplier: float   # ex: 0.8 (offensive) ou 1.3 (defensive)
```

```python
# Fighter muda de comportamento baseado na stance ATUAL
class Fighter(Character):
    def change_stance(self, new_stance: Stance) -> None:
        self._stance = new_stance   # muda o estado

    @property
    def physical_attack(self) -> int:
        base = super().physical_attack
        return int(base * self._current_stance_mod.atk_multiplier)
        #                  ^^^^^^^^^^^^^^^^^^^^^^^^^^
        #                  resultado muda conforme stance!
```

#### Mage - Overcharge

**Arquivo:** `src/core/classes/mage/mage.py`

```python
class Mage(Character):
    def activate_overcharge(self) -> bool:
        self._overcharged = True    # muda estado

    @property
    def magical_attack(self) -> int:
        base = super().magical_attack
        if self._overcharged:                               # comportamento muda!
            return int(base * _OVERCHARGE_CONFIG.atk_multiplier)
        return base
```

### State "completo" vs State "inline"

No projeto usamos a versao inline (enum + ifs nas properties). Para sistemas
mais complexos, o padrao State completo usa classes separadas por estado:

```python
# State completo (nao no projeto, mas pra referencia futura)
class CombatState(ABC):
    @abstractmethod
    def on_enter(self, context): ...
    @abstractmethod
    def on_exit(self, context): ...
    @abstractmethod
    def update(self, context): ...

class PlayerTurnState(CombatState): ...
class EnemyTurnState(CombatState): ...
class VictoryState(CombatState): ...
```

### Quando usar em outros projetos?

| Cenario | Exemplo |
|---------|---------|
| **Pedido (e-commerce)** | Pendente → Pago → Enviado → Entregue. Cada estado tem acoes diferentes |
| **Player de musica** | Playing → Paused → Stopped. `play()` faz coisas diferentes em cada estado |
| **Conexao de rede** | Disconnected → Connecting → Connected → Error |
| **Editor de texto** | Normal → Insert → Visual (tipo Vim). Cada tecla faz algo diferente por estado |
| **Semaforo** | Verde → Amarelo → Vermelho. Comportamento muda ciclicamente |

---

## 8. Value Object (Frozen Dataclasses)

### O que e?

Value Objects sao objetos **imutaveis** identificados pelo seu valor, nao por
identidade. Dois `DamageResult` com os mesmos campos sao iguais. Nao podem
ser modificados apos criacao (frozen = True). Isso previne bugs de estado
compartilhado e torna o codigo mais previsivel.

### Onde esta no projeto?

O projeto usa `@dataclass(frozen=True)` extensivamente:

```python
# src/core/combat/damage.py
@dataclass(frozen=True)
class DamageResult:
    raw_damage: int
    defense_value: int
    is_critical: bool
    final_damage: int

# src/core/combat/combat_engine.py
@dataclass(frozen=True)
class CombatEvent:
    round_number: int
    actor_name: str
    target_name: str
    damage: DamageResult

@dataclass(frozen=True)
class TurnContext:
    combatant: Character
    allies: list[Character]
    enemies: list[Character]
    action_economy: ActionEconomy
    round_number: int

# src/core/effects/stat_modifier.py
@dataclass(frozen=True)
class StatModifier:
    stat: ModifiableStat
    flat: int = 0
    percent: float = 0.0

# src/core/classes/fighter/stance.py
@dataclass(frozen=True)
class StanceModifier:
    atk_multiplier: float
    def_multiplier: float
```

**Lista completa de Value Objects no projeto:**
`DamageResult`, `CombatEvent`, `TurnContext`, `StatModifier`, `TickResult`,
`ClassModifiers`, `CombatLogEntry`, `HpInput`, `AttackInput`, `DefenseInput`,
`ThresholdEntry`, `StanceModifier`, `OverchargeConfig`, `DivinityConfig`

### Por que frozen?

```python
result = resolve_damage(100, 30)
result.final_damage = 999   # ERRO! frozen=True impede isso

# Sem frozen, alguem poderia acidentalmente mudar o resultado
# e corromper o estado do combate
```

### Quando usar em outros projetos?

| Cenario | Exemplo |
|---------|---------|
| **Dinheiro** | `Money(amount=100, currency="BRL")` - imutavel, comparavel por valor |
| **Coordenadas** | `Point(x=10, y=20)` - dois points iguais sao o mesmo ponto |
| **DTOs de API** | `UserResponse(id=1, name="Ana")` - dados que so transitam, nao mudam |
| **Configs** | `DatabaseConfig(host, port, db)` - config carregada uma vez, nao muda |
| **Eventos** | `OrderPlaced(order_id, timestamp)` - evento ja aconteceu, nao muda |

### Regra de ouro

> Se o objeto **carrega dados** e nao deveria **mudar apos criacao**, faca frozen.
> Se precisa de igualdade por valor (dois objetos com mesmos campos = iguais), e Value Object.

---

## 9. Dependency Injection

### O que e?

Dependency Injection (DI) significa: em vez de uma classe **criar** suas dependencias
internamente, ela **recebe** elas pelo construtor. Isso permite trocar implementacoes
facilmente (inclusive nos testes com mocks).

### Onde esta no projeto?

**Em todo lugar.** E o padrao mais difuso do projeto. Exemplos:

```python
# CombatEngine RECEBE o TurnHandler, nao cria internamente
class CombatEngine:
    def __init__(
        self,
        party: list[Character],
        enemies: list[Character],
        turn_handler: TurnHandler,    # INJETADO
    ) -> None: ...

# Fighter RECEBE threshold_calculator e class_modifiers
class Fighter(Character):
    def __init__(
        self,
        name: str,
        attributes: Attributes,
        class_modifiers: ClassModifiers,         # INJETADO
        *,
        threshold_calculator: ThresholdCalculator, # INJETADO
    ) -> None: ...

# DispatchTurnHandler RECEBE o mapa de handlers e o default
class DispatchTurnHandler:
    def __init__(
        self,
        handlers: dict[str, TurnHandler],  # INJETADO
        default: TurnHandler,              # INJETADO
    ) -> None: ...
```

### Sem DI vs Com DI

```python
# RUIM - cria dependencia internamente (acoplado, impossivel de testar isolado)
class CombatEngine:
    def __init__(self, party, enemies):
        self._handler = BasicAttackHandler()  # hardcoded!

# BOM - recebe dependencia (desacoplado, facil de mockar)
class CombatEngine:
    def __init__(self, party, enemies, turn_handler: TurnHandler):
        self._handler = turn_handler  # qualquer implementacao serve
```

### Como facilita os testes?

```python
# No teste, voce injeta um mock
class FakeHandler:
    def execute_turn(self, context):
        return []  # nao faz nada - so pra testar o engine

engine = CombatEngine(party, enemies, FakeHandler())
# Agora voce testa CombatEngine isoladamente, sem depender de BasicAttackHandler
```

### Quando usar em outros projetos?

**Sempre.** DI e um principio fundamental, nao apenas um padrao. Use quando:

| Cenario | Exemplo |
|---------|---------|
| **Repositorios** | `UserService(repo: UserRepository)` - troca Postgres por SQLite no teste |
| **APIs externas** | `PaymentService(gateway: PaymentGateway)` - mocka nos testes |
| **Logging** | `App(logger: Logger)` - troca entre file logger e console logger |
| **Cache** | `ProductService(cache: Cache)` - troca Redis por dict em testes |

### Regra de ouro

> Se uma classe **usa** outra classe, ela deve **receber** em vez de **criar**.
> Excecao: Value Objects e tipos basicos podem ser criados internamente.

---

## 10. Memoization / Caching

### O que e?

Memoization e guardar o resultado de uma computacao cara para nao repetir.
Na proxima chamada, retorna o valor salvo. Se os dados mudarem, invalida o cache.

### Onde esta no projeto?

**Arquivo:** `src/core/characters/character.py` - `get_threshold_bonuses()`

```python
def get_threshold_bonuses(self) -> dict[str, int]:
    if self._threshold_cache is not None:
        return self._threshold_cache   # retorna cache
    # Calculo caro: agrega bonuses de 7 atributos
    total: dict[str, int] = {}
    for attr_type in AttributeType:
        # ... calcula thresholds para cada atributo ...
    self._threshold_cache = total      # salva no cache
    return total

def invalidate_threshold_cache(self) -> None:
    """Chamado quando atributos mudam (level up, buff)."""
    self._threshold_cache = None
```

### Quando usar em outros projetos?

| Cenario | Exemplo |
|---------|---------|
| **Fibonacci** | Classico: `fib(n)` sem cache = O(2^n), com cache = O(n) |
| **Queries de BD** | Cachear resultado de queries frequentes que mudam pouco |
| **API calls** | Cachear respostas de APIs externas com TTL |
| **Renderizacao** | Cachear resultados de calculos de layout/rendering |
| **Compilacao** | Cachear resultados intermediarios (como webpack faz) |

### Cuidado

> Cache invalido e uma das maiores fontes de bugs. Sempre tenha um mecanismo
> de invalidacao claro (`invalidate_threshold_cache()` no projeto).

---

## Resumo Visual

```
                    Padroes no RPG Turno
                    ====================

    CRIACAO                    COMPORTAMENTO              ESTRUTURA
    -------                    -------------              ---------
    Factory Functions          Template Method            Protocol (ISP)
    Factory Method             Strategy                   ABC + Polimorfismo
    (from_json)                Dispatch Table             Value Object
                               State (inline)             (frozen dataclass)

                    PRINCIPIOS TRANSVERSAIS
                    -----------------------
                    Dependency Injection
                    Memoization / Caching
                    Enums (type safety)
```

---

## Referencias

- **"Design Patterns" (GoF)** - Gamma, Helm, Johnson, Vlissides
- **"Head First Design Patterns"** - Freeman & Robson (mais didatico)
- **"Clean Code"** - Robert C. Martin
- **"Refactoring"** - Martin Fowler
- **Python docs**: `abc` module, `typing.Protocol`, `dataclasses`
