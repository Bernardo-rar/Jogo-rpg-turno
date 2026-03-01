"""OnHitConfig - configuracao data-driven de on-hit por elemento."""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from src.core._paths import resolve_data_path
from src.core.elements.element_type import ElementType

ON_HIT_DATA_PATH = "data/elements/on_hit_defaults.json"


@dataclass(frozen=True)
class EffectSpec:
    """Especificacao de um efeito a ser criado (tipo + parametros)."""

    effect_type: str
    params: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class OnHitConfig:
    """Configuracao de on-hit de um elemento, carregada do JSON.

    target_effects: specs de efeitos para aplicar no alvo.
    self_effects: specs de efeitos para aplicar no atacante.
    party_healing_percent: % do dano causado convertido em cura party.
    bonus_damage_percent: % do dano causado adicionado como bonus.
    breaks_shield: True se quebra escudo.
    description: template de descricao para logs.
    """

    target_effects: tuple[EffectSpec, ...] = ()
    self_effects: tuple[EffectSpec, ...] = ()
    party_healing_percent: float = 0.0
    bonus_damage_percent: float = 0.0
    breaks_shield: bool = False
    description: str = ""


def load_on_hit_configs(
    filepath: str = ON_HIT_DATA_PATH,
) -> dict[ElementType, OnHitConfig]:
    """Carrega configuracoes de on-hit do JSON."""
    with open(resolve_data_path(filepath), encoding="utf-8") as f:
        data = json.load(f)
    return {
        ElementType[name]: _parse_config(raw)
        for name, raw in data.items()
    }


def _parse_config(raw: dict[str, object]) -> OnHitConfig:
    """Converte dict do JSON para OnHitConfig."""
    target_effects = tuple(
        _parse_effect_spec(spec)
        for spec in raw.get("target_effects", [])
    )
    self_effects = tuple(
        _parse_effect_spec(spec)
        for spec in raw.get("self_effects", [])
    )
    return OnHitConfig(
        target_effects=target_effects,
        self_effects=self_effects,
        party_healing_percent=raw.get("party_healing_percent", 0.0),
        bonus_damage_percent=raw.get("bonus_damage_percent", 0.0),
        breaks_shield=raw.get("breaks_shield", False),
        description=raw.get("description", ""),
    )


def _parse_effect_spec(spec: dict[str, object]) -> EffectSpec:
    """Converte dict do JSON para EffectSpec."""
    return EffectSpec(
        effect_type=spec["type"],
        params=spec.get("params", {}),
    )
