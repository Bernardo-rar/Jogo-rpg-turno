import pytest

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.threshold_calculator import ThresholdCalculator


@pytest.fixture
def calculator() -> ThresholdCalculator:
    return ThresholdCalculator.from_json("data/attributes/thresholds.json")


class TestThresholdCalculatorLoading:
    def test_loads_from_json_file(self, calculator: ThresholdCalculator):
        assert calculator is not None

    def test_has_thresholds_for_strength(self, calculator: ThresholdCalculator):
        thresholds = calculator.get_thresholds(AttributeType.STRENGTH)
        assert len(thresholds) == 5


class TestStrengthThresholdBonuses:
    def test_no_bonus_below_first_threshold(self, calculator: ThresholdCalculator):
        bonuses = calculator.calculate_bonuses(AttributeType.STRENGTH, 17)
        assert bonuses.get("atk_physical_mod", 0) == 0

    def test_one_tier1_bonus_at_18(self, calculator: ThresholdCalculator):
        bonuses = calculator.calculate_bonuses(AttributeType.STRENGTH, 18)
        assert bonuses["atk_physical_mod"] == 2
        assert bonuses["def_physical_mod"] == 1
        assert bonuses["hp_mod"] == 2

    def test_two_tier1_bonuses_at_22(self, calculator: ThresholdCalculator):
        bonuses = calculator.calculate_bonuses(AttributeType.STRENGTH, 22)
        assert bonuses["atk_physical_mod"] == 4
        assert bonuses["def_physical_mod"] == 2
        assert bonuses["hp_mod"] == 4

    def test_three_tier1_bonuses_at_26(self, calculator: ThresholdCalculator):
        bonuses = calculator.calculate_bonuses(AttributeType.STRENGTH, 26)
        assert bonuses["atk_physical_mod"] == 6
        assert bonuses["def_physical_mod"] == 3
        assert bonuses["hp_mod"] == 6

    def test_tier1_plus_tier2_at_30(self, calculator: ThresholdCalculator):
        bonuses = calculator.calculate_bonuses(AttributeType.STRENGTH, 30)
        # 3x tier1 (2+2+2=6) + 1x tier2 (4) = 10
        assert bonuses["atk_physical_mod"] == 10
        # 3x tier1 (1+1+1=3) + 1x tier2 (2) = 5
        assert bonuses["def_physical_mod"] == 5

    def test_all_thresholds_at_32(self, calculator: ThresholdCalculator):
        bonuses = calculator.calculate_bonuses(AttributeType.STRENGTH, 32)
        # 3x tier1 (2+2+2=6) + 2x tier2 (4+4=8) = 14
        assert bonuses["atk_physical_mod"] == 14
        # 3x tier1 (1+1+1=3) + 2x tier2 (2+2=4) = 7
        assert bonuses["def_physical_mod"] == 7

    def test_value_between_thresholds_gets_lower_bonus(
        self, calculator: ThresholdCalculator
    ):
        bonuses = calculator.calculate_bonuses(AttributeType.STRENGTH, 20)
        assert bonuses["atk_physical_mod"] == 2


class TestDexterityThresholdBonuses:
    def test_crit_chance_at_18(self, calculator: ThresholdCalculator):
        bonuses = calculator.calculate_bonuses(AttributeType.DEXTERITY, 18)
        assert bonuses["crit_chance_pct"] == 10

    def test_crit_chance_at_30(self, calculator: ThresholdCalculator):
        bonuses = calculator.calculate_bonuses(AttributeType.DEXTERITY, 30)
        # 3x tier1 (10+10+10=30) + 1x tier2 (20) = 50
        assert bonuses["crit_chance_pct"] == 50


class TestConstitutionThresholdBonuses:
    def test_multi_stat_bonus_at_18(self, calculator: ThresholdCalculator):
        bonuses = calculator.calculate_bonuses(AttributeType.CONSTITUTION, 18)
        assert bonuses["hp_mod"] == 2
        assert bonuses["def_physical_mod"] == 1
        assert bonuses["def_magical_mod"] == 1
        assert bonuses["hp_regen_mod"] == 1
        assert bonuses["stamina_mod"] == 1


class TestMindThresholdBonuses:
    def test_mind_has_no_threshold_bonuses(self, calculator: ThresholdCalculator):
        bonuses = calculator.calculate_bonuses(AttributeType.MIND, 32)
        assert len(bonuses) == 0
