# Requisitos Funcionais - RPG Turno

## RF01 - Sistema de Atributos

### RF01.1 - Atributos Primarios
O sistema deve suportar 7 atributos primarios para cada personagem:
- **STR (Forca)**: Mod ataque fisico, mod defesa fisica, HP
- **DEX (Destreza)**: Mod defesa fisica, mod dano, chance de critico, speed, esquiva
- **CON (Constituicao)**: HP, regen HP, resistencia a debuff, stamina, mod defesa fisica e magica
- **INT (Inteligencia)**: Dano magico, num de habs na barra de skills
- **WIS (Sabedoria)**: Defesa magica, num efeitos em skill, cura
- **CHA (Carisma)**: Dano magico, num itens magicos equipaveis, mind
- **MIND (Mente)**: Mana total, mana usavel por turno, critico magico

### RF01.2 - Scaling de Atributos e Thresholds de Bonus

Cada ponto de atributo contribui incrementalmente para os stats derivados (ex: cada +1 STR aumenta ataque fisico e defesa).
Alem disso, ao atingir **marcos especificos**, o personagem recebe bonus EXTRAS adicionais:

- **Tier 1** (18, 22, 26): Bonus moderados por marco atingido
  - STR: +2 mod ataque fisico, +1 mod defesa fisica, +2 mod HP
  - DEX: +2 mod ataque fisico, +1 mod defesa fisica, +10% chance critica
  - CON: +2 mod HP, +1 mod defesa fisica, +1 mod defesa magica, +1 regen HP, +1 stamina
  - INT: +2 mod mana, +1 mod defesa magica, +2 mod ataque magico
  - WIS: +1 num efeitos em skill, +2 mod defesa magica, +2 mod cura
  - CHA: +1 mind, +1 slot itens magicos, +2 mod ataque magico
- **Tier 2** (30, 32): Bonus fortes por marco atingido (hiperespecializacao)
  - STR: +4 mod ataque fisico, +2 mod defesa fisica, +4 mod HP
  - DEX: +4 mod ataque fisico, +2 mod defesa fisica, +20% chance critica
  - CON: +4 mod HP, +2 mod defesa fisica, +2 mod defesa magica, +2 regen HP, +2 stamina
  - INT: +4 mod mana, +2 mod defesa magica, +4 mod ataque magico
  - WIS: +1 num efeitos em skill, +4 mod defesa magica, +4 mod cura
  - CHA: +2 mind, +1 slot itens magicos, +4 mod ataque magico

Os bonus sao **cumulativos**: um personagem com STR 26 recebeu bonus nos marcos 18, 22 E 26.

### RF01.3 - Atributos Derivados
Calculados a partir dos primarios:
- **HP**: `((hit_dice + CON + mod_hp_flat) * 2) * mod_hp_mult` (lvl 1, dobrado como Tormenta)
- **Mana**: `dado_mana * MIND * 10`
- **Stamina**: Baseada em CON + STR (para classes marciais)
- **CA (Armor Class)**: `CA_armadura + DEX + nivel`
- **Speed**: Determina ordem de turnos
- **Guard**: Chance de reduzir dano apos ser acertado
- **Esquiva**: Chance de desviar mesmo apos ataque passar CA

### RF01.4 - Regeneracao
- **HP Regen**: `CON * nivel * constante_balanceamento` por turno
- **Mana Regen**: `MIND * nivel * constante_balanceamento` por turno

---

## RF02 - Sistema de Personagens

### RF02.1 - Personagens Pre-definidos
Personagens sao pre-definidos (nao criados do zero), com personalidade e lore:
- Devem quebrar estereotipos (ex: guerreira velha humana, goblin mago, elfo barbaro)
- Cada um com stats base fixos e classe pre-determinada
- Podem comecar em niveis diferentes (guerreiro comeca mais alto)

### RF02.2 - Party
- Party fixa de **4 personagens** em combate
- Cada personagem ocupa posicao **Front** ou **Back** line

### RF02.3 - Classes Base (13)
Cada classe deve ter:
- Stats base diferentes (hit dice, mods de ataque/defesa)
- Mecanica unica que a diferencia das outras
- 2-6 subclasses desbloqueadas no nivel 3
- Passivas de classe
- Skills de classe

