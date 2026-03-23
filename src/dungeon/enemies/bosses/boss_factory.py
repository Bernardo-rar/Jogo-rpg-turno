"""BossFactory — cria Character + PhaseHandler para bosses."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.combat.basic_attack_handler import BasicAttackHandler
from src.core.elements.elemental_profile import ElementalProfile
from src.core.items.weapon import Weapon
from src.core.skills.skill import Skill
from src.core.skills.skill_bar import SkillBar
from src.core.skills.spell_slot import SpellSlot
from src.dungeon.enemies.bosses.boss_template import BossTemplate
from src.dungeon.enemies.bosses.phase_handler import PhaseHandler

if TYPE_CHECKING:
    from src.core.combat.combat_engine import TurnHandler

_EMPTY_THRESHOLDS = ThresholdCalculator({})
_BOSS_SKILL_BUDGET = 200

_HANDLER_REGISTRY: dict[str, type] = {}


def register_phase_handler(key: str, handler_cls: type) -> None:
    """Registra handler de fase de boss pelo handler_key."""
    _HANDLER_REGISTRY[key] = handler_cls


def _get_phase_handler(key: str) -> TurnHandler:
    cls = _HANDLER_REGISTRY.get(key)
    if cls is None:
        return BasicAttackHandler()
    return cls()


@dataclass(frozen=True)
class BossResult:
    """Resultado de criar um boss: Character + handler."""

    character: Character
    handler: TurnHandler


class BossFactory:
    """Cria boss Characters com PhaseHandler montado."""

    def __init__(
        self,
        weapon_catalog: dict[str, Weapon],
        profile_catalog: dict[str, ElementalProfile],
        skill_catalog: dict[str, Skill],
    ) -> None:
        self._weapons = weapon_catalog
        self._profiles = profile_catalog
        self._skills = skill_catalog

    def create(self, template: BossTemplate) -> BossResult:
        """Cria Character + PhaseHandler a partir de BossTemplate."""
        attrs = _build_attributes(template.base_attributes)
        skill_bar = self._build_skill_bar(template.all_skill_ids())
        config = CharacterConfig(
            class_modifiers=template.class_modifiers,
            threshold_calculator=_EMPTY_THRESHOLDS,
            position=template.position,
            weapon=self._weapons.get(template.weapon_id),
            elemental_profile=self._profiles.get(
                template.elemental_profile_id,
            ),
            skill_bar=skill_bar,
        )
        character = Character(template.name, attrs, config)
        handler = self._build_phase_handler(template)
        return BossResult(character=character, handler=handler)

    def _build_skill_bar(
        self,
        skill_ids: tuple[str, ...],
    ) -> SkillBar | None:
        if not skill_ids:
            return None
        skills = tuple(
            self._skills[sid]
            for sid in skill_ids
            if sid in self._skills
        )
        if not skills:
            return None
        slot = SpellSlot(max_cost=_BOSS_SKILL_BUDGET, skills=skills)
        return SkillBar(slots=(slot,))

    def _build_phase_handler(
        self,
        template: BossTemplate,
    ) -> PhaseHandler:
        phases = tuple(pc.phase for pc in template.phases)
        phase_handlers = {
            pc.phase.handler_key: _get_phase_handler(
                pc.phase.handler_key,
            )
            for pc in template.phases
        }
        return PhaseHandler(
            phases=phases,
            phase_handlers=phase_handlers,
            default_handler=BasicAttackHandler(),
        )


def _build_attributes(attr_map: dict[AttributeType, int]) -> Attributes:
    attrs = Attributes()
    for attr_type, value in attr_map.items():
        attrs.set(attr_type, value)
    return attrs
