"""Factory para criar InteractiveCombatScene pronta para jogar."""

from __future__ import annotations

from src.core.characters.character import Character
from src.core.combat.basic_attack_handler import BasicAttackHandler
from src.core.combat.combat_engine import CombatEngine, TurnHandler
from src.core.combat.composite_handler import CompositeHandler
from src.core.combat.consumable_handler import ConsumableHandler
from src.core.combat.skill_handler import SkillHandler
from src.ui.scenes.interactive_combat import InteractiveCombatScene


def create_interactive_combat(
    party: list[Character],
    enemies: list[Character],
    ai_handler: TurnHandler | None = None,
) -> InteractiveCombatScene:
    """Cria combate interativo com IA padrao para inimigos."""
    handler = ai_handler or _default_ai_handler()
    engine = CombatEngine(party, enemies, handler)
    party_names = frozenset(c.name for c in party)
    return InteractiveCombatScene(
        engine=engine,
        party_names=party_names,
        ai_handler=handler,
    )


def _default_ai_handler() -> TurnHandler:
    """Cria handler padrao: skill > consumable > basic attack."""
    return CompositeHandler(handlers=(
        SkillHandler(),
        ConsumableHandler(),
        BasicAttackHandler(),
    ))
