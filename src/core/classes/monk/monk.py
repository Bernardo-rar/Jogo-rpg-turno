from __future__ import annotations

from src.core.attributes.attributes import Attributes
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_resource_snapshot import (
    ClassResourceSnapshot,
    ResourceDisplayType,
)
from src.core.classes.monk.equilibrium_bar import (
    EquilibriumBar,
    EquilibriumState,
)
from src.core.classes.monk.equilibrium_config import load_equilibrium_config

_EQ_CONFIG = load_equilibrium_config()


class Monk(Character):
    """Monk: DPS multi-hit com barra Equilibrium."""

    def __init__(
        self,
        name: str,
        attributes: Attributes,
        config: CharacterConfig,
    ) -> None:
        super().__init__(name, attributes, config)
        self._eq = EquilibriumBar(
            _EQ_CONFIG.max_value,
            _EQ_CONFIG.vitality_upper,
            _EQ_CONFIG.destruction_lower,
        )

    @property
    def equilibrium(self) -> EquilibriumBar:
        return self._eq

    def attack_action(self) -> int:
        """Registra acao ofensiva: desloca barra pro Destruction."""
        return self._eq.shift_toward_destruction(_EQ_CONFIG.shift_per_attack)

    def defensive_action(self) -> int:
        """Registra acao defensiva: desloca barra pro Vitality."""
        return self._eq.shift_toward_vitality(_EQ_CONFIG.shift_per_defend)

    def end_of_turn_decay(self) -> int:
        """Decai barra pro centro no fim do turno."""
        return self._eq.decay_toward_center(_EQ_CONFIG.decay_per_turn)

    @property
    def hit_count(self) -> int:
        """Numero de hits por acao de ataque."""
        base = _EQ_CONFIG.base_hit_count
        if self._eq.state == EquilibriumState.DESTRUCTION:
            return base + _EQ_CONFIG.destruction_extra_hits
        return base

    @property
    def crit_chance_bonus(self) -> float:
        """Bonus de crit chance (escala com destruction intensity)."""
        return self._eq.destruction_intensity * _EQ_CONFIG.destruction_crit_bonus

    @property
    def debuff_chance_bonus(self) -> float:
        """Chance de aplicar debuff por hit (escala com destruction)."""
        return self._eq.destruction_intensity * _EQ_CONFIG.debuff_chance_max

    @property
    def physical_attack(self) -> int:
        base = super().physical_attack
        return int(base * (1.0 + self._get_atk_bonus()))

    @property
    def physical_defense(self) -> int:
        base = super().physical_defense
        return int(base * (1.0 + self._get_def_bonus()))

    def _get_atk_bonus(self) -> float:
        state = self._eq.state
        if state == EquilibriumState.DESTRUCTION:
            return self._eq.destruction_intensity * _EQ_CONFIG.destruction_atk_bonus
        if state == EquilibriumState.BALANCED:
            return _EQ_CONFIG.balance_atk_bonus
        return 0.0

    def _get_def_bonus(self) -> float:
        state = self._eq.state
        if state == EquilibriumState.VITALITY:
            return self._eq.vitality_intensity * _EQ_CONFIG.vitality_def_bonus
        if state == EquilibriumState.BALANCED:
            return _EQ_CONFIG.balance_def_bonus
        return 0.0

    def get_resource_snapshots(self) -> tuple[ClassResourceSnapshot, ...]:
        """Retorna snapshots dos recursos do Monk para a UI."""
        return (
            ClassResourceSnapshot(
                name="Equilibrium",
                display_type=ResourceDisplayType.BAR,
                current=self.equilibrium.value,
                maximum=self.equilibrium.max_value,
                color=(100, 220, 220),
                label=self.equilibrium.state.name,
            ),
        )
