"""PartyFactory — cria Characters jogáveis a partir de ClassId."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from src.core._paths import resolve_data_path
from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_modifiers import ClassModifiers
from src.core.characters.position import Position
from src.core.items.inventory import Inventory
from src.core.skills.skill_bar import SkillBar
from src.core.skills.skill_loader import load_class_skills
from src.core.skills.spell_slot import SpellSlot
from src.core.classes.artificer.artificer import Artificer
from src.core.classes.barbarian.barbarian import Barbarian
from src.core.classes.bard.bard import Bard
from src.core.classes.class_id import ClassId
from src.core.classes.cleric.cleric import Cleric
from src.core.classes.druid.druid import Druid
from src.core.classes.fighter.fighter import Fighter
from src.core.classes.mage.mage import Mage
from src.core.classes.monk.monk import Monk
from src.core.classes.paladin.paladin import Paladin
from src.core.classes.ranger.ranger import Ranger
from src.core.classes.rogue.rogue import Rogue
from src.core.classes.sorcerer.sorcerer import Sorcerer
from src.core.classes.warlock.warlock import Warlock

if TYPE_CHECKING:
    from src.core.items.accessory import Accessory
    from src.core.items.armor import Armor
    from src.core.items.weapon import Weapon

_DEFAULTS_FILE = "data/dungeon/party_defaults.json"
_EMPTY_THRESHOLDS = ThresholdCalculator({})
_SKILL_BAR_BUDGET = 100

_CLASS_MAP: dict[ClassId, type[Character]] = {
    ClassId.FIGHTER: Fighter,
    ClassId.BARBARIAN: Barbarian,
    ClassId.MAGE: Mage,
    ClassId.CLERIC: Cleric,
    ClassId.PALADIN: Paladin,
    ClassId.RANGER: Ranger,
    ClassId.MONK: Monk,
    ClassId.SORCERER: Sorcerer,
    ClassId.WARLOCK: Warlock,
    ClassId.DRUID: Druid,
    ClassId.ROGUE: Rogue,
    ClassId.BARD: Bard,
    ClassId.ARTIFICER: Artificer,
}

_FRONT_CLASSES = {
    ClassId.FIGHTER, ClassId.BARBARIAN, ClassId.PALADIN, ClassId.MONK,
}


def is_frontliner(class_id: ClassId) -> bool:
    """Retorna True se a classe é naturalmente front-liner."""
    return class_id in _FRONT_CLASSES


class PartyFactory:
    """Cria Characters jogáveis a partir de ClassId + defaults."""

    def __init__(
        self,
        weapon_catalog: dict[str, Weapon],
        armor_catalog: dict[str, Armor] | None = None,
        accessory_catalog: dict[str, Accessory] | None = None,
    ) -> None:
        self._weapons = weapon_catalog
        self._armors = armor_catalog or {}
        self._accessories = accessory_catalog or {}
        self._defaults = _load_defaults()

    def create(self, class_id: ClassId, name: str) -> Character:
        """Cria Character da classe com defaults de arma/atributos/skills."""
        cls = _CLASS_MAP[class_id]
        defaults = self._defaults[class_id.value]
        attrs = _build_attributes(defaults["attrs"])
        mods = ClassModifiers.from_json(
            f"data/classes/{class_id.value}.json",
        )
        config = self._build_config(defaults, mods, class_id)
        return cls(name, attrs, config)

    def _build_config(
        self,
        defaults: dict,
        mods: ClassModifiers,
        class_id: ClassId,
    ) -> CharacterConfig:
        """Monta CharacterConfig a partir dos defaults."""
        return CharacterConfig(
            class_modifiers=mods,
            threshold_calculator=_EMPTY_THRESHOLDS,
            position=Position[defaults["position"]],
            weapon=self._weapons.get(defaults["weapon"]),
            armor=_resolve_armor(defaults, self._armors),
            accessories=_resolve_accessories(defaults, self._accessories),
            skill_bar=_build_skill_bar(class_id),
            inventory=Inventory(),
        )


def _build_skill_bar(class_id: ClassId) -> SkillBar | None:
    """Carrega skills da classe e monta SkillBar."""
    skills_dict = load_class_skills(class_id.value)
    if not skills_dict:
        return None
    skills = tuple(skills_dict.values())
    total_cost = sum(s.slot_cost for s in skills)
    budget = max(total_cost + 10, _SKILL_BAR_BUDGET)
    slot = SpellSlot(max_cost=budget, skills=skills)
    return SkillBar(slots=(slot,))


def _load_defaults() -> dict[str, dict]:
    path = resolve_data_path(_DEFAULTS_FILE)
    return json.loads(path.read_text(encoding="utf-8"))


def _build_attributes(attr_list: list[int]) -> Attributes:
    attrs = Attributes()
    for attr_type, value in zip(AttributeType, attr_list):
        attrs.set(attr_type, value)
    return attrs


def _resolve_armor(
    defaults: dict,
    catalog: dict[str, Armor],
) -> Armor | None:
    """Busca armor no catalogo pelo id do JSON. None se ausente."""
    armor_id = defaults.get("armor")
    if armor_id is None:
        return None
    return catalog.get(armor_id)


def _resolve_accessories(
    defaults: dict,
    catalog: dict[str, Accessory],
) -> tuple[Accessory, ...]:
    """Busca accessories no catalogo pelos ids do JSON."""
    ids: list[str] = defaults.get("accessories", [])
    resolved = [catalog[a] for a in ids if a in catalog]
    return tuple(resolved)
