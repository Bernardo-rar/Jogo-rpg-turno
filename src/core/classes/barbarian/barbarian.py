from __future__ import annotations

from src.core.attributes.attributes import Attributes
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.classes.barbarian.fury_bar import FuryBar
from src.core.classes.barbarian.fury_config import load_fury_config

_FURY_CONFIG = load_fury_config()


class Barbarian(Character):
    """Barbaro: DPS brutal com Barra de Furia e dano por HP perdido."""

    def __init__(
        self,
        name: str,
        attributes: Attributes,
        config: CharacterConfig,
    ) -> None:
        super().__init__(name, attributes, config)
        fury_max = int(self.max_hp * _FURY_CONFIG.fury_max_ratio)
        self._fury_bar = FuryBar(fury_max)

    @property
    def fury_bar(self) -> FuryBar:
        return self._fury_bar

    def take_damage(self, amount: int) -> int:
        """Recebe dano e ganha fury proporcional."""
        actual = super().take_damage(amount)
        fury_gained = int(actual * _FURY_CONFIG.fury_on_damage_ratio)
        self._fury_bar.gain(fury_gained)
        return actual

    def generate_fury_from_attack(self) -> int:
        """Gera fury ao atacar. Retorna fury real ganha."""
        return self._fury_bar.gain(_FURY_CONFIG.fury_on_basic_attack)

    def decay_fury(self) -> int:
        """Decai fury no fim do turno. Retorna quantidade decaida."""
        return self._fury_bar.decay(_FURY_CONFIG.fury_decay_per_turn)

    @property
    def _missing_hp_ratio(self) -> float:
        """Razao de HP faltando (0.0 = full, ~1.0 = quase morto)."""
        if self.max_hp == 0:
            return 0.0
        return 1.0 - (self.current_hp / self.max_hp)

    @property
    def physical_attack(self) -> int:
        base = super().physical_attack
        fury_mult = 1.0 + (
            self._fury_bar.fury_ratio * _FURY_CONFIG.atk_bonus_at_max_fury
        )
        missing_mult = 1.0 + (
            self._missing_hp_ratio * _FURY_CONFIG.missing_hp_atk_bonus
        )
        return int(base * fury_mult * missing_mult)

    @property
    def hp_regen(self) -> int:
        base = super().hp_regen
        regen_mult = 1.0 + (
            self._fury_bar.fury_ratio * _FURY_CONFIG.regen_bonus_at_max_fury
        )
        return int(base * regen_mult)

    def on_level_up(self) -> None:
        """Atualiza fury max baseado no novo max_hp."""
        new_max = int(self.max_hp * _FURY_CONFIG.fury_max_ratio)
        self._fury_bar.update_max(new_max)
