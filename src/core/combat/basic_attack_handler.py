from __future__ import annotations

from src.core.combat.action_economy import ActionType
from src.core.combat.combat_engine import CombatEvent, TurnContext
from src.core.combat.damage import resolve_damage
from src.core.combat.targeting import AttackRange, get_valid_targets


class BasicAttackHandler:
    """Handler padrao: ataque fisico melee no primeiro inimigo valido."""

    def execute_turn(self, context: TurnContext) -> list[CombatEvent]:
        if not context.action_economy.has_actions:
            return []
        context.action_economy.use(ActionType.ACTION)
        targets = get_valid_targets(AttackRange.MELEE, context.enemies)
        if not targets:
            return []
        target = targets[0]
        result = resolve_damage(
            attack_power=context.combatant.physical_attack,
            defense=target.physical_defense,
        )
        target.take_damage(result.final_damage)
        return [
            CombatEvent(
                round_number=context.round_number,
                actor_name=context.combatant.name,
                target_name=target.name,
                damage=result,
            )
        ]
