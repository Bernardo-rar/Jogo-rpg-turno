"""ChargedAttack — config e effect para ataques carregados de boss."""

from __future__ import annotations

from dataclasses import dataclass

from src.core.effects.effect import Effect
from src.core.effects.effect_category import EffectCategory
from src.core.effects.tick_result import TickResult

CHARGE_DURATION = 1


@dataclass(frozen=True)
class ChargedAttackConfig:
    """Config de um ataque carregado do boss."""

    attack_id: str
    name: str
    charge_message: str
    release_message: str
    damage_mult: float
    target_type: str = "ALL_ENEMIES"
    element: str | None = None
    aoe_falloff: float = 1.0

    @classmethod
    def from_dict(cls, data: dict) -> ChargedAttackConfig:
        return cls(
            attack_id=str(data["attack_id"]),
            name=str(data["name"]),
            charge_message=str(data["charge_message"]),
            release_message=str(data["release_message"]),
            damage_mult=float(data["damage_mult"]),
            target_type=str(data.get("target_type", "ALL_ENEMIES")),
            element=data.get("element"),
            aoe_falloff=float(data.get("aoe_falloff", 1.0)),
        )


class ChargeStateEffect(Effect):
    """Applied to boss during charge turn. Causes skip_turn for 1 turn.

    On the NEXT turn, the boss handler detects this expired effect
    and fires the charged attack instead of normal AI.
    """

    def __init__(self, config: ChargedAttackConfig) -> None:
        super().__init__(CHARGE_DURATION)
        self._config = config

    @property
    def config(self) -> ChargedAttackConfig:
        return self._config

    @property
    def name(self) -> str:
        return f"Charging: {self._config.name}"

    @property
    def stacking_key(self) -> str:
        return "boss_charge"

    @property
    def category(self) -> EffectCategory:
        return EffectCategory.DEBUFF

    def _do_tick(self) -> TickResult:
        return TickResult(
            skip_turn=True,
            message=self._config.charge_message,
        )
