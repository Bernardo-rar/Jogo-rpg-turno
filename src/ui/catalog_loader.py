"""Catalog loading — carrega e merge catalogs de items/enemies."""

from __future__ import annotations

import json

from src.core._paths import resolve_data_path
from src.core.combat.basic_attack_handler import BasicAttackHandler
from src.core.combat.composite_handler import CompositeHandler
from src.core.combat.skill_effect_applier import set_combo_detector
from src.core.combat.skill_handler import SkillHandler
from src.core.elements.combo.combo_config import load_combo_configs
from src.core.elements.combo.combo_detector import ComboDetector
from src.core.elements.element_type import ElementType
from src.core.elements.elemental_profile import ElementalProfile, load_profiles
from src.core.items.accessory_loader import load_accessories
from src.core.items.armor_loader import load_armors
from src.core.items.consumable_loader import load_consumables
from src.core.items.weapon import Weapon
from src.core.items.weapon_loader import load_weapons
from src.core.skills.skill import Skill
from src.core.skills.skill_loader import load_skills
from src.dungeon.encounters.encounter_factory import EncounterFactory
from src.dungeon.enemies.bosses.boss_factory import BossFactory
from src.dungeon.enemies.elite_modifier import load_elite_bonuses
from src.dungeon.enemies.enemy_factory import EnemyFactory
from src.dungeon.enemies.enemy_template_loader import load_tier_templates
from src.dungeon.run.encounter_builder import EncounterBuilder
from src.dungeon.run.equipment_catalog import EquipmentCatalogs
from src.dungeon.run.party_factory import PartyFactory


def load_app_catalogs() -> AppCatalogs:
    """Carrega todos os catalogs necessarios para o RunApp."""
    weapons = load_weapons()
    armors = load_armors()
    accessories = load_accessories()
    consumables = load_consumables()
    party_factory = PartyFactory(weapons, armors, accessories)
    equipment = EquipmentCatalogs(
        weapons=weapons, armors=armors, accessories=accessories,
    )
    enc_factory = _build_encounter_factory()
    boss_factory = _build_boss_factory()
    encounter_builder = EncounterBuilder(enc_factory, boss_factory)
    _init_combo_detector()
    return AppCatalogs(
        consumables=consumables,
        party_factory=party_factory,
        equipment=equipment,
        encounter_builder=encounter_builder,
    )


class AppCatalogs:
    """Container para catalogs carregados no init."""

    def __init__(
        self,
        consumables: dict,
        party_factory: PartyFactory,
        equipment: EquipmentCatalogs,
        encounter_builder: EncounterBuilder,
    ) -> None:
        self.consumables = consumables
        self.party_factory = party_factory
        self.equipment = equipment
        self.encounter_builder = encounter_builder


def _load_dungeon_weapons() -> dict[str, Weapon]:
    """Carrega armas do dungeon e merge com core."""
    core = load_weapons()
    raw = json.loads(
        resolve_data_path("data/dungeon/enemies/weapons.json")
        .read_text(encoding="utf-8"),
    )
    dungeon = {k: Weapon.from_dict(v) for k, v in raw.items()}
    return {**core, **dungeon}


def _load_dungeon_profiles() -> dict[str, ElementalProfile]:
    """Carrega perfis elementais do dungeon e merge com core."""
    core = load_profiles()
    raw = json.loads(
        resolve_data_path(
            "data/dungeon/enemies/elemental_profiles.json",
        ).read_text(encoding="utf-8"),
    )
    dungeon = {
        name: ElementalProfile(
            resistances={ElementType[k]: v for k, v in r.items()},
        )
        for name, r in raw.items()
    }
    return {**core, **dungeon}


def _load_extra_skills(
    extra_paths: list[str],
) -> dict[str, Skill]:
    """Carrega skills extras de arquivos JSON."""
    core = load_skills()
    extra: dict[str, Skill] = {}
    for path in extra_paths:
        raw = json.loads(
            resolve_data_path(path).read_text(encoding="utf-8"),
        )
        extra.update(
            {sid: Skill.from_dict(sid, d) for sid, d in raw.items()},
        )
    return {**core, **extra}


def _load_dungeon_catalogs(
    extra_skill_files: list[str],
) -> tuple[dict[str, Weapon], dict[str, ElementalProfile], dict[str, Skill]]:
    """Load weapons, profiles, and skills for factories."""
    weapons = _load_dungeon_weapons()
    profiles = _load_dungeon_profiles()
    skills = _load_extra_skills(extra_skill_files)
    return weapons, profiles, skills


def _build_encounter_factory() -> EncounterFactory:
    weapons, profiles, skills = _load_dungeon_catalogs([
        "data/dungeon/enemies/skills/tier1_skills.json",
        "data/dungeon/enemies/skills/elite_skills.json",
    ])
    enemy_factory = EnemyFactory(weapons, profiles, skills)
    elite_bonuses = load_elite_bonuses()
    return EncounterFactory(
        enemy_factory, load_tier_templates(tier=1),
        elite_bonuses=elite_bonuses,
    )


def _build_boss_factory() -> BossFactory:
    weapons, profiles, skills = _load_dungeon_catalogs([
        "data/dungeon/enemies/skills/boss_skills.json",
    ])
    return BossFactory(weapons, profiles, skills)


def _init_combo_detector() -> None:
    """Carrega combos elementais e configura detector global."""
    combos = load_combo_configs()
    detector = ComboDetector(combos=combos)
    set_combo_detector(detector)
