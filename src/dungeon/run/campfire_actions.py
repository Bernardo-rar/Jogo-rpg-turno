"""Campfire actions — acoes disponiveis em salas de fogueira."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import TYPE_CHECKING

from src.core._paths import resolve_data_path

if TYPE_CHECKING:
    from src.core.characters.character import Character
    from src.dungeon.run.run_state import RunState

_CAMPFIRE_FILE = "data/dungeon/campfire/campfire_buffs.json"


@dataclass(frozen=True)
class CampfireBuff:
    """Dados de um buff de fogueira."""

    buff_id: str
    name: str
    description: str
    heal_pct: float
    buff_stat: str
    buff_value: int
    duration_rooms: int


def load_campfire_buffs() -> dict[str, CampfireBuff]:
    """Carrega buffs de fogueira do JSON."""
    path = resolve_data_path(_CAMPFIRE_FILE)
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {
        key: _parse_buff(key, data)
        for key, data in raw.items()
    }


def _parse_buff(buff_id: str, raw: dict) -> CampfireBuff:
    """Converte dict JSON em CampfireBuff."""
    return CampfireBuff(
        buff_id=buff_id,
        name=raw["name"],
        description=raw["description"],
        heal_pct=raw["heal_pct"],
        buff_stat=raw["buff_stat"],
        buff_value=raw["buff_value"],
        duration_rooms=raw["duration_rooms"],
    )


def apply_campfire_buff(
    run_state: RunState,
    buff: CampfireBuff,
) -> dict[str, object]:
    """Aplica buff de fogueira: heal ou stat boost."""
    if buff.heal_pct > 0:
        return _apply_heal(run_state, buff)
    return _apply_stat_buff(buff)


def _apply_heal(
    run_state: RunState,
    buff: CampfireBuff,
) -> dict[str, object]:
    """Cura percentual do HP de membros vivos."""
    total = 0
    for c in run_state.party:
        if c.is_alive:
            amount = int(c.max_hp * buff.heal_pct)
            total += c.heal(amount)
    return {"healed": total, "buff_name": buff.name}


def _apply_stat_buff(buff: CampfireBuff) -> dict[str, object]:
    """Retorna dados do buff para aplicacao futura."""
    return {
        "buff_stat": buff.buff_stat,
        "buff_value": buff.buff_value,
        "duration_rooms": buff.duration_rooms,
        "buff_name": buff.name,
    }
