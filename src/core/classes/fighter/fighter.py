from __future__ import annotations

from src.core.attributes.attributes import Attributes
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.classes.fighter.action_points import ActionPoints
from src.core.classes.fighter.stance import Stance, StanceModifier, load_stance_modifiers

_STANCE_MODIFIERS = load_stance_modifiers()


class Fighter(Character):
    """Guerreiro: Tank/DPS adaptavel com Pontos de Acao e Estancias."""

    def __init__(
        self,
        name: str,
        attributes: Attributes,
        config: CharacterConfig,
    ) -> None:
        super().__init__(name, attributes, config)
        self._action_points = ActionPoints(config.level)
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

    def on_level_up(self) -> None:
        """Atualiza AP limit ao subir de nivel."""
        self._action_points.update_limit(self._level)

    @property
    def _current_stance_mod(self) -> StanceModifier:
        return _STANCE_MODIFIERS[self._stance]
