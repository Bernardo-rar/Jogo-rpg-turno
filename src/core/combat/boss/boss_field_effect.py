"""BossFieldEffect — persistent battlefield condition applied by bosses."""

from __future__ import annotations

from dataclasses import dataclass

from src.core.effects.effect import Effect
from src.core.effects.effect_category import EffectCategory
from src.core.effects.tick_result import TickResult


@dataclass(frozen=True)
class BossFieldConfig:
    """Config for a boss field effect loaded from JSON."""

    field_id: str
    name: str
    element: str
    damage_pct_max_hp: float
    duration: int
    trigger_message: str
    debuff_stat: str | None = None
    debuff_percent: float = 0.0
    cleanse_element: str | None = None

    @classmethod
    def from_dict(cls, data: dict) -> BossFieldConfig:
        return cls(
            field_id=str(data["field_id"]),
            name=str(data["name"]),
            element=str(data["element"]),
            damage_pct_max_hp=float(data["damage_pct_max_hp"]),
            duration=int(data["duration"]),
            trigger_message=str(data["trigger_message"]),
            debuff_stat=data.get("debuff_stat"),
            debuff_percent=float(data.get("debuff_percent", 0.0)),
            cleanse_element=data.get("cleanse_element"),
        )


class BossFieldEffect(Effect):
    """Persistent field that deals damage each turn to all combatants."""

    def __init__(self, config: BossFieldConfig) -> None:
        super().__init__(config.duration)
        self._config = config

    @property
    def config(self) -> BossFieldConfig:
        return self._config

    @property
    def name(self) -> str:
        return self._config.name

    @property
    def stacking_key(self) -> str:
        return "boss_field"

    @property
    def category(self) -> EffectCategory:
        return EffectCategory.DEBUFF

    def compute_damage(self, max_hp: int) -> int:
        """Computes field damage for a target based on their max HP."""
        return max(1, int(max_hp * self._config.damage_pct_max_hp))

    def can_cleanse(self, element: str) -> bool:
        """Returns True if this field can be cleansed by the given element."""
        if self._config.cleanse_element is None:
            return False
        return element == self._config.cleanse_element

    def _do_tick(self) -> TickResult:
        return TickResult(message=self._config.name)
