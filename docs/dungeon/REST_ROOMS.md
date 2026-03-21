# Rest Rooms — Design Detalhado

## Conceito

Rest rooms sao pontos de pausa estrategica na run. O jogador escolhe **1 acao** dentre varias opcoes. Cada opcao tem um beneficio claro. Nao ha risco (diferente de eventos).

Rest rooms sao **raros** (1-2 por floor), entao a escolha importa.

---

## Acoes Disponiveis

O jogador escolhe **UMA** acao por rest room:

### 1. Descansar (Heal)
- **Efeito**: Cura **30% do HP max** de TODA a party
- **Quando usar**: Party desgastada, HP baixo
- **Nota**: Nao cura mana

### 2. Meditar (Mana Recovery)
- **Efeito**: Recupera **40% da mana max** de TODA a party
- **Quando usar**: Casters sem recurso

### 3. Afiar Armas (Upgrade)
- **Efeito**: Escolhe 1 arma da party → +10% dano base permanente (stack max 3x)
- **Quando usar**: Quando DPS e mais importante que sustain
- **Nota**: Buff permanente pela run inteira

### 4. Fortificar (Defense Buff)
- **Efeito**: Toda a party ganha **+15% DEF** no proximo combate (1 combate)
- **Quando usar**: Antes de elite ou boss que vc sabe que vai doer

### 5. Estudar Inimigos (Reveal)
- **Efeito**: Revela **conteudo exato** de todos os nos na proxima camada do mapa (quais monstros, qual evento, etc.)
- **Quando usar**: Quando voce quer planejar o caminho com mais informacao

### 6. Remover Maldições (Cleanse)
- **Efeito**: Remove **todos os debuffs e ailments permanentes** da party (efeitos que persistem entre combates, como curses de eventos)
- **Quando usar**: Se alguem pegou curse de evento ou reliquia ruim

### 7. Forjar (Combinar) — Requer materiais
- **Efeito**: Combina 2 consumiveis do inventario pra criar 1 consumivel superior
- **Receitas**: Pocao HP + Pocao Mana = Pocao Full Restore. 2x Antidoto = Elixir de Purificacao. etc.
- **Quando usar**: Se tem consumiveis sobrando e quer otimizar inventario
- **Nota**: So aparece se party tem 2+ consumiveis combinaveis

---

## Implementacao

```python
# src/dungeon/rooms/rest_room.py
class RestAction(Enum):
    HEAL = "heal"                 # 30% HP party
    MEDITATE = "meditate"         # 40% mana party
    SHARPEN = "sharpen"           # +10% dano 1 arma (permanente)
    FORTIFY = "fortify"           # +15% DEF proximo combate
    STUDY = "study"               # Revela proxima camada
    CLEANSE = "cleanse"           # Remove debuffs persistentes
    FORGE = "forge"               # Combinar consumiveis

class RestRoom:
    """Sala de descanso: jogador escolhe 1 acao."""

    def get_available_actions(self, state: RunState) -> list[RestAction]:
        """Retorna acoes disponiveis (filtra por contexto)."""
        # FORGE so se tem consumiveis combinaveis
        # CLEANSE so se alguem tem debuff persistente
        # STUDY so se nao esta na ultima camada
        ...

    def apply_action(self, state: RunState,
                     action: RestAction,
                     target: Character | None = None) -> RunState:
        """Aplica a acao escolhida e retorna novo estado."""
        ...
```

### Dados: `data/dungeon/rest_actions.json`

```json
{
  "heal": {
    "name": "Descansar",
    "description": "Cura 30% do HP max de toda a party",
    "icon": "campfire",
    "heal_percent": 0.30,
    "target": "party"
  },
  "meditate": {
    "name": "Meditar",
    "description": "Recupera 40% da mana max de toda a party",
    "icon": "meditation",
    "mana_percent": 0.40,
    "target": "party"
  },
  "sharpen": {
    "name": "Afiar Armas",
    "description": "+10% dano base em 1 arma (permanente, max 3x)",
    "icon": "anvil",
    "damage_buff_percent": 0.10,
    "max_stacks": 3,
    "target": "single_weapon"
  },
  "fortify": {
    "name": "Fortificar",
    "description": "+15% DEF para toda a party no proximo combate",
    "icon": "shield",
    "def_buff_percent": 0.15,
    "duration": "next_combat",
    "target": "party"
  },
  "study": {
    "name": "Estudar Inimigos",
    "description": "Revela conteudo dos nos na proxima camada",
    "icon": "book",
    "reveal_layers": 1,
    "target": "map"
  },
  "cleanse": {
    "name": "Remover Maldicoes",
    "description": "Remove todos debuffs persistentes da party",
    "icon": "holy_water",
    "target": "party"
  },
  "forge": {
    "name": "Forjar",
    "description": "Combina 2 consumiveis em 1 superior",
    "icon": "forge",
    "target": "inventory"
  }
}
```

### Receitas de Forge

```json
{
  "recipes": [
    {
      "input": ["potion_hp_small", "potion_hp_small"],
      "output": "potion_hp_medium",
      "name": "Pocao de Cura Media"
    },
    {
      "input": ["potion_mana_small", "potion_mana_small"],
      "output": "potion_mana_medium",
      "name": "Pocao de Mana Media"
    },
    {
      "input": ["potion_hp_small", "potion_mana_small"],
      "output": "potion_full_restore_small",
      "name": "Pocao de Restauracao"
    },
    {
      "input": ["antidote", "antidote"],
      "output": "elixir_purification",
      "name": "Elixir de Purificacao (cura todos ailments)"
    },
    {
      "input": ["elemental_crystal", "weapon_oil"],
      "output": "elemental_weapon_oil",
      "name": "Oleo Elemental (adiciona elemento a arma 1 combate)"
    }
  ]
}
```

---

## Balanceamento

- Rest rooms sao **escassos** (1-2 por floor) pra que a escolha tenha peso
- Heal de 30% e intencional — nao e full heal, entao gestao de HP importa
- Afiar armas stacka pra recompensar quem prioriza ofensiva sobre sustain
- Fortify so dura 1 combate pra nao ser pick automatico antes de boss
- O jogador pode ver o mapa e decidir se vale ir pro rest ou pro shop/elite
