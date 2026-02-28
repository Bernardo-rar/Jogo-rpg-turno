from __future__ import annotations

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character import Character
from src.core.characters.class_modifiers import ClassModifiers
from src.core.characters.position import Position
from src.core.classes.mage.barrier import BARRIER_EFFICIENCY, Barrier
from src.core.classes.mage.overcharge import OverchargeConfig, load_overcharge_config

_OVERCHARGE_CONFIG = load_overcharge_config()

MANA_PER_BASIC_ATTACK_MOD = 3


class Mage(Character):
    """Mago: Glass cannon com AOE elemental, Overcharge e Barreiras."""

    def __init__(
        self,
        name: str,
        attributes: Attributes,
        class_modifiers: ClassModifiers,
        *,
        threshold_calculator: ThresholdCalculator,
        level: int = 1,
        position: Position = Position.BACK,
    ) -> None:
        super().__init__(
            name, attributes, class_modifiers,
            threshold_calculator=threshold_calculator,
            level=level, position=position,
        )
        self._barrier = Barrier()
        self._overcharged = False

    @property
    def barrier(self) -> Barrier:
        return self._barrier

    def create_barrier(self, mana_cost: int) -> bool:
        """Gasta mana para criar barreira. Retorna False se mana insuficiente."""
        if not self.spend_mana(mana_cost):
            return False
        self._barrier.add(mana_cost * BARRIER_EFFICIENCY)
        return True

    def take_damage(self, amount: int) -> int:
        """Dano passa pela barreira antes de atingir HP."""
        remaining = self._barrier.absorb(amount)
        barrier_absorbed = amount - remaining
        hp_damage = super().take_damage(remaining)
        return barrier_absorbed + hp_damage

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
