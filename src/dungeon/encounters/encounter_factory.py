"""EncounterFactory — gera grupo de inimigos + handler montado."""

from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import TYPE_CHECKING

from src.core.combat.basic_attack_handler import BasicAttackHandler
from src.core.combat.dispatch_handler import DispatchTurnHandler
from src.core.combat.synergy.synergy_config import SynergyBinding
from src.dungeon.enemies.ai.archetype_handler_factory import create_handler
from src.dungeon.enemies.elite_modifier import EliteTierBonuses, apply_elite
from src.dungeon.encounters.encounter_template import EncounterSlot, EncounterTemplate

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
    synergy_bindings: tuple[SynergyBinding, ...] = ()


class EncounterFactory:
    """Gera encounters a partir de templates, factory e pool de monstros."""

    def __init__(
        self,
        enemy_factory: EnemyFactory,
        enemy_pool: dict[str, EnemyTemplate],
        elite_bonuses: dict[int, EliteTierBonuses] | None = None,
    ) -> None:
        self._enemy_factory = enemy_factory
        self._enemy_pool = enemy_pool
        self._elite_bonuses = elite_bonuses or {}

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
        bindings: list[SynergyBinding] = []
        suffix_counter: dict[str, int] = {}
        for slot in template.slots:
            chosen = self._pick_template(slot, rng)
            if chosen is None:
                continue
            if slot.is_elite:
                chosen = self._apply_elite(chosen, rng)
            count = suffix_counter.get(chosen.enemy_id, 0)
            suffix_counter[chosen.enemy_id] = count + 1
            enemy = self._enemy_factory.create(chosen, suffix=str(count))
            enemies.append(enemy)
            handlers[enemy.name] = create_handler(slot.archetype)
            if template.synergy_id:
                bindings.append(SynergyBinding(
                    combatant_name=enemy.name,
                    synergy_id=template.synergy_id,
                    role_key=slot.synergy_role,
                ))
        handler = DispatchTurnHandler(handlers, BasicAttackHandler())
        return EncounterResult(
            enemies=tuple(enemies),
            handler=handler,
            synergy_bindings=tuple(bindings),
        )

    def _pick_template(
        self,
        slot: EncounterSlot,
        rng: Random,
    ) -> EnemyTemplate | None:
        candidates = _filter_by_archetype(
            self._enemy_pool, slot.archetype,
        )
        if not candidates:
            return None
        return rng.choice(candidates)

    def _apply_elite(
        self,
        template: EnemyTemplate,
        rng: Random,
    ) -> EnemyTemplate:
        bonuses = self._elite_bonuses.get(template.tier)
        if bonuses is None:
            return template
        return apply_elite(template, bonuses, rng)


def _filter_by_archetype(
    pool: dict[str, EnemyTemplate],
    archetype,
) -> list[EnemyTemplate]:
    """Filtra templates do pool que batem com o archetype."""
    return [t for t in pool.values() if t.archetype == archetype]
