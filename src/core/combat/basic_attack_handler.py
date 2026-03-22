from __future__ import annotations

from src.core.combat.action_economy import ActionType
from src.core.combat.combat_engine import CombatEvent, TurnContext
from src.core.combat.damage import DamageType, resolve_damage
from src.core.combat.targeting import AttackRange, get_valid_targets


class BasicAttackHandler:
    """Handler padrao: ataque no primeiro inimigo valido (tipo preferido da classe)."""

    def execute_turn(self, context: TurnContext) -> list[CombatEvent]:
        if not context.action_economy.has_actions:
            return []
        context.action_economy.use(ActionType.ACTION)
        atk_type = context.combatant.preferred_attack_type
        attack_range = _range_for(atk_type)
        targets = get_valid_targets(attack_range, context.enemies)
        if not targets:
            return []
        target = targets[0]
        result = resolve_damage(
            attack_power=context.combatant.attack_power,
            defense=target.defense_for(atk_type),
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


def _range_for(damage_type: DamageType) -> AttackRange:
    """PHYSICAL → MELEE, MAGICAL → RANGED."""
    if damage_type == DamageType.PHYSICAL:
        return AttackRange.MELEE
    return AttackRange.RANGED
