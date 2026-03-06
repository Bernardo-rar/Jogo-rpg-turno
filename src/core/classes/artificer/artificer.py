from __future__ import annotations

from src.core.attributes.attributes import Attributes
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.classes.artificer.artificer_config import load_artificer_config
from src.core.classes.artificer.tech_suit import TechSuit, load_suit_config

_CONFIG = load_artificer_config()
_SUIT_CONFIG = load_suit_config()


class Artificer(Character):
    """Artifice: Support/Mana com Traje Tecmagis."""

    def __init__(
        self,
        name: str,
        attributes: Attributes,
        config: CharacterConfig,
    ) -> None:
        super().__init__(name, attributes, config)
        self._tech_suit = TechSuit(_SUIT_CONFIG)

    # --- TechSuit ---

    @property
    def tech_suit(self) -> TechSuit:
        return self._tech_suit

    def _mana_ratio(self) -> float:
        return TechSuit.mana_ratio(self.current_mana, self.max_mana)

    # --- Stat Overrides (mana scaling) ---

    @property
    def magical_attack(self) -> int:
        base = super().magical_attack
        return int(base * self._tech_suit.atk_multiplier(self._mana_ratio()))

    @property
    def physical_defense(self) -> int:
        base = super().physical_defense
        mult = self._tech_suit.phys_def_multiplier(self._mana_ratio())
        return int(base * mult)

    @property
    def magical_defense(self) -> int:
        base = super().magical_defense
        passive = 1.0 + _CONFIG.magical_defense_bonus
        suit = self._tech_suit.mag_def_multiplier(self._mana_ratio())
        return int(base * passive * suit)

    # --- Passivas ---

    @property
    def mana_regen(self) -> int:
        base = super().mana_regen
        return int(base * (1.0 + _CONFIG.mana_regen_bonus))

    @property
    def scroll_potentiation(self) -> float:
        """Bonus percentual ao dano de scrolls."""
        return _CONFIG.scroll_potentiation
