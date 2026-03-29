from __future__ import annotations

from src.core.combat.action_economy import ActionType
from src.core.combat.combat_engine import CombatEvent, TurnContext
from src.core.combat.damage import DamageResult, DamageType, resolve_damage
from src.core.combat.position_modifiers import scale_dealt, scale_taken
from src.core.combat.skill_effect_applier import get_run_modifier_effect
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
        raw_atk = scale_dealt(context.combatant.attack_power, context.combatant.position)
        attack = _scaled_attack(raw_atk)
        result = resolve_damage(
            attack_power=attack,
            defense=target.defense_for(atk_type),
        )
        raw_final = scale_taken(result.final_damage, target.position)
        final = _scaled_final_damage(raw_final)
        target.take_damage(final)
        scaled = _with_final(result, final)
        return [
            CombatEvent(
                round_number=context.round_number,
                actor_name=context.combatant.name,
                target_name=target.name,
                damage=scaled,
            )
        ]


def _scaled_attack(attack_power: int) -> int:
    """Aplica damage_dealt_mult do modifier ao attack."""
    mod = get_run_modifier_effect()
    if mod is None:
        return attack_power
    return int(attack_power * mod.damage_dealt_mult)


def _scaled_final_damage(final: int) -> int:
    """Aplica damage_taken_mult do modifier ao dano final."""
    mod = get_run_modifier_effect()
    if mod is None:
        return final
    return max(1, int(final * mod.damage_taken_mult))


def _with_final(result: DamageResult, final: int) -> DamageResult:
    """Retorna DamageResult com final_damage atualizado."""
    if result.final_damage == final:
        return result
    return DamageResult(
        raw_damage=result.raw_damage,
        defense_value=result.defense_value,
        is_critical=result.is_critical,
        final_damage=final,
    )


def _range_for(damage_type: DamageType) -> AttackRange:
    """PHYSICAL → MELEE, MAGICAL → RANGED."""
    if damage_type == DamageType.PHYSICAL:
        return AttackRange.MELEE
    return AttackRange.RANGED
