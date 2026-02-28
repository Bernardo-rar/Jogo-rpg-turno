from __future__ import annotations

from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character import Character
from src.core.characters.class_modifiers import ClassModifiers
from src.core.characters.position import Position
from src.core.classes.fighter.action_points import ActionPoints
from src.core.classes.fighter.stance import Stance, StanceModifier, load_stance_modifiers

_STANCE_MODIFIERS = load_stance_modifiers()


class Fighter(Character):
    """Guerreiro: Tank/DPS adaptavel com Pontos de Acao e Estancias."""

    def __init__(
        self,
        name: str,
        attributes: Attributes,
        class_modifiers: ClassModifiers,
        *,
        threshold_calculator: ThresholdCalculator,
        level: int = 1,
        position: Position = Position.FRONT,
    ) -> None:
        super().__init__(
            name, attributes, class_modifiers,
            threshold_calculator=threshold_calculator,
            level=level, position=position,
        )
        self._action_points = ActionPoints(level)
        self._stance = Stance.NORMAL

    @property
    def action_points(self) -> ActionPoints:
        return self._action_points

    @property
    def stance(self) -> Stance:
        return self._stance

    def change_stance(self, new_stance: Stance) -> None:
        self._stance = new_stance

    @property
    def physical_attack(self) -> int:
        base = super().physical_attack
        return int(base * self._current_stance_mod.atk_multiplier)

    @property
    def magical_attack(self) -> int:
        base = super().magical_attack
        return int(base * self._current_stance_mod.atk_multiplier)

    @property
    def physical_defense(self) -> int:
        base = super().physical_defense
        return int(base * self._current_stance_mod.def_multiplier)

    @property
    def magical_defense(self) -> int:
        base = super().magical_defense
        return int(base * self._current_stance_mod.def_multiplier)

    @property
    def _current_stance_mod(self) -> StanceModifier:
        return _STANCE_MODIFIERS[self._stance]
