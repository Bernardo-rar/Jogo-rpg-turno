import pytest

from src.core.combat.damage import (
    BASE_CRIT_CHANCE,
    DEFAULT_CRIT_MULTIPLIER,
    DamageResult,
    DamageType,
    MAX_CRIT_CHANCE,
    MIN_DAMAGE,
    calculate_crit_chance,
    resolve_damage,
)


class TestDamageType:
    def test_has_physical(self):
        assert DamageType.PHYSICAL is not None

    def test_has_magical(self):
        assert DamageType.MAGICAL is not None

    def test_has_two_values(self):
        assert len(list(DamageType)) == 2


class TestDamageResult:
    def test_is_frozen(self):
        result = DamageResult(
            raw_damage=100,
            defense_value=50,
            is_critical=False,
            final_damage=50,
        )
        with pytest.raises(AttributeError):
            result.final_damage = 999


class TestResolveDamage:
    def test_basic_damage_attack_minus_defense(self):
        result = resolve_damage(attack_power=100, defense=30)
        assert result.final_damage == 70

    def test_raw_damage_stored(self):
        result = resolve_damage(attack_power=100, defense=30)
        assert result.raw_damage == 100

    def test_defense_value_stored(self):
        result = resolve_damage(attack_power=100, defense=30)
        assert result.defense_value == 30

    def test_not_critical_by_default(self):
        result = resolve_damage(attack_power=100, defense=30)
        assert result.is_critical is False

    def test_minimum_damage_when_defense_exceeds_attack(self):
        result = resolve_damage(attack_power=10, defense=999)
        assert result.final_damage == MIN_DAMAGE

    def test_minimum_damage_when_defense_equals_attack(self):
        result = resolve_damage(attack_power=50, defense=50)
        assert result.final_damage == MIN_DAMAGE

    def test_zero_attack_gives_minimum_damage(self):
        result = resolve_damage(attack_power=0, defense=50)
        assert result.final_damage == MIN_DAMAGE

    def test_zero_defense_gives_full_damage(self):
        result = resolve_damage(attack_power=100, defense=0)
        assert result.final_damage == 100


class TestResolveDamageCritical:
    def test_critical_multiplies_attack_before_defense(self):
        # attack=100, crit -> 200, defense=50 -> 150
        result = resolve_damage(attack_power=100, defense=50, is_critical=True)
        assert result.final_damage == 100 * DEFAULT_CRIT_MULTIPLIER - 50

    def test_critical_flag_stored(self):
        result = resolve_damage(attack_power=100, defense=50, is_critical=True)
        assert result.is_critical is True

    def test_critical_raw_damage_is_original(self):
        result = resolve_damage(attack_power=100, defense=50, is_critical=True)
        assert result.raw_damage == 100

    def test_critical_still_respects_minimum(self):
        result = resolve_damage(attack_power=1, defense=9999, is_critical=True)
        assert result.final_damage == MIN_DAMAGE


class TestResolveDamageWithFighterStats:
    """Testa com stats reais do Fighter (STR=10, DEX=8, CON=5)."""

    def test_fighter_vs_fighter_physical(self):
        # Fighter physical_attack = (0 + 10 + 8) * 10 = 180
        # Fighter physical_defense = (8 + 5 + 10) * 5 = 115
        result = resolve_damage(attack_power=180, defense=115)
        assert result.final_damage == 65

    def test_fighter_crit_vs_fighter_physical(self):
        # 180 * 2 = 360, 360 - 115 = 245
        result = resolve_damage(attack_power=180, defense=115, is_critical=True)
        assert result.final_damage == 245


class TestCalculateCritChance:
    def test_no_bonus_returns_base(self):
        assert calculate_crit_chance(bonus_pct=0) == BASE_CRIT_CHANCE

    def test_bonus_adds_to_base(self):
        # 10% bonus = 0.10, base = 0.05 -> 0.15
        result = calculate_crit_chance(bonus_pct=10)
        assert result == pytest.approx(BASE_CRIT_CHANCE + 0.10)

    def test_cumulative_threshold_bonus(self):
        # DEX 26 = 3 thresholds tier 1 = 30% bonus
        result = calculate_crit_chance(bonus_pct=30)
        assert result == pytest.approx(BASE_CRIT_CHANCE + 0.30)

    def test_capped_at_max(self):
        result = calculate_crit_chance(bonus_pct=200)
        assert result == MAX_CRIT_CHANCE

    def test_max_crit_is_one(self):
        assert MAX_CRIT_CHANCE == 1.0


class TestConstants:
    def test_min_damage_is_one(self):
        assert MIN_DAMAGE == 1

    def test_default_crit_multiplier_is_two(self):
        assert DEFAULT_CRIT_MULTIPLIER == 2

    def test_base_crit_chance_is_five_percent(self):
        assert BASE_CRIT_CHANCE == pytest.approx(0.05)
