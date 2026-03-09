"""Configuracao imutavel para criacao de Character."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.class_modifiers import ClassModifiers
from src.core.characters.position import Position
from src.core.effects.effect_manager import EffectManager
from src.core.elements.elemental_profile import ElementalProfile

if TYPE_CHECKING:
    from src.core.items.accessory import Accessory
    from src.core.items.armor import Armor
    from src.core.items.inventory import Inventory
    from src.core.items.weapon import Weapon
    from src.core.skills.skill_bar import SkillBar


@dataclass(frozen=True)
class CharacterConfig:
    """Agrupa modificadores de classe, thresholds e parametros opcionais."""

    class_modifiers: ClassModifiers
    threshold_calculator: ThresholdCalculator
    level: int = 1
    position: Position = Position.FRONT
    elemental_profile: ElementalProfile | None = None
    effect_manager: EffectManager | None = None
    weapon: Weapon | None = None
    armor: Armor | None = None
    accessories: tuple[Accessory, ...] = ()
    skill_bar: SkillBar | None = None
    inventory: Inventory | None = None
