from __future__ import annotations

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_resource_snapshot import (
    ClassResourceSnapshot,
    ResourceDisplayType,
)
from src.core.classes.rogue.rogue_config import load_rogue_config
from src.core.classes.rogue.stealth import Stealth

_CONFIG = load_rogue_config()


class Rogue(Character):
    """Ladino: DPS/Utility com stealth, crits e uso livre de itens."""

    def __init__(
        self,
        name: str,
        attributes: Attributes,
        config: CharacterConfig,
    ) -> None:
        super().__init__(name, attributes, config)
        self._stealth = Stealth()
        self._crit_speed_remaining: int = 0

    # --- Stealth ---

    @property
    def stealth(self) -> Stealth:
        return self._stealth

    @property
    def guaranteed_crit(self) -> bool:
        return self._stealth.guaranteed_crit

    def enter_stealth(self) -> bool:
        """Ativa stealth. Retorna False se ja estava ativo."""
        return self._stealth.enter()

    def break_stealth(self) -> bool:
        """Quebra stealth. Retorna False se ja estava inativo."""
        return self._stealth.break_stealth()

    def take_damage(self, amount: int) -> int:
        """Recebe dano e quebra stealth automaticamente."""
        self._stealth.break_stealth()
        return super().take_damage(amount)

    # --- Passivas ---

    @property
    def free_item_use(self) -> bool:
        """Ladino usa itens sem gastar acao."""
        return True

    @property
    def crit_chance_bonus(self) -> float:
        """Bonus de crit escalando com DEX."""
        dex = self._attributes.get(AttributeType.DEXTERITY)
        return dex * _CONFIG.crit_bonus_per_dex

    @property
    def poison_damage_bonus(self) -> float:
        """Bonus percentual ao dano de veneno."""
        return _CONFIG.poison_damage_bonus

    @property
    def extra_skill_slots(self) -> int:
        """Cabeca Fria: slots extras de habilidade."""
        return _CONFIG.extra_skill_slots

    # --- Speed Override ---

    @property
    def speed(self) -> int:
        """Speed base + bonus passivo + bonus de crit."""
        base = super().speed
        passive = int(base * _CONFIG.speed_bonus_pct)
        crit = self._crit_speed_bonus(base)
        return base + passive + crit

    def _crit_speed_bonus(self, base_speed: int) -> int:
        """Bonus temporario de speed apos crit."""
        if self._crit_speed_remaining <= 0:
            return 0
        return int(base_speed * _CONFIG.crit_speed_boost_pct)

    # --- Crit Speed Boost ---

    def on_crit(self) -> None:
        """Chamado pelo combat handler ao critar."""
        self._crit_speed_remaining = _CONFIG.crit_speed_boost_duration

    def tick_crit_speed_boost(self) -> None:
        """Decrementa boost de speed no fim do turno."""
        if self._crit_speed_remaining > 0:
            self._crit_speed_remaining -= 1

    def get_resource_snapshots(self) -> tuple[ClassResourceSnapshot, ...]:
        """Retorna snapshots dos recursos do Rogue para a UI."""
        return (
            ClassResourceSnapshot(
                name="Stealth",
                display_type=ResourceDisplayType.TOGGLE,
                current=1 if self.stealth.is_active else 0,
                maximum=1,
                color=(80, 80, 120),
                label="Active" if self.stealth.is_active else "Hidden",
            ),
        )
