"""Captura um frame do combate interativo e salva como PNG."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pygame

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_modifiers import ClassModifiers
from src.core.characters.position import Position
from src.core.items.armor_loader import load_armors
from src.core.items.weapon_loader import load_weapons
from src.core.skills.skill_bar import SkillBar
from src.core.skills.skill_loader import load_skills
from src.core.skills.spell_slot import SpellSlot
from src.ui import layout
from src.ui.font_manager import FontManager
from src.ui.scenes.interactive_combat_factory import create_interactive_combat
from src.ui.scenes.playable_combat_scene import PlayableCombatScene

EMPTY_THRESHOLDS = ThresholdCalculator({})
FIGHTER_MODS = ClassModifiers(
    hit_dice=12, vida_mod=0, mod_hp=10, mana_multiplier=6,
    mod_atk_physical=10, mod_atk_magical=6, mod_def_physical=5,
    mod_def_magical=3, regen_hp_mod=5, regen_mana_mod=3,
)
ORC_MODS = ClassModifiers(
    hit_dice=10, vida_mod=0, mod_hp=8, mana_multiplier=5,
    mod_atk_physical=8, mod_atk_magical=4, mod_def_physical=4,
    mod_def_magical=3, regen_hp_mod=3, regen_mana_mod=2,
)
SORCERER_MODS = ClassModifiers(
    hit_dice=6, vida_mod=0, mod_hp=6, mana_multiplier=12,
    mod_atk_physical=4, mod_atk_magical=10, mod_def_physical=2,
    mod_def_magical=5, regen_hp_mod=2, regen_mana_mod=5,
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


def main():
    weapons = load_weapons()
    armors = load_armors()

    gareth = Character(
        name="Gareth", attributes=_attrs(8, 6, 7, 3, 4, 3, 3),
        config=CharacterConfig(
            class_modifiers=FIGHTER_MODS,
            threshold_calculator=EMPTY_THRESHOLDS,
            weapon=weapons["longsword"], armor=armors["chain_mail"],
        ),
    )
    lyra = Character(
        name="Lyra", attributes=_attrs(3, 5, 5, 9, 8, 6, 9),
        config=CharacterConfig(
            class_modifiers=SORCERER_MODS,
            threshold_calculator=EMPTY_THRESHOLDS,
            position=Position.BACK, armor=armors["mage_robes"],
            skill_bar=_make_skill_bar(["fireball", "ice_bolt"]),
        ),
    )
    orc = Character(
        name="Orc", attributes=_attrs(7, 5, 7, 3, 4, 3, 3),
        config=CharacterConfig(
            class_modifiers=ORC_MODS,
            threshold_calculator=EMPTY_THRESHOLDS,
            weapon=weapons["greatsword"],
        ),
    )

    party = [gareth, lyra]
    enemies = [orc]

    pygame.init()
    surface = pygame.display.set_mode(
        (layout.WINDOW_WIDTH, layout.WINDOW_HEIGHT),
    )
    fonts = FontManager()
    interactive = create_interactive_combat(party, enemies)
    playable = PlayableCombatScene(interactive, party, enemies, fonts)

    # Update para chegar em WAITING_INPUT
    playable.update(16)
    playable.draw(surface)

    Path("debug/screenshots").mkdir(parents=True, exist_ok=True)
    pygame.image.save(surface, "debug/screenshots/first_playable.png")
    print("Screenshot salvo em debug/screenshots/first_playable.png")
    pygame.quit()


if __name__ == "__main__":
    main()