| # | Classe | Hit Dice | Papel Principal | Mecanica Unica |
|---|--------|----------|-----------------|----------------|
| 1 | Fighter (Guerreiro) | d12 | Tank/DPS adaptavel | Pontos de Acao, Estancias, Overdrive |
| 2 | Barbarian (Barbaro) | d12 | DPS brutal | Barra de Furia, dano por HP perdido |
| 3 | Paladin (Paladino) | d10 | Tank defensivo, auras | Divindade, Juramentos stack, Glimpse of Glory |
| 4 | Ranger | d10 | DPS critico continuo | Foco Predatorio (stack crit), Marca do Cacador |
| 5 | Monk (Monge) | d10 | DPS multi-hit, debuff | Barra Equilibrium (Vitalidade/Destruicao) |
| 6 | Mage (Mago) | d6 | AOE elemental, protecao | Overcharge, ataque basico gera mana, scrolls |
| 7 | Sorcerer (Feiticeiro) | d6 | DPS magico puro | Metamagia, Overcharged, Rotacao de Mana |
| 8 | Cleric (Clerigo) | d8 | Healer/Buffer | Divindade (elemento), Canalizar Divindade |
| 9 | Warlock (Bruxo) | d8 | Debuffer/DPS | Insanidade, Familiares, Sede Insaciavel |
| 10 | Druid (Druida) | d8 | Controle/Transformacao | Transformacoes, condicoes de campo |
| 11 | Rogue (Ladino) | d8 | DPS/Utilidade | Usa itens sem gastar turno, mistura itens |
| 12 | Bard (Bardo) | d8 | Buffer/Debuffer | Embalo Musical (stack), recruta NPCs |
| 13 | Artificer (Artifice) | d8 | Suporte/Mana | Traje Tecmagis, potencializa itens ativos |

---

## RF03 - Sistema de Combate

### RF03.1 - Action Economy (por turno, por personagem)
Cada personagem tem por turno:
1. **Acao Normal** (1x): Atacar, usar skill, usar item
2. **Acao Bonus** (1x): Mudar estancia, ativar aura, habilidade rapida, movimentacao
3. **Reacao** (1x, no turno inimigo): Proteger, contra-atacar, barreira, esquivar

### RF03.2 - Ordem de Turnos
- Baseada no atributo **Speed**
- Todos os personagens da party agem, depois todos os inimigos (ou intercalado por speed)

### RF03.3 - Posicionamento
- **Front Line**: Recebe ataques melee, pode proteger back line
- **Back Line**: Protegido de ataques melee diretos, vulneravel a AOE e ranged
- Movimentacao entre linhas gasta stamina (acao bonus)

### RF03.4 - Ataque Basico
- Dano: `(dado_arma + mods_atributo) * mod_ataque_classe`
- Deve ter valor durante todo o jogo (nao so early game)
- Pode gerar recursos (mana para mago, pontos de acao para guerreiro, furia para barbaro)
- Chance de critico baseada em DEX

### RF03.5 - Defesa
- **Defesa Fisica**: `(DEX + CON + STR) * mod_defesa_fisica_classe`
- **Defesa Magica**: `(CON + WIS + INT) * mod_defesa_magica_classe`
- **Reducao de dano fisico**: `CA / 4` (base, varia por classe - barbaro CA/3)
- Calculo: `dano_final = (dano_bruto * (1 - reducao_%)) - reducao_flat - escudo`

### RF03.6 - Critico
- Chance base por DEX (fisico) ou MIND (magico)
- Dano critico: multiplicador (default 2x)
- Algumas classes tem interacoes especiais ao critar (ranger: debuff, barbaro: bonus)

### RF03.7 - Dificuldade
- Definida pelo **comportamento da IA** dos monstros, nao apenas stats
- Dificuldades mais altas: inimigos usam recursos de forma mais inteligente, ataques novos
- Timer opcional em dificuldades altas
- Boss precisa de **2-3 turnos** para wipe na party (nao one-shot)

---

## RF04 - Sistema Elemental

### RF04.1 - Elementos
| Elemento | Efeito On-Hit |
|----------|---------------|
| Fogo | Queimadura (DoT, reduz regen HP) |
| Agua | Potencializa outras magias |
| Gelo | Reduz Speed, reduz defesa fisica |
| Eletrico | Paralisia, corta cura |
| Terra | Aumenta defesa |
| Holy (Sagrado) | Gera escudo, cura ao acertar hit (% dano / membros party) |
| Darkness (Trevas) | Efeitos ao contato (burn necrotico) |
| Celestial | Cura party ao dar dano |
| Psiquico | Confusao (ataque aleatorio), Fear (desvantagem) |
| Forca | Dano extra, quebra escudos/defesas |

### RF04.2 - Fraquezas e Resistencias
- Inimigos podem ter fraquezas/resistencias elementais
- Status "analisado" revela fraquezas (como Octopath)
- Protecoes elementais especificas reduzem dano daquele tipo em %

---

## RF05 - Sistema de Buffs, Debuffs e Status Ailments

### RF05.1 - Buffs
- Flat (ex: +2 CON) e percentuais (ex: +10% HP)
- Conversao de stats (ex: 20% defesa vira ataque adicional)
- Duracao em turnos
- Buffs especiais: Haste (+1 turno), Angel Idol (sobrevive a knockout com 1 HP), Moral (impede mais de 50% HP loss por turno), Bless, Brave (crit chance)

