from __future__ import annotations

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_resource_snapshot import (
    ClassResourceSnapshot,
    ResourceDisplayType,
)
from src.core.classes.mage.barrier import BARRIER_EFFICIENCY
from src.core.classes.mage.overcharge import OverchargeConfig, load_overcharge_config

_OVERCHARGE_CONFIG = load_overcharge_config()

MANA_PER_BASIC_ATTACK_MOD = 3


class Mage(Character):
    """Mago: Glass cannon com AOE elemental, Overcharge e Barreiras."""

    def __init__(
        self,
        name: str,
        attributes: Attributes,
        config: CharacterConfig,
    ) -> None:
        super().__init__(name, attributes, config)
        self._overcharged = False

    def create_barrier(self, mana_cost: int) -> bool:
        """Gasta mana para criar barreira. Retorna False se mana insuficiente."""
        if not self.spend_mana(mana_cost):
            return False
        self._barrier.add(mana_cost * BARRIER_EFFICIENCY)
        return True

    @property
    def is_overcharged(self) -> bool:
        return self._overcharged

    def activate_overcharge(self) -> bool:
        """Ativa overcharge. Retorna False se ja ativo."""
        if self._overcharged:
            return False
        self._overcharged = True
        return True

    def deactivate_overcharge(self) -> None:
        """Desativa overcharge."""
        self._overcharged = False

    def apply_overcharge_cost(self) -> None:
        """Aplica custo de mana do overcharge. Auto-desativa se insuficiente."""
        if not self._overcharged:
            return
        if not self.spend_mana(_OVERCHARGE_CONFIG.mana_cost_per_turn):
            self._overcharged = False

    @property
    def magical_attack(self) -> int:
        base = super().magical_attack
        if self._overcharged:
            return int(base * _OVERCHARGE_CONFIG.atk_multiplier)
        return base

    @property
    def mana_per_basic_attack(self) -> int:
        """Mana gerada por ataque basico: MIND * mod."""
        mind = self._attributes.get(AttributeType.MIND)
        return mind * MANA_PER_BASIC_ATTACK_MOD

    def get_resource_snapshots(self) -> tuple[ClassResourceSnapshot, ...]:
        """Retorna snapshots dos recursos do Mage para a UI."""
        return (
            ClassResourceSnapshot(
                name="Barrier",
                display_type=ResourceDisplayType.BAR,
                current=self.barrier.current,
                maximum=self.barrier.max_value,
                color=(150, 200, 255),
            ),
            ClassResourceSnapshot(
                name="Overcharge",
                display_type=ResourceDisplayType.TOGGLE,
                current=1 if self.is_overcharged else 0,
                maximum=1,
                color=(150, 200, 255),
                label="ON" if self.is_overcharged else "OFF",
            ),
        )
