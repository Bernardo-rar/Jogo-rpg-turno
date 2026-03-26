from __future__ import annotations

from src.core.attributes.attributes import Attributes
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_resource_snapshot import (
    ClassResourceSnapshot,
    ResourceDisplayType,
)
from src.core.classes.paladin.aura import Aura, AuraModifier, load_aura_modifiers
from src.core.classes.paladin.divine_favor import DivineFavor
from src.core.classes.paladin.glory_config import load_glory_config

DIVINE_FAVOR_MAX = 10

_AURA_MODIFIERS = load_aura_modifiers()
_GLORY_CONFIG = load_glory_config()


class Paladin(Character):
    """Paladino: Tank defensivo com Auras, Favor Divino e Glimpse of Glory."""

    def __init__(
        self,
        name: str,
        attributes: Attributes,
        config: CharacterConfig,
    ) -> None:
        super().__init__(name, attributes, config)
        self._divine_favor = DivineFavor(DIVINE_FAVOR_MAX)
        self._aura = Aura.NONE
        self._glory_active = False
        self._glory_turns = 0

    @property
    def divine_favor(self) -> DivineFavor:
        return self._divine_favor

    @property
    def aura(self) -> Aura:
        return self._aura

    def change_aura(self, new_aura: Aura) -> None:
        self._aura = new_aura

    def gain_favor(self) -> int:
        """Ganha +1 favor divino (proteger, buffar ou curar aliado)."""
        return self._divine_favor.gain()

    @property
    def is_glory_active(self) -> bool:
        return self._glory_active

    def activate_glimpse_of_glory(self) -> bool:
        """Ativa Glimpse of Glory. Requer aura ativa e favor suficiente."""
        if self._glory_active:
            return False
        if self._aura == Aura.NONE:
            return False
        if not self._divine_favor.spend(_GLORY_CONFIG.favor_cost):
            return False
        self._glory_active = True
        self._glory_turns = _GLORY_CONFIG.duration_turns
        return True

    def tick_glory(self) -> None:
        """Decrementa duracao do Glory. Desativa se expirou."""
        if not self._glory_active:
            return
        self._glory_turns -= 1
        if self._glory_turns <= 0:
            self._glory_active = False

    def _aura_multiplier(self, field: str) -> float:
        base = getattr(self._current_aura_mod, field)
        if self._glory_active:
            return 1.0 + (base - 1.0) * _GLORY_CONFIG.aura_boost_multiplier
        return base

    @property
    def _current_aura_mod(self) -> AuraModifier:
        return _AURA_MODIFIERS[self._aura]

    @property
    def physical_attack(self) -> int:
        base = super().physical_attack
        return int(base * self._aura_multiplier("atk_multiplier"))

    @property
    def magical_attack(self) -> int:
        base = super().magical_attack
        return int(base * self._aura_multiplier("atk_multiplier"))

    @property
    def physical_defense(self) -> int:
        base = super().physical_defense
        return int(base * self._aura_multiplier("def_multiplier"))

    @property
    def magical_defense(self) -> int:
        base = super().magical_defense
        return int(base * self._aura_multiplier("def_multiplier"))

    @property
    def hp_regen(self) -> int:
        base = super().hp_regen
        return int(base * self._aura_multiplier("regen_multiplier"))

    def get_resource_snapshots(self) -> tuple[ClassResourceSnapshot, ...]:
        """Retorna snapshots dos recursos do Paladin para a UI."""
        return (
            ClassResourceSnapshot(
                name="Divine Favor",
                display_type=ResourceDisplayType.COUNTER,
                current=self.divine_favor.current,
                maximum=self.divine_favor.max_stacks,
                color=(255, 220, 100),
            ),
            ClassResourceSnapshot(
                name="Aura",
                display_type=ResourceDisplayType.TOGGLE,
                current=1,
                maximum=1,
                color=(255, 220, 100),
                label=self._aura.name,
            ),
        )
