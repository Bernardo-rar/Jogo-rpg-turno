"""StatBonus frozen dataclass para bonus de equipamento."""

from __future__ import annotations

from dataclasses import dataclass

from src.core.effects.modifiable_stat import ModifiableStat

_DEFAULT_FLAT = 0
_DEFAULT_PERCENT = 0.0


@dataclass(frozen=True)
class StatBonus:
    """Bonus de stat de um acessorio (flat e/ou percentual)."""

    stat: ModifiableStat
    flat: int = _DEFAULT_FLAT
    percent: float = _DEFAULT_PERCENT

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> StatBonus:
        """Cria StatBonus a partir de dict (JSON)."""
        return cls(
            stat=ModifiableStat[str(data["stat"])],
            flat=int(data.get("flat", _DEFAULT_FLAT)),  # type: ignore[arg-type]
            percent=float(data.get("percent", _DEFAULT_PERCENT)),  # type: ignore[arg-type]
        )