### RF05.2 - Debuffs
- Reduzir ataque, defesa, velocidade inimigos
- Fraqueza contra critico, fraqueza elemental
- Flat e percentual (em dificuldades baixas flat primeiro; em altas, % primeiro)

### RF05.3 - Status Ailments
| Ailment | Efeito |
|---------|--------|
| Scorch | Reduz HP max (acumulativo) + DoT massivo |
| Queimadura | DoT fogo + reduz healing HP em % |
| Freeze | Perde X turnos + reduz healing |
| Cold | Debuff speed |
| Poison | DoT veneno |
| Virus | Poison potencializado |
| Paralisia | Chance de perder acao |
| Fraqueza | Perde % de defesa |
| Injury | Perde % de ataque |
| Sickness | Perde % de recuperacao HP |
| Amnesia | Impede uso de habs de mana |
| Curse | Impede uso de habs de aura |
| Bleed | DoT sangramento |

---

## RF06 - Sistema de Skills/Habilidades

### RF06.1 - Spell Slots com Custo
- Cada personagem tem spell slots com custo maximo
- Jogador monta suas skills combinando efeitos ate o custo maximo do slot
- Exemplo: Clerigo com slot de custo 8 pode escolher "Cura party toda (8)" OU "Cura menor (3) + Buff def (3)" num unico slot
- Custo maximo aumenta com stats de conjurador

### RF06.2 - Progressao de Skills
- Early: Ataques basicos fortes, poucas skills, single target
- Mid: Skills de area, buffs/debuffs mais potentes
- Late: Spam de habilidades, skills devastadoras (ex: Ragnarok, Meteoro)

### RF06.3 - Cooldowns e Custos
- Skills tem custo de mana e/ou stamina
- Algumas tem cooldown em turnos
- Revive tem cooldown alto
- Auras podem ser "sempre ativas" (ex: paladino)

---

## RF07 - Sistema de Equipamento

### RF07.1 - Armas
- Tipos: Espadas, adagas, arcos, cajados, martelos, lancas, etc.
- Cada tipo com dado de dano diferente e tipos de dano (corte/perfuracao/contusao)
- Separadas em **Normais** e **Magicas**
- Magicas: 3 tiers (Incomum, Raro, Lendario/Artefato)
- Armas magicas requerem CHA para equipar
- Lendarias tem passivas e ativas (ex: Aegis, Dragonslayer, Arondight)
- Classes tem proficiencia em tipos de arma

### RF07.2 - Armaduras
- Tipos: Leve, Media, Pesada (sets completos)
- Aumentam CA, HP, Mana, Defesa Fisica/Magica
- Algumas com passivas e ativas

### RF07.3 - Acessorios/Amuletos
- Buffs diversos em stats
- Passivas e possivelmente habilidades extras
- Limitados por CHA (num max de itens magicos)

### RF07.4 - Consumiveis
- Pocoes de cura
- Itens de defesa (ex: casco de tartaruga magica)
- Itens de ataque (ex: molotov)
- Itens de cleanse (removem status ailments)
- Itens de fuga
- Custam mana para usar (os melhores custam mais)

### RF07.5 - Inventario
- Limite de slots (20 por tipo?)
- Equipar/desequipar armas, armaduras, acessorios
- Ladino pode usar itens sem gastar turno

---

## RF08 - Sistema de Progressao

### RF08.1 - Level Up (1 a 10)
- Cada nivel da:
  - Aumento de HP e Mana (baseado em hit dice + atributos)
  - Pontos de atributo para distribuir (fisicos e mentais separados)
  - Novas skills e/ou melhoria de existentes
  - Bonus de proficiencia = nivel

### RF08.2 - Marcos de Nivel
| Nivel | Evento |
|-------|--------|
| 1 | Classe base, skills iniciais, escolha estilos de combate |
| 2 | Novas habilidades, aumento de stats |
| 3 | **Escolha de subclasse**, talentos, novas skills |
| 4 | Aumento de stats maior |
| 5 | Skills poderosas (Overdrive, etc), talentos |
| 6-10 | Progressao continua, skills de alto nivel |

### RF08.3 - Subclasses
- Escolhidas no nivel 3
- Dao bonus em % para atributos primarios/secundarios
- Passivas e skills unicas
- Modificam o comportamento de skills da classe base
- Cada subclasse tem progressao propria nos niveis 3, 5, 7, 9

### RF08.4 - Talentos
- Escolhidos em niveis especificos (3, 5, etc)
- Exemplos:
  - Tough (18 STR): bonus HP
  - Maestria Elemental: reduz custo mana de magia elemental
  - Battle Continuation: auto-revive consumindo recursos

