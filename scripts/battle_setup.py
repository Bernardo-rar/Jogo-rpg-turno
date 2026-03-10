"""Setup compartilhado para Mock Battle v2."""

from __future__ import annotations

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_modifiers import ClassModifiers
from src.core.characters.position import Position
from src.core.combat.basic_attack_handler import BasicAttackHandler
from src.core.combat.combat_engine import CombatEngine
from src.core.combat.composite_handler import CompositeHandler
from src.core.combat.consumable_handler import ConsumableHandler
from src.core.combat.dispatch_handler import DispatchTurnHandler
from src.core.combat.skill_handler import SkillHandler
from src.core.elements.elemental_profile import load_profiles
from src.core.items.accessory_loader import load_accessories
from src.core.items.armor_loader import load_armors
from src.core.items.consumable_loader import load_consumables
from src.core.items.inventory import Inventory
from src.core.items.weapon_loader import load_weapons
from src.core.skills.skill_bar import SkillBar
from src.core.skills.skill_loader import load_skills
from src.core.skills.spell_slot import SpellSlot

EMPTY_THRESHOLDS = ThresholdCalculator({})

FIGHTER_MODS = ClassModifiers(
    hit_dice=12, vida_mod=0, mod_hp=10, mana_multiplier=6,
    mod_atk_physical=10, mod_atk_magical=6, mod_def_physical=5,
    mod_def_magical=3, regen_hp_mod=5, regen_mana_mod=3,
)
RANGER_MODS = ClassModifiers(
    hit_dice=10, vida_mod=0, mod_hp=8, mana_multiplier=7,
    mod_atk_physical=8, mod_atk_magical=6, mod_def_physical=3,
    mod_def_magical=3, regen_hp_mod=3, regen_mana_mod=3,
)
CLERIC_MODS = ClassModifiers(
    hit_dice=8, vida_mod=0, mod_hp=8, mana_multiplier=8,
    mod_atk_physical=5, mod_atk_magical=8, mod_def_physical=3,
    mod_def_magical=4, regen_hp_mod=3, regen_mana_mod=4,
)
SORCERER_MODS = ClassModifiers(
    hit_dice=6, vida_mod=0, mod_hp=6, mana_multiplier=12,
    mod_atk_physical=4, mod_atk_magical=10, mod_def_physical=2,
    mod_def_magical=5, regen_hp_mod=2, regen_mana_mod=5,
)
ORC_MODS = ClassModifiers(
    hit_dice=10, vida_mod=0, mod_hp=8, mana_multiplier=5,
    mod_atk_physical=8, mod_atk_magical=4, mod_def_physical=4,
    mod_def_magical=3, regen_hp_mod=3, regen_mana_mod=2,
)
SHAMAN_MODS = ClassModifiers(
    hit_dice=6, vida_mod=0, mod_hp=5, mana_multiplier=10,
    mod_atk_physical=4, mod_atk_magical=8, mod_def_physical=2,
    mod_def_magical=4, regen_hp_mod=2, regen_mana_mod=4,
)


def _attrs(s, d, c, i, w, ch, m):
    return Attributes({
        AttributeType.STRENGTH: s, AttributeType.DEXTERITY: d,
        AttributeType.CONSTITUTION: c, AttributeType.INTELLIGENCE: i,
        AttributeType.WISDOM: w, AttributeType.CHARISMA: ch,
        AttributeType.MIND: m,
    })


def _make_skill_bar(skill_ids):
    all_skills = load_skills()
    skills = tuple(all_skills[sid] for sid in skill_ids)
    total_cost = sum(s.slot_cost for s in skills)
    slot = SpellSlot(max_cost=total_cost + 10, skills=skills)
    return SkillBar(slots=(slot,))


def _make_inventory(item_quantities):
    all_consumables = load_consumables()
    inv = Inventory()
    for cid, qty in item_quantities.items():
        inv.add_item(all_consumables[cid], quantity=qty)
    return inv


def create_battle():
    """Cria party, enemies, handler e engine. Retorna (engine, party, enemies)."""
    weapons = load_weapons()
    armors = load_armors()
    accessories = load_accessories()
    profiles = load_profiles()

    party = _create_party(weapons, armors, accessories)
    enemies = _create_enemies(weapons, profiles)
    handler = _create_handler()

    engine = CombatEngine(party, enemies, handler)
    return engine, party, enemies


