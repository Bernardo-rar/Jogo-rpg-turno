"""EncounterBuilder — constrói encounters/bosses para nós do mapa."""

from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import TYPE_CHECKING

from src.core.combat.synergy.synergy_config import SynergyBinding
from src.dungeon.encounters.encounter_difficulty import EncounterDifficulty
from src.dungeon.encounters.encounter_template_loader import (
    load_templates_by_difficulty,
)
from src.dungeon.map.room_type import RoomType

if TYPE_CHECKING:
    from src.core.characters.character import Character
    from src.core.combat.combat_engine import TurnHandler
    from src.dungeon.encounters.encounter_factory import EncounterFactory
    from src.dungeon.enemies.bosses.boss_factory import BossFactory, BossResult
    from src.dungeon.map.map_node import MapNode


@dataclass(frozen=True)
class CombatSetup:
    """Tudo que precisa para iniciar um combate."""

    enemies: list[Character]
    handler: TurnHandler
    is_boss: bool
    synergy_bindings: list[SynergyBinding] | None = None


_ROOM_TO_DIFFICULTY: dict[RoomType, EncounterDifficulty] = {
    RoomType.COMBAT: EncounterDifficulty.MEDIUM,
    RoomType.ELITE: EncounterDifficulty.ELITE,
}


class EncounterBuilder:
    """Constrói encounters a partir de nós do mapa."""

    def __init__(
        self,
        encounter_factory: EncounterFactory,
        boss_factory: BossFactory,
    ) -> None:
        self._encounter_factory = encounter_factory
        self._boss_factory = boss_factory

    def build(
        self, node: MapNode, rng: Random, tier: int = 1,
    ) -> CombatSetup:
        """Gera enemies + handler para o nó dado."""
        if node.room_type == RoomType.BOSS:
            return self._build_boss(rng, tier)
        return self._build_encounter(node, rng)

    def _build_encounter(
        self,
        node: MapNode,
        rng: Random,
    ) -> CombatSetup:
        difficulty = _ROOM_TO_DIFFICULTY.get(
            node.room_type, EncounterDifficulty.MEDIUM,
        )
        templates = load_templates_by_difficulty(difficulty)
        if not templates:
            templates = load_templates_by_difficulty(
                EncounterDifficulty.EASY,
            )
        template_id = rng.choice(list(templates.keys()))
        result = self._encounter_factory.create(
            templates[template_id], rng=rng,
        )
        bindings = list(result.synergy_bindings) or None
        return CombatSetup(
            enemies=list(result.enemies),
            handler=result.handler,
            is_boss=False,
            synergy_bindings=bindings,
        )

    def _build_boss(
        self, rng: Random | None = None, tier: int = 1,
    ) -> CombatSetup:
        from src.dungeon.enemies.bosses.boss_loader import load_all_bosses
        from src.dungeon.enemies.bosses.boss_registry import register_all_bosses
        register_all_bosses()
        all_bosses = load_all_bosses()
        boss_id = _pick_boss(all_bosses, rng, tier)
        template = all_bosses[boss_id]
        result = self._boss_factory.create(template)
        from src.core.combat.basic_attack_handler import BasicAttackHandler
        from src.core.combat.dispatch_handler import DispatchTurnHandler
        handler = DispatchTurnHandler(
            {result.character.name: result.handler},
            BasicAttackHandler(),
        )
        return CombatSetup(
            enemies=[result.character],
            handler=handler,
            is_boss=True,
        )


def _pick_boss(
    bosses: dict[str, object], rng: Random | None, tier: int = 1,
) -> str:
    """Escolhe boss aleatório do tier correto."""
    tier_bosses = [
        bid for bid, t in bosses.items()
        if getattr(t, "tier", 1) == tier
    ]
    if not tier_bosses:
        tier_bosses = list(bosses.keys())
    if rng is not None:
        return rng.choice(tier_bosses)
    return tier_bosses[0]
