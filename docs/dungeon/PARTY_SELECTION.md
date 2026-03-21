# Party Selection — Design Detalhado

## Conceito

Antes de cada run, o jogador **monta sua party de 4** escolhendo entre as classes desbloqueadas. A composicao da party e uma das decisoes mais impactantes do jogo — determina sinergia, cobertura elemental, e estrategia de combate.

---

## Fluxo da Tela de Party Selection

```
┌─────────────────────────────────────────────────────────┐
│                    PARTY SELECTION                       │
│                                                         │
│  Classes Disponiveis:                                   │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐         │
│  │FIGHTER│ │ MAGE │ │CLERIC│ │ROGUE │ │RANGER│         │
│  │  🔴  │ │  🔵  │ │  🟡  │ │  🟢  │ │  🟤  │         │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘         │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐         │
│  │PALADIN│ │BARBAR│ │ BARD │ │ MONK │ │DRUID │         │
│  │  ⚪  │ │  🔴  │ │  🟣  │ │  🟠  │ │  🟢  │         │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘         │
│  ┌──────┐ ┌──────┐ ┌──────┐                            │
│  │SORCR │ │WARLCK│ │ARTFCR│                            │
│  │  🔵  │ │  🟣  │ │  🟤  │                            │
│  └──────┘ └──────┘ └──────┘                            │
│                                                         │
│  Party Selecionada: [1/4]                               │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐                  │
│  │CLERIC│ │  ??  │ │  ??  │ │  ??  │                  │
│  └──────┘ └──────┘ └──────┘ └──────┘                  │
│                                                         │
│  [INFO: Stats] [CONFIRM] [BACK]                         │
└─────────────────────────────────────────────────────────┘
```

### Fluxo

1. Jogador ve todas as classes **desbloqueadas** (cinza = bloqueada)
2. Clica numa classe → ve detalhes (stats, habilidades, arma inicial, posicao preferida)
3. Confirma → classe adicionada a party (slot 1 de 4)
4. Repete ate 4 membros
5. Pode reordenar (drag) e trocar posicao (FRONT/BACK)
6. Pode remover e trocar ate confirmar
7. **CONFIRM** → inicia run

### Regras

- **Sem duplicatas**: nao pode ter 2 da mesma classe
- **Min 1 FRONT**: pelo menos 1 membro deve ser frontline
- **Classes bloqueadas**: aparecem com icone de cadeado + requisito pra desbloquear
- **Nao precisa de healer**: composicao livre, mas UI pode avisar se nao tem sustain

---

## Informacoes Exibidas por Classe

Ao selecionar uma classe, o painel lateral mostra:

```
┌─────────────────────────────────┐
│ FIGHTER                    🔴   │
│ ─────────────────────────────── │
│ Papel: DPS / Tank Fisico        │
│ Posicao: FRONT                  │
│ HP: ████████████ (Alto)         │
│ Mana: ████ (Baixo)             │
│ ATK Fisico: █████████ (Alto)    │
│ ATK Magico: ████ (Baixo)       │
│ DEF Fisica: ███████ (Alto)     │
│ DEF Magica: ████ (Medio)       │
│                                 │
│ Arma Inicial: Long Sword (d8)  │
│ Recurso Especial: Stance System │
│ Fraqueza: Baixa mobilidade      │
│                                 │
│ Sinergia: Barbarian, Cleric     │
│ ─────────────────────────────── │
│ [ADICIONAR A PARTY]             │
└─────────────────────────────────┘
```

### Sinergias Sugeridas

A UI mostra sinergias entre classes pra ajudar novatos:

| Classe | Sinergiza com | Razao |
|--------|--------------|-------|
| Fighter | Cleric, Bard | Tank precisa de heal/buff |
| Mage | Sorcerer, Druid | Elemental combos/reactions |
| Cleric | Fighter, Paladin | Heal + frontline tanky |
| Rogue | Ranger, Bard | Backline DPS + suporte |
| Ranger | Rogue, Druid | Natureza + backline combo |
| Paladin | Cleric, Fighter | Double tank + heal |
| Barbarian | Fighter, Cleric | Frontline brutal + sustain |
| Bard | Qualquer | Versatil, buffa todo mundo |
| Monk | Rogue, Ranger | Combo hits, high speed |
| Druid | Mage, Ranger | Natureza + elemental |
| Sorcerer | Mage, Warlock | Burst magico maximo |
| Warlock | Sorcerer, Cleric | Dark magic + sustain |
| Artificer | Ranger, Rogue | Suporte tatico + utility |