def _create_party(weapons, armors, accessories):
    gareth = Character(
        name="Gareth", attributes=_attrs(8, 6, 7, 3, 4, 3, 3),
        config=CharacterConfig(
            class_modifiers=FIGHTER_MODS, threshold_calculator=EMPTY_THRESHOLDS,
            weapon=weapons["longsword"], armor=armors["chain_mail"],
            accessories=(accessories["iron_ring"],),
            inventory=_make_inventory({"health_potion_small": 2}),
        ),
    )
    kael = Character(
        name="Kael", attributes=_attrs(5, 8, 5, 5, 6, 4, 5),
        config=CharacterConfig(
            class_modifiers=RANGER_MODS, threshold_calculator=EMPTY_THRESHOLDS,
            position=Position.BACK, weapon=weapons["longbow"],
            armor=armors["studded_leather"],
            accessories=(accessories["cloak_of_speed"],),
            skill_bar=_make_skill_bar(["poison_strike"]),
        ),
    )
    aurelia = Character(
        name="Aurelia", attributes=_attrs(3, 5, 5, 9, 8, 6, 9),
        config=CharacterConfig(
            class_modifiers=CLERIC_MODS, threshold_calculator=EMPTY_THRESHOLDS,
            position=Position.BACK, weapon=weapons["mace"],
            armor=armors["scale_mail"],
            accessories=(accessories["amulet_of_wisdom"],),
            skill_bar=_make_skill_bar(["minor_heal"]),
            inventory=_make_inventory({"antidote": 2}),
        ),
    )
    lyra = Character(
        name="Lyra", attributes=_attrs(3, 5, 5, 9, 8, 6, 9),
        config=CharacterConfig(
            class_modifiers=SORCERER_MODS, threshold_calculator=EMPTY_THRESHOLDS,
            position=Position.BACK, armor=armors["mage_robes"],
            skill_bar=_make_skill_bar(["fireball", "ice_bolt"]),
            inventory=_make_inventory({"mana_potion_small": 2}),
        ),
    )
    return [gareth, kael, aurelia, lyra]


def _create_enemies(weapons, profiles):
    orc_0 = Character(
        name="Orc_0", attributes=_attrs(7, 5, 7, 3, 4, 3, 3),
        config=CharacterConfig(
            class_modifiers=ORC_MODS, threshold_calculator=EMPTY_THRESHOLDS,
            weapon=weapons["greatsword"],
            inventory=_make_inventory({"health_potion_small": 1}),
        ),
    )
    orc_1 = Character(
        name="Orc_1", attributes=_attrs(7, 5, 7, 3, 4, 3, 3),
        config=CharacterConfig(
            class_modifiers=ORC_MODS, threshold_calculator=EMPTY_THRESHOLDS,
            weapon=weapons["longsword"],
            skill_bar=_make_skill_bar(["weaken"]),
        ),
    )
    shaman = Character(
        name="Shaman", attributes=_attrs(3, 5, 5, 9, 8, 6, 9),
        config=CharacterConfig(
            class_modifiers=SHAMAN_MODS, threshold_calculator=EMPTY_THRESHOLDS,
            position=Position.BACK, weapon=weapons["dagger"],
            elemental_profile=profiles["fire_creature"],
            skill_bar=_make_skill_bar(["fireball"]),
        ),
    )
    return [orc_0, orc_1, shaman]


def _create_handler():
    skill_h = SkillHandler()
    consumable_h = ConsumableHandler()
    basic_h = BasicAttackHandler()
    return DispatchTurnHandler(
        {
            "Gareth": CompositeHandler((consumable_h, basic_h)),
            "Kael": CompositeHandler((skill_h, basic_h)),
            "Aurelia": CompositeHandler((skill_h, consumable_h, basic_h)),
            "Lyra": CompositeHandler((skill_h, consumable_h, basic_h)),
            "Orc_0": CompositeHandler((consumable_h, basic_h)),
            "Orc_1": CompositeHandler((skill_h, basic_h)),
            "Shaman": CompositeHandler((skill_h, basic_h)),
        },
        basic_h,
    )