---

## RF09 - Sistema de Inimigos

### RF09.1 - Tipos de Inimigos
- Inimigos comuns: stats baseados no nivel, IA simples
- Mini-bosses: mecanicas especificas, ataques carregados
- Bosses: mecanicas complexas, fases por threshold de HP

### RF09.2 - Mecanicas de Boss
- **Ataques carregados**: 1 turno idle, proximo turno porradao (AOE ou ST)
- **Thresholds de HP**: Transformacoes, novas habilidades ao atingir % de HP
- **Empenho**: Barra que aumenta dano do boss se party nao atacar pontos fracos
- **Invocacao de minions**: Boss spawna adds que devem ser limpos rapido
- **Mecanicas baseadas em status**: Comportamento muda baseado em buffs/debuffs

### RF09.3 - Combates com Multiplos Inimigos
- Mecanicas baseadas em HP/status dos aliados inimigos
- Mecanicas baseadas na quantidade de inimigos vivos
- Sinergias entre inimigos

### RF09.4 - Bosses Secretos
- Desbloqueados por condicoes especificas
- Sistema de trials (estilo Brave Frontier)
- Dificuldade acima do normal, recompensas exclusivas

---

## RF10 - UI e Controles (futuro, mas documentado)

### RF10.1 - Fluxo de Telas
1. Tela Titulo (New Game, Load, Options, Credits, Sair)
2. Nome/Dificuldade
3. Selecao de Personagens (escolher 4)
4. Tutorial
5. Combate
6. Inventario/Equipamento/Alquimia
7. Tela de Vitoria/Derrota
8. Menu de pausa

### RF10.2 - Estilo Visual
- Estilo FF classico: PNGs sem animacoes complexas, animacoes simples para VFX
- Feedback visual de dano (numeros flutuantes)
- Feedback visual de mudanca de estancia/instancia
- Destaque visual em acoes importantes (QTE)

### RF10.3 - Controles
- **Teclado primeiro**: 1-6 seleciona personagem, 1-4 seleciona tipo de acao
- Sistema de atalhos tipo CS:GO (memorizar sequencias)
- Mouse como fallback para jogadores casuais
- QTE opcional: sequencias WASD para bonus em skills (mais potencia = QTE maior)

---

## RF11 - Balanceamento

### RF11.1 - Escala de HP
- Early (lvl 1-3): ~200-500 HP (marciais)
- Mid (lvl 4-6): ~1000-2000 HP
- Late (lvl 7-10): ~3000-5000+ HP
- Cura nao agressiva: recuperar de 75% a 90%, nao de 50% a 100%

### RF11.2 - Balanceamento de Classes (Radar de Roles)
Cada classe avaliada em 5 eixos (1-5):
- **Tank**: Capacidade de tankar dano
- **Damage**: DPS sustentado
- **Utility**: Crowd control, ferramentas pro time
- **AOE**: Alcance de area
- **Support**: Buffs, heals diretos

### RF11.3 - Composicao de Party
- **Generalista**: Nao sofre tanto com perda de membro, porem menos potente
- **Especialista**: Otimizado, muito potente, mas sofre horrores se alguem cai
- Mesclar as duas abordagens deve ser a chave pro meta
- Algumas classes tem sinergias claras; outras sao "coringas" faceis de encaixar

### RF11.4 - Scaling
- Evitar scale desigual: jogador deve poder escolher a comp que quer sem trocar membros por serem fracos early/late
- Classes dao % de buff em atributos primarios (10% lvl 1-3, 15% lvl 9-11)
- Subclasses potencializam um aspecto especifico

---

## Priorizacao para Implementacao

### Fase 1 - Core Engine (MVP)
1. Sistema de atributos (RF01)
2. Classe base Character (RF02.1, RF02.2)
3. Engine de combate basico (RF03.1 a RF03.6)
4. 3 classes: Fighter, Mage, Cleric (RF02.3 parcial)
5. Skills basicas pre-setadas (RF06 simplificado)

### Fase 2 - Profundidade
6. Sistema elemental (RF04)
7. Buffs/Debuffs/Ailments (RF05)
8. Todas as 13 classes (RF02.3 completo)
9. Sistema de equipamento basico (RF07)
10. Progressao level 1-10 (RF08)

### Fase 3 - Conteudo
11. Subclasses (RF08.3)
12. Spell slots customizaveis (RF06.1)
13. IA de inimigos e bosses (RF09)
14. Itens lendarios com passivas/ativas (RF07.1)
15. Talentos (RF08.4)

### Fase 4 - Polish
16. UI completa (RF10)
17. QTE system (RF10.3)
18. Bosses secretos/trials (RF09.4)
19. Balanceamento fino (RF11)
