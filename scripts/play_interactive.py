"""Roda combate interativo com Pygame — first playable."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_modifiers import ClassModifiers
from src.core.characters.position import Position
from src.core.items.accessory_loader import load_accessories
from src.core.items.armor_loader import load_armors
from src.core.items.consumable_loader import load_consumables
from src.core.items.inventory import Inventory
from src.core.items.weapon_loader import load_weapons
from src.core.skills.skill_bar import SkillBar
from src.core.skills.skill_loader import load_skills
from src.core.skills.spell_slot import SpellSlot
import pygame

from src.ui.font_manager import FontManager
from src.ui.game import Game
from src.ui.scenes.interactive_combat_factory import create_interactive_combat
from src.ui.scenes.playable_combat_scene import PlayableCombatScene

EMPTY_THRESHOLDS = ThresholdCalculator({})

FIGHTER_MODS = ClassModifiers(
    hit_dice=12, vida_mod=0, mod_hp=10, mana_multiplier=6,
    mod_atk_physical=10, mod_atk_magical=6, mod_def_physical=5,
    mod_def_magical=3, regen_hp_mod=5, regen_mana_mod=3,
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


def main():
    weapons = load_weapons()
    armors = load_armors()
    accessories = load_accessories()

    # Party (jogador controla)
    gareth = Character(
        name="Gareth", attributes=_attrs(8, 6, 7, 3, 4, 3, 3),
        config=CharacterConfig(
            class_modifiers=FIGHTER_MODS,
            threshold_calculator=EMPTY_THRESHOLDS,
            weapon=weapons["longsword"], armor=armors["chain_mail"],
            accessories=(accessories["iron_ring"],),
            inventory=_make_inventory({"health_potion_small": 2}),
        ),
    )
    aurelia = Character(
        name="Aurelia", attributes=_attrs(3, 5, 5, 9, 8, 6, 9),
        config=CharacterConfig(
            class_modifiers=CLERIC_MODS,
            threshold_calculator=EMPTY_THRESHOLDS,
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
            class_modifiers=SORCERER_MODS,
            threshold_calculator=EMPTY_THRESHOLDS,
            position=Position.BACK, armor=armors["mage_robes"],
            skill_bar=_make_skill_bar(["fireball", "ice_bolt"]),
            inventory=_make_inventory({"mana_potion_small": 2}),
        ),
    )

    # Inimigos (IA controla)
    orc_0 = Character(
        name="Orc_0", attributes=_attrs(7, 5, 7, 3, 4, 3, 3),
        config=CharacterConfig(
            class_modifiers=ORC_MODS,
            threshold_calculator=EMPTY_THRESHOLDS,
            weapon=weapons["greatsword"],
            inventory=_make_inventory({"health_potion_small": 1}),
        ),
    )
    orc_1 = Character(
        name="Orc_1", attributes=_attrs(7, 5, 7, 3, 4, 3, 3),
        config=CharacterConfig(
            class_modifiers=ORC_MODS,
            threshold_calculator=EMPTY_THRESHOLDS,
            weapon=weapons["longsword"],
        ),
    )

    party = [gareth, aurelia, lyra]
    enemies = [orc_0, orc_1]

    interactive = create_interactive_combat(party, enemies)
    pygame.init()
    fonts = FontManager()
    playable = PlayableCombatScene(interactive, party, enemies, fonts)
    game = Game(playable)  # Game.__init__ chama pygame.init() de novo (safe)
    game.run()


if __name__ == "__main__":
    main()
