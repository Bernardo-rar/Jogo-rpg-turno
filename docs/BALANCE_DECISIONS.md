# Decisoes de Balanceamento

Registro das decisoes de design relacionadas a numeros, formulas e balanceamento.

## Mana

### Base Multiplier = 5 (era 10)
- **Formula**: `mana = mana_multiplier * MIND * 5`
- **Motivo**: Multiplicador 10 gerava pools absurdos (1000+ mana). Com 5, os valores ficam razoaveis (90~590 lvl1).
- **Custos de skill ajustados**: Divididos por 2 proporcionalmente.
- **Exemplos lvl1**: Fighter 90, Ranger 175, Cleric 360, Sorcerer 540.

### Consumiveis fisicos nao custam mana
- Potions (health, mana) e antidotes: `mana_cost = 0`
- Itens magicos (molotov, turtle shell, smoke bomb): custam mana
- **Motivo**: Beber uma pocao nao requer poder magico.

## Cura

### Skill heal escala com magical_attack do caster
- **Formula**: `heal_power = base_power + magical_attack`
- **Motivo**: Dano escala com stats (attack vs defense), cura precisa escalar tambem. Magical attack inteiro garante que heals acompanhem o dano recebido.
- **Exemplo**: Minor Heal (base 20) por Aurelia (magical_attack 136) = 20 + 136 = 156 HP bruto.
- **Nota**: Consumable heals (potions) continuam flat — nao escalam com stats do usuario.

### Cura recebida escala com CON do alvo
- **Formula**: `heal_received = heal_amount * (1 + CON * 0.05)`
- **Constante**: `CON_HEAL_BONUS_PER_POINT = 0.05` (5% por ponto de CON)
- **Motivo**: Personagens com alta constituicao (tanques) se beneficiam mais de cura, refletindo resiliencia fisica.
- **Exemplos**:
  - CON 5: +25% cura recebida
  - CON 7 (Gareth): +35% cura recebida
  - CON 10: +50% cura recebida
  - CON 20: +100% cura recebida
  - CON 30: +150% cura recebida
- **Interacao**: Aplica ANTES de effect modifiers (buffs/debuffs de HEALING_RECEIVED).

### Consumable heals sao flat
- Potions curam um valor fixo (base_power) que recebe apenas o bonus de CON do alvo.
- NAO escalam com stats do usuario.
- **Motivo**: Potions sao itens genericos, qualquer personagem pode usar com mesmo efeito base.

## AI de Consumiveis/Skills

### Skip de heals desnecessarios
- **SkillHandler**: Pula skills puramente de heal se todos os aliados estao com HP cheio.
- **ConsumableHandler**: Pula potions de cura se HP cheio, pula cleanse se sem efeitos negativos.
- **Motivo**: Evita desperdicio de recursos (ex: Aurelia curando 0 HP no round 1).

### Target resolver para heals
- `SINGLE_ALLY` seleciona o aliado mais machucado (menor ratio HP/MaxHP).
- **Motivo**: Curar quem mais precisa e mais eficiente que curar o primeiro da lista.

## Poison/DoTs

- Poison: 10 dano/tick, duracao 3 turnos = 30 total
- Valores configurados no JSON de skills, nao hardcoded.

### TODO: Scaling de DoTs (futuro)
- Atualmente DoTs (poison, burn, bleed) fazem dano flat por tick sem escalar com nenhum stat.
- Ideia: poison poderia escalar com % do HP maximo do alvo (ex: 2-3% do max_hp por tick). Isso tornaria poison mais relevante contra tanques e manteria proporcionalidade em niveis altos.
- Alternativas: escalar com magical_attack do caster, ou com o nivel do caster.
- Decisao adiada ate ter mais dados de balanceamento em combates de nivel alto.
