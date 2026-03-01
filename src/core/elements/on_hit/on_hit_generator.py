"""OnHitGenerator - gera OnHitResult a partir de OnHitConfig."""

from __future__ import annotations

from typing import Callable

from src.core.effects.ailments.ailment_factory import (
    create_burn,
    create_cold,
    create_confusion,
    create_injury,
    create_paralysis,
    create_sickness,
)
from src.core.effects.buff_factory import (
    create_flat_buff,
    create_flat_debuff,
    create_percent_buff,
    create_percent_debuff,
)
from src.core.effects.effect import Effect
from src.core.effects.modifiable_stat import ModifiableStat
from src.core.elements.on_hit.on_hit_config import EffectSpec, OnHitConfig
from src.core.elements.on_hit.on_hit_result import OnHitResult


def generate_on_hit(
    config: OnHitConfig,
    damage_dealt: int,
) -> OnHitResult:
    """Gera OnHitResult a partir de config e dano causado."""
    effects = _build_effects(config.target_effects)
    self_effects = _build_effects(config.self_effects)
    party_healing = int(damage_dealt * config.party_healing_percent)
    bonus_damage = int(damage_dealt * config.bonus_damage_percent)
    return OnHitResult(
        effects=tuple(effects),
        self_effects=tuple(self_effects),
        bonus_damage=bonus_damage,
        party_healing=party_healing,
        breaks_shield=config.breaks_shield,
        description=config.description,
    )


def _build_effects(specs: tuple[EffectSpec, ...]) -> list[Effect]:
    """Cria lista de Effects a partir de specs."""
    return [_create_effect(spec) for spec in specs]


def _create_effect(spec: EffectSpec) -> Effect:
    """Cria um Effect a partir de um EffectSpec usando dispatch table."""
    factory = _EFFECT_FACTORIES.get(spec.effect_type)
    if factory is None:
        msg = f"Unknown effect type: {spec.effect_type}"
        raise ValueError(msg)
    return factory(spec.params)


def _create_ailment_burn(params: dict[str, object]) -> Effect:
    return create_burn(**params)


def _create_ailment_cold(params: dict[str, object]) -> Effect:
    return create_cold(**params)


def _create_ailment_paralysis(params: dict[str, object]) -> Effect:
    return create_paralysis(**params)


def _create_ailment_sickness(params: dict[str, object]) -> Effect:
    return create_sickness(**params)


def _create_ailment_confusion(params: dict[str, object]) -> Effect:
    return create_confusion(**params)


def _create_ailment_injury(params: dict[str, object]) -> Effect:
    return create_injury(**params)


def _create_flat_buff(params: dict[str, object]) -> Effect:
    stat = ModifiableStat[params["stat"]]
    return create_flat_buff(stat, params["flat"], params["duration"])


def _create_percent_buff(params: dict[str, object]) -> Effect:
    stat = ModifiableStat[params["stat"]]
    return create_percent_buff(stat, params["percent"], params["duration"])


def _create_flat_debuff(params: dict[str, object]) -> Effect:
    stat = ModifiableStat[params["stat"]]
    return create_flat_debuff(stat, params["flat"], params["duration"])


def _create_percent_debuff(params: dict[str, object]) -> Effect:
    stat = ModifiableStat[params["stat"]]
    return create_percent_debuff(
        stat, params["percent"], params["duration"],
    )


_EFFECT_FACTORIES: dict[str, Callable[[dict[str, object]], Effect]] = {
    "burn": _create_ailment_burn,
    "cold": _create_ailment_cold,
    "paralysis": _create_ailment_paralysis,
    "sickness": _create_ailment_sickness,
    "confusion": _create_ailment_confusion,
    "injury": _create_ailment_injury,
    "flat_buff": _create_flat_buff,
    "percent_buff": _create_percent_buff,
    "flat_debuff": _create_flat_debuff,
    "percent_debuff": _create_percent_debuff,
}
