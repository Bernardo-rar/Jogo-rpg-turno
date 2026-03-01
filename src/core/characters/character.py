from __future__ import annotations

from src.core.attributes.attributes import Attributes
from src.core.characters.character_config import CharacterConfig
from src.core.characters.combat_stats_mixin import CombatStatsMixin
from src.core.characters.position import Position
from src.core.characters.threshold_mixin import ThresholdBonusMixin
from src.core.effects.effect import Effect
from src.core.effects.effect_manager import EffectManager
from src.core.effects.modifiable_stat import ModifiableStat
from src.core.elements.elemental_profile import ElementalProfile


class Character(ThresholdBonusMixin, CombatStatsMixin):
    """Classe base de personagem. Subclasses (Fighter, Mage, etc.) herdam dela."""

    def __init__(
        self,
        name: str,
        attributes: Attributes,
        config: CharacterConfig,
    ) -> None:
        self._name = name
        self._attributes = attributes
        self._modifiers = config.class_modifiers
        self._threshold_calc = config.threshold_calculator
        self._level = config.level
        self._position = config.position
        self._alive = True
        self._threshold_cache: dict[str, int] | None = None
        self._effect_manager = config.effect_manager or EffectManager()
        self._elemental_profile = config.elemental_profile or ElementalProfile()
        self._current_hp = self.max_hp
        self._current_mana = self.max_mana

    @property
    def name(self) -> str:
        return self._name

    @property
    def level(self) -> int:
        return self._level

    @property
    def position(self) -> Position:
        return self._position

    @property
    def is_alive(self) -> bool:
        return self._alive

    @property
    def effect_manager(self) -> EffectManager:
        return self._effect_manager

    @property
    def elemental_profile(self) -> ElementalProfile:
        return self._elemental_profile

    @property
    def current_hp(self) -> int:
        return self._current_hp

    @property
    def current_mana(self) -> int:
        return self._current_mana

    def take_damage(self, amount: int) -> int:
        actual = min(amount, self._current_hp)
        self._current_hp -= actual
        if self._current_hp == 0:
            self._alive = False
        return actual

    def heal(self, amount: int) -> int:
        if not self._alive:
            return 0
        modified = self._apply_effect_modifiers(
            ModifiableStat.HEALING_RECEIVED, amount,
        )
        actual = min(modified, self.max_hp - self._current_hp)
        self._current_hp += actual
        return actual

    def spend_mana(self, amount: int) -> bool:
        if amount > self._current_mana:
            return False
        self._current_mana -= amount
        return True

    def drain_mana(self, amount: int) -> int:
        """Drena mana ate o disponivel. Retorna quantidade real drenada."""
        actual = min(amount, self._current_mana)
        self._current_mana -= actual
        return actual

    def restore_mana(self, amount: int) -> int:
        actual = min(amount, self.max_mana - self._current_mana)
        self._current_mana += actual
        return actual

    def change_position(self, new_position: Position) -> None:
        self._position = new_position

    def apply_regen(self) -> None:
        self.heal(self.hp_regen)
        self.restore_mana(self.mana_regen)

    def add_effect(self, effect: Effect) -> None:
        """Adiciona efeito ao personagem."""
        self._effect_manager.add_effect(effect)

    def has_active_effects(self) -> bool:
        """True se tem efeitos ativos."""
        return self._effect_manager.count > 0
