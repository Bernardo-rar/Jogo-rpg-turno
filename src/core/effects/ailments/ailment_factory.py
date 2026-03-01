"""Factory functions para criacao ergonomica de ailments."""

from __future__ import annotations

from src.core.effects.ailments.amnesia import Amnesia
from src.core.effects.ailments.bleed import Bleed
from src.core.effects.ailments.burn import Burn
from src.core.effects.ailments.confusion import Confusion
from src.core.effects.ailments.cold import Cold
from src.core.effects.ailments.curse import Curse
from src.core.effects.ailments.freeze import Freeze
from src.core.effects.ailments.injury import Injury
from src.core.effects.ailments.paralysis import Paralysis
from src.core.effects.ailments.poison import Poison
from src.core.effects.ailments.scorch import Scorch
from src.core.effects.ailments.sickness import Sickness
from src.core.effects.ailments.virus import Virus
from src.core.effects.ailments.weakness import Weakness


def create_poison(damage_per_tick: int, duration: int) -> Poison:
    """Cria Poison DoT."""
    return Poison(damage_per_tick=damage_per_tick, duration=duration)


def create_virus(damage_per_tick: int, duration: int) -> Virus:
    """Cria Virus DoT (Poison potencializado)."""
    return Virus(damage_per_tick=damage_per_tick, duration=duration)


def create_bleed(damage_per_tick: int, duration: int) -> Bleed:
    """Cria Bleed DoT."""
    return Bleed(damage_per_tick=damage_per_tick, duration=duration)


def create_burn(damage_per_tick: int, duration: int) -> Burn:
    """Cria Burn DoT com reducao de cura default."""
    return Burn(damage_per_tick=damage_per_tick, duration=duration)


def create_scorch(damage_per_tick: int, duration: int) -> Scorch:
    """Cria Scorch DoT com reducao de MAX_HP default."""
    return Scorch(damage_per_tick=damage_per_tick, duration=duration)


def create_freeze(duration: int) -> Freeze:
    """Cria Freeze CC (impede acao + reduz cura)."""
    return Freeze(duration=duration)


def create_paralysis(duration: int) -> Paralysis:
    """Cria Paralysis CC (chance de perder acao)."""
    return Paralysis(duration=duration)


def create_cold(duration: int, reduction_percent: float) -> Cold:
    """Cria Cold debuff (reduz speed)."""
    return Cold(duration=duration, speed_reduction_percent=reduction_percent)


def create_weakness(duration: int, reduction_percent: float) -> Weakness:
    """Cria Weakness debuff (reduz defesa phys + mag)."""
    return Weakness(
        duration=duration, defense_reduction_percent=reduction_percent,
    )


def create_injury(duration: int, reduction_percent: float) -> Injury:
    """Cria Injury debuff (reduz ataque phys + mag)."""
    return Injury(
        duration=duration, attack_reduction_percent=reduction_percent,
    )


def create_sickness(duration: int, reduction_percent: float) -> Sickness:
    """Cria Sickness debuff (reduz cura recebida)."""
    return Sickness(
        duration=duration, recovery_reduction_percent=reduction_percent,
    )


def create_amnesia(duration: int) -> Amnesia:
    """Cria Amnesia (bloqueia skills de mana)."""
    return Amnesia(duration=duration)


def create_confusion(duration: int) -> Confusion:
    """Cria Confusion CC (redireciona ataques para alvos aleatorios)."""
    return Confusion(duration=duration)


def create_curse(duration: int) -> Curse:
    """Cria Curse (bloqueia skills de aura)."""
    return Curse(duration=duration)
