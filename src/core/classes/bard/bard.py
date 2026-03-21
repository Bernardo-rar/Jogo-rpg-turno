from __future__ import annotations

from src.core.attributes.attributes import Attributes
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_resource_snapshot import (
    ClassResourceSnapshot,
    ResourceDisplayType,
)
from src.core.classes.bard.bard_config import load_bard_config
from src.core.classes.bard.musical_groove import MusicalGroove, load_groove_config

_CONFIG = load_bard_config()
_GROOVE_CONFIG = load_groove_config()


class Bard(Character):
    """Bardo: Buffer/Debuffer com Embalo Musical."""

    def __init__(
        self,
        name: str,
        attributes: Attributes,
        config: CharacterConfig,
    ) -> None:
        super().__init__(name, attributes, config)
        self._groove = MusicalGroove(_GROOVE_CONFIG)

    # --- Groove ---

    @property
    def groove(self) -> MusicalGroove:
        return self._groove

    def register_skill_use(self) -> None:
        """Chamado ao usar uma skill. Ganha stacks de embalo."""
        self._groove.gain()

    def tick_groove(self) -> None:
        """Fim do turno: decai stacks e tick crescendo."""
        self._groove.decay()
        self._groove.tick_crescendo()

    # --- Groove Bonuses (convenience) ---

    @property
    def groove_buff_bonus(self) -> float:
        return self._groove.buff_bonus

    @property
    def groove_debuff_bonus(self) -> float:
        return self._groove.debuff_bonus

    @property
    def groove_crit_bonus(self) -> float:
        return self._groove.crit_bonus

    # --- Passivas ---

    @property
    def buff_effectiveness_bonus(self) -> float:
        """Bonus passivo na efetividade de buffs."""
        return _CONFIG.buff_effectiveness_bonus

    @property
    def debuff_effectiveness_bonus(self) -> float:
        """Bonus passivo na efetividade de debuffs."""
        return _CONFIG.debuff_effectiveness_bonus

    @property
    def extra_bonus_actions(self) -> int:
        """Versatile Performer: bonus actions extras."""
        return _CONFIG.extra_bonus_actions

    # --- Speed Override ---

    @property
    def speed(self) -> int:
        """Speed base + bonus passivo + groove speed bonus."""
        base = super().speed
        passive = int(base * _CONFIG.speed_bonus_pct)
        groove = int(base * self._groove.speed_bonus)
        return base + passive + groove

    def get_resource_snapshots(self) -> tuple[ClassResourceSnapshot, ...]:
        """Retorna snapshots dos recursos do Bard para a UI."""
        return (
            ClassResourceSnapshot(
                name="Groove",
                display_type=ResourceDisplayType.COUNTER,
                current=self.groove.stacks,
                maximum=self.groove.max_stacks,
                color=(255, 120, 180),
            ),
        )
