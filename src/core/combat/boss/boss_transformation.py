"""BossTransformation — replaces boss stats/name/position at HP threshold."""

from __future__ import annotations

from dataclasses import dataclass

from src.core.characters.character import Character
from src.core.characters.class_modifiers import ClassModifiers
from src.core.characters.position import Position


@dataclass(frozen=True)
class TransformationConfig:
    """Config for a boss transformation loaded from JSON."""

    hp_threshold: float
    new_name: str
    battle_cry: str
    heal_pct: float
    new_class_modifiers: ClassModifiers
    new_elemental_profile_id: str | None = None
    new_position: Position | None = None

    @classmethod
    def from_dict(cls, data: dict) -> TransformationConfig:
        mods = ClassModifiers.from_dict(data["new_class_modifiers"])
        pos_str = data.get("new_position")
        pos = Position[pos_str] if pos_str else None
        return cls(
            hp_threshold=float(data["hp_threshold"]),
            new_name=str(data["new_name"]),
            battle_cry=str(data.get("battle_cry", "")),
            heal_pct=float(data.get("heal_pct", 0.0)),
            new_class_modifiers=mods,
            new_elemental_profile_id=data.get(
                "new_elemental_profile_id",
            ),
            new_position=pos,
        )


def apply_transformation(
    boss: Character,
    config: TransformationConfig,
) -> None:
    """Applies transformation: new name, modifiers, heal, position."""
    boss._name = config.new_name
    boss._modifiers = config.new_class_modifiers
    if config.new_position is not None:
        boss.change_position(config.new_position)
    _heal_boss(boss, config.heal_pct)


def _heal_boss(boss: Character, heal_pct: float) -> None:
    """Heals boss by heal_pct of new max HP."""
    if heal_pct <= 0:
        return
    heal_amount = int(boss.max_hp * heal_pct)
    boss.heal(heal_amount)
