from __future__ import annotations

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.classes.cleric.divinity import Divinity, load_divinity_configs
from src.core.classes.cleric.holy_power import HOLY_POWER_PER_HEAL, HolyPower

_DIVINITY_CONFIGS = load_divinity_configs()

HEAL_MANA_COST = 30
HEALING_POWER_MOD = 3
CHANNEL_DIVINITY_COST = 3
CHANNEL_ATK_MULTIPLIER = 1.3
CHANNEL_DEF_MULTIPLIER = 1.3


class Cleric(Character):
    """Clerigo: Healer/Buffer versatil com Divindade e Channel Divinity."""

    def __init__(
        self,
        name: str,
        attributes: Attributes,
        config: CharacterConfig,
        *,
        divinity: Divinity = Divinity.HOLY,
    ) -> None:
        super().__init__(name, attributes, config)
        self._divinity = divinity
        self._holy_power = HolyPower()
        self._channeling = False

    @property
    def divinity(self) -> Divinity:
        return self._divinity

    @property
    def holy_power(self) -> HolyPower:
        return self._holy_power

    @property
    def healing_power(self) -> int:
        """Poder de cura: WIS * mod * bonus da divindade."""
        wis = self._attributes.get(AttributeType.WISDOM)
        bonus = _DIVINITY_CONFIGS[self._divinity].healing_bonus
        return int(wis * HEALING_POWER_MOD * bonus)

    def heal_target(self, target: Character) -> int:
        """Cura um aliado. Gasta mana, ganha holy power."""
        if not self.spend_mana(HEAL_MANA_COST):
            return 0
        healed = target.heal(self.healing_power)
        self._holy_power.gain(HOLY_POWER_PER_HEAL)
        return healed

    @property
    def is_channeling(self) -> bool:
        return self._channeling

    def channel_divinity(self) -> bool:
        """Canaliza divindade: gasta holy power, buffa atk/def magicos."""
        if self._channeling:
            return False
        if not self._holy_power.spend(CHANNEL_DIVINITY_COST):
            return False
        self._channeling = True
        return True

    def end_channel(self) -> None:
        """Encerra canalizacao."""
        self._channeling = False

    @property
    def magical_attack(self) -> int:
        base = super().magical_attack
        if self._channeling:
            return int(base * CHANNEL_ATK_MULTIPLIER)
        return base

    @property
    def magical_defense(self) -> int:
        base = super().magical_defense
        if self._channeling:
            return int(base * CHANNEL_DEF_MULTIPLIER)
        return base
