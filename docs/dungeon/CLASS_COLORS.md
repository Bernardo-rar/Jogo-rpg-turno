# Class Colors — Referencia Visual

## Conceito

Cada classe tem uma **cor tematica** usada na UI: borda do card, texto do nome, indicador de classe na party selection, barras de recurso, etc. Cores definidas de forma modular em `data/ui/class_colors.json` — facil de mudar sem tocar em codigo.

---

## Paleta de Cores por Classe

| Classe | Cor | Hex | RGB | Tema |
|--------|-----|-----|-----|------|
| **Fighter** | Vermelho | `#C0392B` | (192, 57, 43) | Sangue, furia, combate corpo a corpo |
| **Mage** | Azul Royal | `#2980B9` | (41, 128, 185) | Arcano, conhecimento, magia pura |
| **Cleric** | Dourado | `#F1C40F` | (241, 196, 15) | Divino, luz, protecao sagrada |
| **Rogue** | Verde Esmeralda | `#27AE60` | (39, 174, 96) | Furtividade, veneno, sombras |
| **Ranger** | Verde Floresta | `#1E8449` | (30, 132, 73) | Natureza, caca, sobrevivencia |
| **Paladin** | Prata/Branco | `#BDC3C7` | (189, 195, 199) | Honra, armadura sagrada, justica |
| **Barbarian** | Vermelho Escuro | `#922B21` | (146, 43, 33) | Furia, sangue, selvageria |
| **Bard** | Roxo | `#8E44AD` | (142, 68, 173) | Performance, encantamento, carisma |
| **Monk** | Laranja | `#E67E22` | (230, 126, 34) | Energia espiritual, disciplina, ki |
| **Druid** | Verde Musgo | `#6D8B22` | (109, 139, 34) | Terra, floresta, metamorfose |
| **Sorcerer** | Ciano | `#1ABC9C` | (26, 188, 156) | Magia inata, caos controlado |
| **Warlock** | Roxo Escuro | `#6C3483` | (108, 52, 131) | Pactos sombrios, poder proibido |
| **Artificer** | Bronze | `#BA7D2E` | (186, 125, 46) | Metal, invencao, mecanismos |

---

## Regras de Uso

### Onde usar a cor da classe

1. **Party Selection**: Borda do card da classe
2. **Combat UI**: Borda do card do personagem + nome colorido
3. **Dungeon Map**: Icone da party no mapa (cor do lider ou mistura)
4. **Class Resource Bar**: Cor da barra de recurso especial (se tiver)
5. **Buffs/Debuffs**: Icone do caster usa cor da classe
6. **Sinergias**: Linhas entre classes na party selection

### Contraste

- Todas as cores escolhidas tem contraste suficiente contra fundo escuro (`BG_DARK: #14141E`)
- Para texto sobre a cor, usar branco ou preto conforme luminancia
- Classes com cores similares (Fighter vs Barbarian, Rogue vs Ranger) tem tonalidades distintas o suficiente

### Classes com cores "proximas"

| Par | Diferenciacao |
|-----|--------------|
| Fighter (#C0392B) vs Barbarian (#922B21) | Fighter mais vivo, Barbarian mais escuro/sangue |
| Rogue (#27AE60) vs Ranger (#1E8449) | Rogue mais esmeralda, Ranger mais floresta |
| Mage (#2980B9) vs Sorcerer (#1ABC9C) | Mage azul puro, Sorcerer ciano/teal |
| Bard (#8E44AD) vs Warlock (#6C3483) | Bard roxo vibrante, Warlock roxo sombrio |

---

## Dados: `data/ui/class_colors.json`

```json
{
  "fighter":   {"hex": "#C0392B", "rgb": [192, 57, 43]},
  "mage":      {"hex": "#2980B9", "rgb": [41, 128, 185]},
  "cleric":    {"hex": "#F1C40F", "rgb": [241, 196, 15]},
  "rogue":     {"hex": "#27AE60", "rgb": [39, 174, 96]},
  "ranger":    {"hex": "#1E8449", "rgb": [30, 132, 73]},
  "paladin":   {"hex": "#BDC3C7", "rgb": [189, 195, 199]},
  "barbarian": {"hex": "#922B21", "rgb": [146, 43, 33]},
  "bard":      {"hex": "#8E44AD", "rgb": [142, 68, 173]},
  "monk":      {"hex": "#E67E22", "rgb": [230, 126, 34]},
  "druid":     {"hex": "#6D8B22", "rgb": [109, 139, 34]},
  "sorcerer":  {"hex": "#1ABC9C", "rgb": [26, 188, 156]},
  "warlock":   {"hex": "#6C3483", "rgb": [108, 52, 131]},
  "artificer": {"hex": "#BA7D2E", "rgb": [186, 125, 46]}
}
```

### Carregar no codigo

```python
# src/ui/class_colors.py
import json
from pathlib import Path

CLASS_COLORS_PATH = Path("data/ui/class_colors.json")

def load_class_colors() -> dict[str, tuple[int, int, int]]:
    """Carrega cores das classes do JSON. Modular: mude o JSON, mude as cores."""
    with open(CLASS_COLORS_PATH) as f:
        data = json.load(f)
    return {class_id: tuple(info["rgb"]) for class_id, info in data.items()}

# Uso:
# colors = load_class_colors()
# fighter_color = colors["fighter"]  # (192, 57, 43)
```

---

## Customizacao Futura

- Jogador pode desbloquear **skins de cor** pra cada classe (meta-progressao)
- Modo daltonico: paleta alternativa com shapes/patterns alem de cores
- Temas: "Dark", "Light", "Retro" — cada um com paleta propria
