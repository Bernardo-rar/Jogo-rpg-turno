"""Quick test: does AI actually deal damage?"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.combat.player_action import PlayerAction, PlayerActionType
from src.ui.scenes.interactive_combat import TurnPhase
from src.ui.scenes.interactive_combat_factory import create_interactive_combat
from scripts.play_interactive import (
    _attrs, _make_skill_bar, _make_inventory,
    FIGHTER_MODS, SORCERER_MODS, ORC_MODS, EMPTY_THRESHOLDS,
)
from src.core.characters.character import Character
from src.core.characters.character_config import CharacterConfig
from src.core.characters.position import Position
from src.core.items.weapon_loader import load_weapons
from src.core.items.armor_loader import load_armors

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
orc = Character(
    name="Orc_0", attributes=_attrs(7, 5, 7, 3, 4, 3, 3),
    config=CharacterConfig(
        class_modifiers=ORC_MODS,
        threshold_calculator=EMPTY_THRESHOLDS,
        weapon=weapons["greatsword"],
    ),
)

party = [gareth]
enemies = [orc]

scene = create_interactive_combat(party, enemies)

print(f"Gareth HP before: {gareth.current_hp}/{gareth.max_hp}")
print(f"Orc HP before: {orc.current_hp}/{orc.max_hp}")
print(f"Gareth position: {gareth.position}")
print(f"Orc position: {orc.position}")

# Round 1: advance to first WAITING_INPUT
scene.update(16)
print(f"\nPhase: {scene.phase}, Active: {scene.active_combatant}")
print(f"Gareth HP after AI turns: {gareth.current_hp}/{gareth.max_hp}")

# Player does end turn
scene.submit_player_action(PlayerAction(action_type=PlayerActionType.END_TURN))
scene.update(16)
print(f"\nPhase: {scene.phase}, Active: {scene.active_combatant}")
print(f"Gareth HP after full round: {gareth.current_hp}/{gareth.max_hp}")
print(f"Orc HP: {orc.current_hp}/{orc.max_hp}")

# Check engine events
events = scene._engine.events
print(f"\nTotal events: {len(events)}")
for e in events:
    print(f"  {e.actor_name} -> {e.target_name}: type={e.event_type}, dmg={e.damage}")
