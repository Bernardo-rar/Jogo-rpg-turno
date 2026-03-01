"""OnHitResult - descreve os efeitos que um ataque elemental produz."""

from __future__ import annotations

from dataclasses import dataclass

from src.core.effects.effect import Effect


@dataclass(frozen=True)
class OnHitResult:
    """Resultado imutavel descrevendo efeitos on-hit de um ataque elemental.

    effects: efeitos para aplicar no ALVO.
    self_effects: efeitos para aplicar no ATACANTE.
    bonus_damage: dano extra a adicionar (Force).
    party_healing: cura para dividir entre membros da party (Holy/Celestial).
    breaks_shield: True se o ataque quebra/ignora escudo (Force).
    description: texto descritivo do efeito para logs.
    """

    effects: tuple[Effect, ...] = ()
    self_effects: tuple[Effect, ...] = ()
    bonus_damage: int = 0
    party_healing: int = 0
    breaks_shield: bool = False
    description: str = ""
