from __future__ import annotations

from src.core.attributes.attributes import Attributes
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_resource_snapshot import (
    ClassResourceSnapshot,
    ResourceDisplayType,
)
from src.core.classes.ranger.hunters_mark import HuntersMark, load_hunters_mark_config
from src.core.classes.ranger.predatory_focus import PredatoryFocus
from src.core.classes.ranger.predatory_focus_config import load_predatory_focus_config

_FOCUS_CONFIG = load_predatory_focus_config()
_MARK_CONFIG = load_hunters_mark_config()


class Ranger(Character):
    """Ranger: DPS critico continuo com Foco Predatorio e Marca do Cacador."""

    def __init__(
        self,
        name: str,
        attributes: Attributes,
        config: CharacterConfig,
    ) -> None:
        super().__init__(name, attributes, config)
        self._focus = PredatoryFocus(_FOCUS_CONFIG.max_stacks)
        self._mark = HuntersMark()

    @property
    def predatory_focus(self) -> PredatoryFocus:
        return self._focus

    @property
    def hunters_mark(self) -> HuntersMark:
        return self._mark

    def register_hit(self) -> int:
        """Registra acerto: ganha stacks de foco."""
        return self._focus.gain(_FOCUS_CONFIG.stacks_per_hit)

    def register_miss(self) -> int:
        """Registra erro: perde stacks * multiplier."""
        loss = int(
            _FOCUS_CONFIG.stacks_per_hit * _FOCUS_CONFIG.miss_loss_multiplier,
        )
        return self._focus.lose(loss)

    def decay_focus(self) -> int:
        """Decai foco no fim do turno."""
        return self._focus.decay(_FOCUS_CONFIG.decay_per_turn)

    def mark_target(self, target_name: str) -> None:
        """Marca um alvo para armor penetration."""
        self._mark.mark(target_name)

    def clear_mark(self) -> None:
        """Remove marca ativa."""
        self._mark.clear()

    def get_armor_penetration(self, target_name: str) -> float:
        """Retorna % de armor pen se target esta marcado, 0.0 caso contrario."""
        if not self._mark.is_active:
            return 0.0
        if self._mark.target_name != target_name:
            return 0.0
        return _MARK_CONFIG.armor_penetration_pct

    @property
    def crit_chance_bonus(self) -> float:
        """Bonus de crit chance baseado em stacks de foco."""
        return self._focus.current * _FOCUS_CONFIG.crit_chance_per_stack

    @property
    def crit_damage_multiplier(self) -> float:
        """Multiplicador extra de crit damage (1.0 = sem bonus)."""
        return 1.0 + self._focus.current * _FOCUS_CONFIG.crit_damage_per_stack

    @property
    def physical_attack(self) -> int:
        base = super().physical_attack
        focus_mult = 1.0 + self._focus.current * _FOCUS_CONFIG.atk_bonus_per_stack
        return int(base * focus_mult)

    def get_resource_snapshots(self) -> tuple[ClassResourceSnapshot, ...]:
        """Retorna snapshots dos recursos do Ranger para a UI."""
        return (
            ClassResourceSnapshot(
                name="Focus",
                display_type=ResourceDisplayType.COUNTER,
                current=self.predatory_focus.current,
                maximum=self.predatory_focus.max_stacks,
                color=(50, 200, 80),
            ),
        )
