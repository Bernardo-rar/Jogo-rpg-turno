"""Roda Mock Battle v2 com visualizacao Pygame."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.battle_setup import create_battle
from src.ui.font_manager import FontManager
from src.ui.game import Game
from src.ui.replay.battle_recorder import BattleRecorder
from src.ui.scenes.combat_scene import CombatScene


def main():
    import pygame
    pygame.init()

    engine, party, enemies = create_battle()
    recorder = BattleRecorder(engine, party, enemies)
    replay = recorder.record()

    fonts = FontManager()
    scene = CombatScene(replay, fonts)
    game = Game(scene)
    game.run()


if __name__ == "__main__":
    main()
