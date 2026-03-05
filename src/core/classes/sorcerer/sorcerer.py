from __future__ import annotations

from src.core.attributes.attributes import Attributes
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.classes.sorcerer.mana_rotation import (
    ManaRotation,
    load_mana_rotation_config,
)
from src.core.classes.sorcerer.overcharged_config import load_overcharged_config
from src.core.elements.element_type import ElementType

_OVERCHARGED_CONFIG = load_overcharged_config()
_ROTATION_CONFIG = load_mana_rotation_config()


class Sorcerer(Character):
    """Feiticeiro: DPS magico puro com Overcharged, Metamagia e Rotacao de Mana."""

    def __init__(
        self,
        name: str,
        attributes: Attributes,
        config: CharacterConfig,
    ) -> None:
        super().__init__(name, attributes, config)
        self._overcharged = False
        self._current_metamagic: ElementType | None = None
        rotation_max = int(self.max_mana * _ROTATION_CONFIG.max_ratio)
        self._mana_rotation = ManaRotation(max_mana=rotation_max)

    @property
    def mana_rotation(self) -> ManaRotation:
        return self._mana_rotation

    # --- Overcharged ---

    @property
    def is_overcharged(self) -> bool:
        return self._overcharged

    def activate_overcharged(self) -> bool:
        """Ativa overcharged. Retorna False se ja ativo."""
        if self._overcharged:
            return False
        self._overcharged = True
        return True

    def deactivate_overcharged(self) -> None:
        self._overcharged = False

    def apply_overcharged_cost(self) -> None:
        """Aplica custo de mana e self-damage. Auto-desativa se mana insuficiente."""
        if not self._overcharged:
            return
        if not self.spend_mana(_OVERCHARGED_CONFIG.mana_cost_per_turn):
            self._overcharged = False
            return
        self_damage = int(self.max_hp * _OVERCHARGED_CONFIG.self_damage_pct)
        self.take_damage(self_damage)

    @property
    def magical_attack(self) -> int:
        base = super().magical_attack
        born_bonus = int(base * _OVERCHARGED_CONFIG.born_of_magic_bonus)
        boosted = base + born_bonus
        if self._overcharged:
            return int(boosted * _OVERCHARGED_CONFIG.atk_multiplier)
        return boosted

    # --- Metamagia ---

    @property
    def current_metamagic(self) -> ElementType | None:
        return self._current_metamagic

    def set_metamagic(self, element: ElementType) -> bool:
        """Troca elemento do proximo ataque. Custa mana."""
        if not self.spend_mana(_OVERCHARGED_CONFIG.metamagic_mana_cost):
            return False
        self._current_metamagic = element
        return True

    def consume_metamagic(self) -> ElementType | None:
        """Retorna e limpa o elemento metamagico atual."""
        element = self._current_metamagic
        self._current_metamagic = None
        return element

    # --- Mana Rotation ---

    def on_deal_magic_damage(self, damage_dealt: int) -> int:
        """Ao causar dano magico, ganha mana via rotacao. Retorna mana restaurada."""
        mana_gain = int(damage_dealt * _ROTATION_CONFIG.gain_ratio)
        stored = self._mana_rotation.gain(mana_gain)
        self.restore_mana(stored)
        return stored

    def apply_rotation_decay(self) -> None:
        """Aplica decay da rotacao de mana no fim do turno."""
        self._mana_rotation.decay(_ROTATION_CONFIG.decay_per_turn)

    # --- Level Up ---

    def on_level_up(self) -> None:
        new_max = int(self.max_mana * _ROTATION_CONFIG.max_ratio)
        self._mana_rotation.update_max(new_max)
