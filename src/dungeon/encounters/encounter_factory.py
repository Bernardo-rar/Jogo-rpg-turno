"""EncounterFactory — gera grupo de inimigos + handler montado."""

from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import TYPE_CHECKING

from src.core.combat.basic_attack_handler import BasicAttackHandler
from src.core.combat.dispatch_handler import DispatchTurnHandler
from src.dungeon.enemies.ai.archetype_handler_factory import create_handler
from src.dungeon.encounters.encounter_template import EncounterTemplate

if TYPE_CHECKING:
    from src.core.characters.character import Character
    from src.core.combat.combat_engine import TurnHandler
    from src.dungeon.enemies.enemy_factory import EnemyFactory
    from src.dungeon.enemies.enemy_template import EnemyTemplate


@dataclass(frozen=True)
class EncounterResult:
    """Resultado de gerar um encounter: inimigos + handler pronto."""

    enemies: tuple[Character, ...]
    handler: TurnHandler


class EncounterFactory:
    """Gera encounters a partir de templates, factory e pool de monstros."""

    def __init__(
        self,
        enemy_factory: EnemyFactory,
        enemy_pool: dict[str, EnemyTemplate],
    ) -> None:
        self._enemy_factory = enemy_factory
        self._enemy_pool = enemy_pool

    def create(
        self,
        template: EncounterTemplate,
        rng: Random | None = None,
    ) -> EncounterResult:
        """Gera inimigos para cada slot do template."""
        if rng is None:
            rng = Random()
        enemies: list[Character] = []
        handlers: dict[str, TurnHandler] = {}
        suffix_counter: dict[str, int] = {}
        for slot in template.slots:
            candidates = _filter_by_archetype(
                self._enemy_pool, slot.archetype,
            )
            if not candidates:
                continue
            chosen = rng.choice(candidates)
            count = suffix_counter.get(chosen.enemy_id, 0)
            suffix_counter[chosen.enemy_id] = count + 1
            enemy = self._enemy_factory.create(chosen, suffix=str(count))
            enemies.append(enemy)
            handlers[enemy.name] = create_handler(slot.archetype)
        handler = DispatchTurnHandler(handlers, BasicAttackHandler())
        return EncounterResult(
            enemies=tuple(enemies),
            handler=handler,
        )


def _filter_by_archetype(
    pool: dict[str, EnemyTemplate],
    archetype,
) -> list[EnemyTemplate]:
    """Filtra templates do pool que batem com o archetype."""
    return [t for t in pool.values() if t.archetype == archetype]
