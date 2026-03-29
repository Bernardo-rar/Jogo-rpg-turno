"""SynergyConfig — data models for enemy synergy definitions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto


class SynergyType(Enum):
    """Types of synergy between enemies."""

    PAIR = auto()
    GROUP = auto()
    COMMANDER = auto()
    COMBO = auto()


@dataclass(frozen=True)
class DeathEffect:
    """Buff/debuff triggered when a synergy partner dies."""

    stat: str
    percent: float
    duration: int

    @classmethod
    def from_dict(cls, data: dict) -> DeathEffect:
        return cls(
            stat=str(data["stat"]),
            percent=float(data["percent"]),
            duration=int(data["duration"]),
        )


@dataclass(frozen=True)
class SynergyRole:
    """One role within a PAIR synergy."""

    role_key: str
    on_partner_death_buffs: tuple[DeathEffect, ...] = ()

    @classmethod
    def from_dict(cls, key: str, data: dict) -> SynergyRole:
        buffs: list[DeathEffect] = []
        for field_name in ("on_partner_death_buff", "on_partner_death_debuff"):
            raw = data.get(field_name)
            if raw is not None:
                buffs.append(DeathEffect.from_dict(raw))
        return cls(
            role_key=key,
            on_partner_death_buffs=tuple(buffs),
        )


@dataclass(frozen=True)
class LastSurvivorConfig:
    """Buff for the last remaining group member."""

    atk_bonus_pct: float
    speed_bonus_pct: float
    duration: int

    @classmethod
    def from_dict(cls, data: dict) -> LastSurvivorConfig:
        return cls(
            atk_bonus_pct=float(data["atk_bonus_pct"]),
            speed_bonus_pct=float(data["speed_bonus_pct"]),
            duration=int(data["duration"]),
        )


@dataclass(frozen=True)
class CommanderAuraConfig:
    """Aura buffs while commander is alive."""

    atk_bonus_pct: float
    def_bonus_pct: float

    @classmethod
    def from_dict(cls, data: dict) -> CommanderAuraConfig:
        return cls(
            atk_bonus_pct=float(data["atk_bonus_pct"]),
            def_bonus_pct=float(data["def_bonus_pct"]),
        )


@dataclass(frozen=True)
class SynergyConfig:
    """Definition of a synergy from JSON."""

    synergy_id: str
    synergy_type: SynergyType
    roles: tuple[SynergyRole, ...] = ()
    pack_same_target_bonus_pct: float = 0.0
    last_survivor: LastSurvivorConfig | None = None
    commander_aura: CommanderAuraConfig | None = None
    commander_death_debuff: DeathEffect | None = None
    combo_damage_bonus_pct: float = 0.0

    @classmethod
    def from_dict(cls, data: dict) -> SynergyConfig:
        stype = SynergyType[data["type"].upper()]
        roles = tuple(
            SynergyRole.from_dict(k, v)
            for k, v in data.get("roles", {}).items()
        )
        ls_raw = data.get("last_survivor")
        last_surv = (
            LastSurvivorConfig.from_dict(ls_raw) if ls_raw else None
        )
        aura_raw = data.get("aura_buffs")
        aura = (
            CommanderAuraConfig.from_dict(aura_raw) if aura_raw else None
        )
        death_raw = data.get("on_commander_death")
        death_debuff = (
            DeathEffect.from_dict(death_raw) if death_raw else None
        )
        return cls(
            synergy_id=str(data["synergy_id"]),
            synergy_type=stype,
            roles=roles,
            pack_same_target_bonus_pct=float(
                data.get("same_target_bonus_pct", 0.0),
            ),
            last_survivor=last_surv,
            commander_aura=aura,
            commander_death_debuff=death_debuff,
            combo_damage_bonus_pct=float(
                data.get("combo_damage_bonus_pct", 0.0),
            ),
        )


@dataclass(frozen=True)
class SynergyBinding:
    """Links a combatant to a synergy + role at combat start."""

    combatant_name: str
    synergy_id: str
    role_key: str = ""
