"""BossMechanicConfig — aggregated config for all boss mechanics."""

from __future__ import annotations

from dataclasses import dataclass, field

from src.core.combat.boss.boss_field_effect import BossFieldConfig
from src.core.combat.boss.boss_transformation import TransformationConfig
from src.core.combat.boss.charged_attack import ChargedAttackConfig
from src.core.combat.boss.empower_bar import EmpowerBarConfig


@dataclass(frozen=True)
class SummonConfig:
    """Config for a boss minion summon."""

    minion_template_id: str
    count: int = 1
    hp_scale: float = 0.20
    atk_scale: float = 0.40
    enrage_atk_pct: float = 15.0

    @classmethod
    def from_dict(cls, data: dict) -> SummonConfig:
        return cls(
            minion_template_id=str(data["minion_template_id"]),
            count=int(data.get("count", 1)),
            hp_scale=float(data.get("hp_scale", 0.20)),
            atk_scale=float(data.get("atk_scale", 0.40)),
            enrage_atk_pct=float(data.get("enrage_atk_pct", 15.0)),
        )


@dataclass(frozen=True)
class BossMechanicConfig:
    """All optional boss mechanics for a single boss."""

    charged_attacks: tuple[ChargedAttackConfig, ...] = ()
    charge_every_n_rounds: int = 4
    summons: tuple[SummonConfig, ...] = ()
    max_minions_alive: int = 2
    summon_cooldown_rounds: int = 5
    empower_bar: EmpowerBarConfig | None = None
    field_effects: tuple[BossFieldConfig, ...] = ()
    transformation: TransformationConfig | None = None

    @classmethod
    def from_dict(cls, data: dict) -> BossMechanicConfig:
        return cls(
            charged_attacks=_parse_charged(data),
            charge_every_n_rounds=int(data.get("charge_every_n_rounds", 4)),
            summons=_parse_summons(data),
            max_minions_alive=int(data.get("max_minions_alive", 2)),
            summon_cooldown_rounds=int(data.get("summon_cooldown_rounds", 5)),
            empower_bar=_parse_empower_opt(data.get("empower_bar")),
            field_effects=_parse_fields(data),
            transformation=_parse_transform_opt(data.get("transformation")),
        )


def _parse_charged(data: dict) -> tuple[ChargedAttackConfig, ...]:
    return tuple(
        ChargedAttackConfig.from_dict(c)
        for c in data.get("charged_attacks", [])
    )


def _parse_summons(data: dict) -> tuple[SummonConfig, ...]:
    return tuple(
        SummonConfig.from_dict(s) for s in data.get("summons", [])
    )


def _parse_fields(data: dict) -> tuple[BossFieldConfig, ...]:
    return tuple(
        BossFieldConfig.from_dict(f)
        for f in data.get("field_effects", [])
    )


def _parse_empower_opt(raw: dict | None) -> EmpowerBarConfig | None:
    return _parse_empower(raw) if raw else None


def _parse_transform_opt(
    raw: dict | None,
) -> TransformationConfig | None:
    return TransformationConfig.from_dict(raw) if raw else None


def _parse_empower(data: dict) -> EmpowerBarConfig:
    return EmpowerBarConfig(
        max_value=int(data.get("max_value", 100)),
        gain_per_round=int(data.get("gain_per_round", 20)),
        loss_on_weakness_hit=int(data.get("loss_on_weakness_hit", 40)),
        empowered_atk_mult=float(
            data.get("empowered_atk_mult", 1.50),
        ),
        empowered_def_mult=float(
            data.get("empowered_def_mult", 1.20),
        ),
        empowered_duration=int(data.get("empowered_duration", 3)),
    )
