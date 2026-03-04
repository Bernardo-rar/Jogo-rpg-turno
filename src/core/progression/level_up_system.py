"""Sistema de level up: gerencia XP, nivel e distribuicao de pontos."""

from __future__ import annotations

from src.core.attributes.attribute_types import AttributeType
from src.core.characters.character import Character
from src.core.progression.attribute_point_config import (
    LevelAttributePoints,
    get_points_for_level,
)
from src.core.progression.level_up_result import LevelUpResult
from src.core.progression.xp_table import XpTable, level_for_xp

PHYSICAL_ATTRIBUTES = frozenset({
    AttributeType.STRENGTH,
    AttributeType.DEXTERITY,
    AttributeType.CONSTITUTION,
})

MENTAL_ATTRIBUTES = frozenset({
    AttributeType.INTELLIGENCE,
    AttributeType.WISDOM,
    AttributeType.CHARISMA,
    AttributeType.MIND,
})


class LevelUpSystem:
    """Orquestra ganho de XP, level up e distribuicao de pontos."""

    def __init__(
        self,
        xp_table: XpTable,
        attribute_config: dict[int, LevelAttributePoints],
    ) -> None:
        self._xp_table = xp_table
        self._attribute_config = attribute_config
        self._xp: dict[int, int] = {}

    def get_xp(self, character: Character) -> int:
        """Retorna XP acumulado do personagem."""
        return self._xp.get(id(character), 0)

    def gain_xp(
        self,
        character: Character,
        amount: int,
    ) -> LevelUpResult | None:
        """Adiciona XP e aplica level up se necessario."""
        if amount <= 0:
            return None
        char_id = id(character)
        current_xp = self._xp.get(char_id, 0) + amount
        self._xp[char_id] = current_xp
        new_level = level_for_xp(current_xp, self._xp_table)
        if new_level <= character.level:
            return None
        return self._apply_level_up(character, new_level)

    def _apply_level_up(
        self,
        character: Character,
        new_level: int,
    ) -> LevelUpResult:
        """Aplica level up e retorna resultado com pontos a distribuir."""
        character._set_level(new_level)
        points = self._aggregate_points(character.level)
        return LevelUpResult(
            new_level=new_level,
            physical_points=points.physical,
            mental_points=points.mental,
        )

    def _aggregate_points(self, target_level: int) -> LevelAttributePoints:
        """Agrega pontos de todos os niveis pulados (multi-level up)."""
        total_phys = 0
        total_mental = 0
        for lvl in range(2, target_level + 1):
            pts = get_points_for_level(lvl, self._attribute_config)
            total_phys += pts.physical
            total_mental += pts.mental
        return LevelAttributePoints(
            physical=total_phys,
            mental=total_mental,
        )

    def distribute_physical_points(
        self,
        character: Character,
        distribution: dict[AttributeType, int],
    ) -> None:
        """Distribui pontos em atributos fisicos (STR, DEX, CON)."""
        self._validate_category(distribution, PHYSICAL_ATTRIBUTES, "physical")
        self._apply_distribution(character, distribution)

    def distribute_mental_points(
        self,
        character: Character,
        distribution: dict[AttributeType, int],
    ) -> None:
        """Distribui pontos em atributos mentais (INT, WIS, CHA, MIND)."""
        self._validate_category(distribution, MENTAL_ATTRIBUTES, "mental")
        self._apply_distribution(character, distribution)

    def _validate_category(
        self,
        distribution: dict[AttributeType, int],
        allowed: frozenset[AttributeType],
        category_name: str,
    ) -> None:
        for attr in distribution:
            if attr not in allowed:
                msg = f"{attr.name} is not a {category_name} attribute"
                raise ValueError(msg)

    def _apply_distribution(
        self,
        character: Character,
        distribution: dict[AttributeType, int],
    ) -> None:
        for attr, amount in distribution.items():
            character._attributes.increase(attr, amount)
        character.invalidate_threshold_cache()