---

## Party Composition Archetypes

Sugestoes (nao obrigatorio, pra novatos):

| Nome | Composicao | Estrategia |
|------|-----------|-----------|
| **Classica** | Fighter + Mage + Cleric + Rogue | Equilibrada, cobre tudo |
| **Rush** | Barbarian + Rogue + Ranger + Monk | DPS puro, mata rapido |
| **Fortaleza** | Fighter + Paladin + Cleric + Bard | Imortal, slow but safe |
| **Elemental** | Mage + Sorcerer + Druid + Warlock | Reactions a cada turno |
| **Chaos** | Bard + Monk + Artificer + Sorcerer | Imprevisivel, divertido |

---

## Desbloqueio de Classes

### Ordem de Desbloqueio (Meta-progressao)

| Fase | Classes Disponíveis | Requisito |
|------|-------------------|-----------|
| Inicial | Fighter, Mage, Cleric, Rogue | Sempre disponivel |
| Tier 1 | +Ranger, +Paladin | Completar Floor 1 (1x) |
| Tier 2 | +Barbarian, +Bard, +Monk | Completar Floor 2 (1x) |
| Tier 3 | +Druid, +Sorcerer, +Warlock | Completar Floor 3 (1x) |
| Tier 4 | +Artificer | Completar run com 3+ modifiers |

### Tela de Classe Bloqueada

```
┌─────────────────────────────────┐
│ ??? (BLOQUEADO)            🔒   │
│ ─────────────────────────────── │
│ "Uma classe misteriosa que       │
│  manipula arcanos proibidos..."  │
│                                 │
│ Desbloqueio: Complete Floor 3   │
│ ─────────────────────────────── │
│ [BLOQUEADO]                     │
└─────────────────────────────────┘
```

---

## Posicionamento Inicial

Apos selecionar 4 classes, o jogador define posicao:

```
FRONT LINE          BACK LINE
┌──────┐ ┌──────┐  ┌──────┐ ┌──────┐
│FIGHTER│ │PALDIN│  │ MAGE │ │CLERIC│
│  HP█  │ │  HP█  │  │  HP█  │ │  HP█  │
└──────┘ └──────┘  └──────┘ └──────┘
```

- Max 2 FRONT + 2 BACK (ou 3+1, ou 1+3)
- Cada classe tem posicao **sugerida** (baseada nos stats), mas jogador escolhe
- Posicao afeta targeting e certas habilidades

### Posicoes Sugeridas por Classe

| Classe | Posicao Sugerida | Razao |
|--------|-----------------|-------|
| Fighter | FRONT | Alto HP, alta DEF |
| Mage | BACK | Baixo HP, ataque a distancia |
| Cleric | BACK | Heal range, HP medio |
| Rogue | BACK | Evasao, ataque furtivo |
| Ranger | BACK | Ataque a distancia |
| Paladin | FRONT | Tank + heal |
| Barbarian | FRONT | HP mais alto do jogo |
| Bard | BACK | Suporte, buffar |
| Monk | FRONT | Evasao alta, corpo a corpo |
| Druid | BACK | Magico, suporte |
| Sorcerer | BACK | Glass cannon magico |
| Warlock | BACK | Magico, medio range |
| Artificer | BACK | Suporte, constructs |

---

## Implementacao

```python
# src/dungeon/run/party_selection.py
class PartySelection:
    """Gerencia o fluxo de selecao de party pre-run."""

    def __init__(self, unlocked_classes: set[str]):
        self.unlocked_classes = unlocked_classes
        self.selected: list[str] = []   # Max 4

    def select_class(self, class_id: str) -> bool:
        """Adiciona classe a party. Retorna False se invalido."""
        if class_id in self.selected:
            return False  # Sem duplicata
        if class_id not in self.unlocked_classes:
            return False  # Bloqueada
        if len(self.selected) >= 4:
            return False  # Party cheia
        self.selected.append(class_id)
        return True

    def remove_class(self, class_id: str) -> bool:
        """Remove classe da party."""
        ...

    def is_valid_party(self) -> bool:
        """Valida: 4 membros, min 1 frontliner."""
        ...

    def get_class_info(self, class_id: str) -> ClassInfo:
        """Retorna dados da classe pra exibicao."""
        ...

    def get_synergies(self) -> list[SynergyInfo]:
        """Retorna sinergias entre classes selecionadas."""
        ...
```
