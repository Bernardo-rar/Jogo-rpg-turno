"""Roda combate interativo com Pygame — first playable."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.battle_setup import (  # noqa: E402
    CLERIC_MODS,
    EMPTY_THRESHOLDS,
    FIGHTER_MODS,
    ORC_MODS,
    SORCERER_MODS,
    _attrs,
    _make_inventory,
    _make_skill_bar,
)

from src.core.characters.character import Character  # noqa: E402
from src.core.characters.character_config import CharacterConfig  # noqa: E402
from src.core.characters.position import Position  # noqa: E402
from src.core.items.accessory_loader import load_accessories  # noqa: E402
from src.core.items.armor_loader import load_armors  # noqa: E402
from src.core.items.weapon_loader import load_weapons  # noqa: E402
import pygame  # noqa: E402

from src.ui.font_manager import FontManager  # noqa: E402
from src.ui.game import Game  # noqa: E402
from src.ui.scenes.interactive_combat_factory import create_interactive_combat  # noqa: E402
from src.ui.scenes.playable_combat_scene import PlayableCombatScene  # noqa: E402


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
