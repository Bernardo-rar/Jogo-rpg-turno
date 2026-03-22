"""EnemyFactory — cria Character inimigos a partir de EnemyTemplate."""

from __future__ import annotations

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.elements.elemental_profile import ElementalProfile
from src.core.items.weapon import Weapon
from src.core.skills.skill import Skill
from src.core.skills.skill_bar import SkillBar
from src.core.skills.spell_slot import SpellSlot
from src.dungeon.enemies.enemy_template import EnemyTemplate

_EMPTY_THRESHOLDS = ThresholdCalculator({})
_SKILL_BAR_BUDGET = 100


class EnemyFactory:
    """Cria Characters inimigos resolvendo IDs do template em objetos reais."""

    def __init__(
        self,
        weapon_catalog: dict[str, Weapon],
        profile_catalog: dict[str, ElementalProfile],
        skill_catalog: dict[str, Skill],
    ) -> None:
        self._weapons = weapon_catalog
        self._profiles = profile_catalog
        self._skills = skill_catalog

    def create(self, template: EnemyTemplate, suffix: str = "") -> Character:
        """Cria um Character a partir de um EnemyTemplate."""
        name = f"{template.name}_{suffix}" if suffix else template.name
        attrs = _build_attributes(template.base_attributes)
        config = self._build_config(template)
        return Character(name, attrs, config)

    def _build_config(self, template: EnemyTemplate) -> CharacterConfig:
        weapon = self._weapons.get(template.weapon_id)
        profile = self._profiles.get(template.elemental_profile_id)
        skill_bar = self._build_skill_bar(template.skill_ids)
        return CharacterConfig(
            class_modifiers=template.class_modifiers,
            threshold_calculator=_EMPTY_THRESHOLDS,
            position=template.position,
            weapon=weapon,
            elemental_profile=profile,
            skill_bar=skill_bar,
        )

    def _build_skill_bar(self, skill_ids: tuple[str, ...]) -> SkillBar | None:
        if not skill_ids:
            return None
        skills = tuple(
            self._skills[sid] for sid in skill_ids if sid in self._skills
        )
        if not skills:
            return None
        slot = SpellSlot(max_cost=_SKILL_BAR_BUDGET, skills=skills)
        return SkillBar(slots=(slot,))


def _build_attributes(attr_map: dict[AttributeType, int]) -> Attributes:
    attrs = Attributes()
    for attr_type, value in attr_map.items():
        attrs.set(attr_type, value)
    return attrs
