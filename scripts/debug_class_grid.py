"""Grid 4x4 de debug: mostra as 13 classes com recursos e skills."""

from __future__ import annotations

import sys

import pygame

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes
from src.core.attributes.threshold_calculator import ThresholdCalculator
from src.core.characters.character_config import CharacterConfig
from src.core.characters.class_modifiers import ClassModifiers
from src.core.classes.class_id import ClassId
from src.core.classes.artificer.artificer import Artificer
from src.core.classes.barbarian.barbarian import Barbarian
from src.core.classes.bard.bard import Bard
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
from src.core.skills.skill_loader import load_class_skills
from src.ui.components.character_card import draw_character_card
from src.ui.font_manager import FontManager
from src.ui.replay.battle_snapshot import snapshot_character
from src.ui import colors

# --- Layout constants ---
GRID_COLS = 4
GRID_ROWS = 4
CELL_WIDTH = 380
CELL_HEIGHT = 240
MARGIN_X = 20
MARGIN_Y = 20
TITLE_HEIGHT = 20
SKILL_LINE_HEIGHT = 15
SKILL_OFFSET_X = 175
SKILL_START_Y = 25

WINDOW_W = MARGIN_X + GRID_COLS * CELL_WIDTH + MARGIN_X
WINDOW_H = MARGIN_Y + GRID_ROWS * CELL_HEIGHT + MARGIN_Y

EMPTY_THRESHOLDS = ThresholdCalculator({})

# Map ClassId -> constructor class
_CLASS_MAP = {
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

# Nomes tematicos por classe
_CLASS_NAMES = {
    ClassId.FIGHTER: "Gareth",
    ClassId.BARBARIAN: "Throk",
    ClassId.MAGE: "Lyra",
    ClassId.CLERIC: "Aurelia",
    ClassId.PALADIN: "Roland",
    ClassId.RANGER: "Kael",
    ClassId.MONK: "Zhen",
    ClassId.SORCERER: "Nyx",
    ClassId.WARLOCK: "Vex",
    ClassId.DRUID: "Fern",
    ClassId.ROGUE: "Shadow",
    ClassId.BARD: "Melody",
    ClassId.ARTIFICER: "Cogsworth",
}


def _make_attrs(primary_high: int = 12, others: int = 8) -> Attributes:
    """Cria atributos com valores razoaveis."""
    return Attributes({at: others for at in AttributeType})


def _build_class_instance(class_id: ClassId):
    """Instancia uma classe real com modifiers do JSON."""
    cls = _CLASS_MAP[class_id]
    mods = ClassModifiers.from_json(f"data/classes/{class_id.value}.json")
    attrs = _make_attrs()
    config = CharacterConfig(
        class_modifiers=mods,
        threshold_calculator=EMPTY_THRESHOLDS,
    )
    name = _CLASS_NAMES.get(class_id, class_id.value.title())
    return cls(name, attrs, config)


def _draw_class_title(
    surface: pygame.Surface,
    class_id: ClassId,
    x: int, y: int,
    font: pygame.font.Font,
) -> None:
    """Titulo da classe acima do card."""
    label = class_id.value.upper()
    rendered = font.render(label, True, colors.TEXT_YELLOW)
    surface.blit(rendered, (x, y))


def _draw_skills_list(
    surface: pygame.Surface,
    class_id: ClassId,
    x: int, y: int,
    font: pygame.font.Font,
) -> None:
    """Lista as 6 skills da classe ao lado do card."""
    skills = load_class_skills(class_id.value)
    for i, (skill_id, skill) in enumerate(skills.items()):
        action = skill.action_type.name[:3]
        cost_parts = []
        if skill.mana_cost > 0:
            cost_parts.append(f"{skill.mana_cost}mp")
        for rc in skill.resource_costs:
            cost_parts.append(f"{rc.amount} {rc.resource_type[:6]}")
        cost_str = " ".join(cost_parts) if cost_parts else "free"
        label = f"[{action}] {skill_id}"
        color = colors.TEXT_WHITE
        if skill.action_type.name == "REACTION":
            color = colors.TEXT_EFFECT
        elif skill.action_type.name == "BONUS_ACTION":
            color = colors.TEXT_YELLOW
        rendered = font.render(label, True, color)
        surface.blit(rendered, (x, y + i * SKILL_LINE_HEIGHT))
        cost_rendered = font.render(cost_str, True, colors.TEXT_MUTED)
        surface.blit(cost_rendered, (x + 155, y + i * SKILL_LINE_HEIGHT))


def main() -> None:
    pygame.init()
    surface = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    pygame.display.set_caption("Debug: 13 Classes Grid")
    clock = pygame.time.Clock()
    fonts = FontManager()
    tiny = pygame.font.SysFont("consolas", 12)

    # Pre-build all instances + snapshots
    class_ids = list(ClassId)
    instances = {}
    for cid in class_ids:
        try:
            instances[cid] = _build_class_instance(cid)
        except Exception as e:
            print(f"ERRO ao instanciar {cid.value}: {e}")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        surface.fill(colors.BG_DARK)

        for idx, cid in enumerate(class_ids):
            col = idx % GRID_COLS
            row = idx // GRID_COLS
            cx = MARGIN_X + col * CELL_WIDTH
            cy = MARGIN_Y + row * CELL_HEIGHT

            # Cell background
            cell_rect = pygame.Rect(
                cx - 5, cy - 5,
                CELL_WIDTH - 10, CELL_HEIGHT - 10,
            )
            pygame.draw.rect(surface, colors.BG_PANEL, cell_rect, border_radius=4)
            pygame.draw.rect(
                surface, colors.BG_PANEL_BORDER, cell_rect, 1, 4,
            )

            # Class title
            _draw_class_title(surface, cid, cx, cy, fonts.medium)

            if cid in instances:
                char = instances[cid]
                snap = snapshot_character(char, is_party=True)
                # Character card
                draw_character_card(
                    surface, snap,
                    cx, cy + TITLE_HEIGHT,
                    fonts,
                )
                # Skills list (to the right of card)
                _draw_skills_list(
                    surface, cid,
                    cx + SKILL_OFFSET_X,
                    cy + SKILL_START_Y,
                    tiny,
                )
            else:
                err = fonts.small.render("ERRO", True, colors.TEXT_DAMAGE)
                surface.blit(err, (cx + 10, cy + 40))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
