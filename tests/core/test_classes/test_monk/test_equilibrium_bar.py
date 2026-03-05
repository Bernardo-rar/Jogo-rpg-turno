import pytest

from src.core.classes.monk.equilibrium_bar import EquilibriumBar, EquilibriumState


# Bar: max=100, vitality_upper=33, destruction_lower=67
# Center = 50, Vitality zone: 0-33, Balanced: 34-66, Destruction: 67-100


class TestEquilibriumBarInit:
    def test_starts_at_center(self):
        bar = EquilibriumBar(max_value=100, vitality_upper=33, destruction_lower=67)
        assert bar.value == 50

    def test_max_value(self):
        bar = EquilibriumBar(max_value=100, vitality_upper=33, destruction_lower=67)
        assert bar.max_value == 100

    def test_starts_in_balanced_state(self):
        bar = EquilibriumBar(max_value=100, vitality_upper=33, destruction_lower=67)
        assert bar.state == EquilibriumState.BALANCED


class TestEquilibriumBarState:
    def test_vitality_state(self):
        bar = EquilibriumBar(max_value=100, vitality_upper=33, destruction_lower=67)
        bar.shift_toward_vitality(30)  # 50 - 30 = 20
        assert bar.state == EquilibriumState.VITALITY

    def test_destruction_state(self):
        bar = EquilibriumBar(max_value=100, vitality_upper=33, destruction_lower=67)
        bar.shift_toward_destruction(30)  # 50 + 30 = 80
        assert bar.state == EquilibriumState.DESTRUCTION

    def test_balanced_state_lower_boundary(self):
        bar = EquilibriumBar(max_value=100, vitality_upper=33, destruction_lower=67)
        bar.shift_toward_vitality(16)  # 50 - 16 = 34
        assert bar.state == EquilibriumState.BALANCED

    def test_vitality_at_threshold(self):
        bar = EquilibriumBar(max_value=100, vitality_upper=33, destruction_lower=67)
        bar.shift_toward_vitality(17)  # 50 - 17 = 33
        assert bar.state == EquilibriumState.VITALITY

    def test_destruction_at_threshold(self):
        bar = EquilibriumBar(max_value=100, vitality_upper=33, destruction_lower=67)
        bar.shift_toward_destruction(17)  # 50 + 17 = 67
        assert bar.state == EquilibriumState.DESTRUCTION

    def test_balanced_upper_boundary(self):
        bar = EquilibriumBar(max_value=100, vitality_upper=33, destruction_lower=67)
        bar.shift_toward_destruction(16)  # 50 + 16 = 66
        assert bar.state == EquilibriumState.BALANCED


class TestEquilibriumBarShift:
    def test_shift_toward_destruction(self):
        bar = EquilibriumBar(max_value=100, vitality_upper=33, destruction_lower=67)
        shifted = bar.shift_toward_destruction(10)
        assert shifted == 10
        assert bar.value == 60

    def test_shift_toward_vitality(self):
        bar = EquilibriumBar(max_value=100, vitality_upper=33, destruction_lower=67)
        shifted = bar.shift_toward_vitality(10)
        assert shifted == 10
        assert bar.value == 40

    def test_shift_clamped_at_max(self):
        bar = EquilibriumBar(max_value=100, vitality_upper=33, destruction_lower=67)
        shifted = bar.shift_toward_destruction(999)
        assert shifted == 50  # 100 - 50 = 50
        assert bar.value == 100

    def test_shift_clamped_at_zero(self):
        bar = EquilibriumBar(max_value=100, vitality_upper=33, destruction_lower=67)
        shifted = bar.shift_toward_vitality(999)
        assert shifted == 50
        assert bar.value == 0


class TestEquilibriumBarDecay:
    def test_decay_toward_center_from_destruction(self):
        bar = EquilibriumBar(max_value=100, vitality_upper=33, destruction_lower=67)
        bar.shift_toward_destruction(30)  # value=80
        decayed = bar.decay_toward_center(5)
        assert decayed == 5
        assert bar.value == 75

    def test_decay_toward_center_from_vitality(self):
        bar = EquilibriumBar(max_value=100, vitality_upper=33, destruction_lower=67)
        bar.shift_toward_vitality(30)  # value=20
        decayed = bar.decay_toward_center(5)
        assert decayed == 5
        assert bar.value == 25

    def test_decay_stops_at_center(self):
        bar = EquilibriumBar(max_value=100, vitality_upper=33, destruction_lower=67)
        bar.shift_toward_destruction(3)  # value=53
        decayed = bar.decay_toward_center(10)
        assert decayed == 3
        assert bar.value == 50

    def test_decay_at_center_is_noop(self):
        bar = EquilibriumBar(max_value=100, vitality_upper=33, destruction_lower=67)
        decayed = bar.decay_toward_center(5)
        assert decayed == 0
        assert bar.value == 50


class TestEquilibriumBarIntensity:
    def test_vitality_intensity_at_zero(self):
        bar = EquilibriumBar(max_value=100, vitality_upper=33, destruction_lower=67)
        bar.shift_toward_vitality(50)  # value=0
        assert bar.vitality_intensity == pytest.approx(1.0)

    def test_vitality_intensity_at_threshold(self):
        bar = EquilibriumBar(max_value=100, vitality_upper=33, destruction_lower=67)
        bar.shift_toward_vitality(17)  # value=33
        assert bar.vitality_intensity == pytest.approx(0.0)

    def test_vitality_intensity_midway(self):
        bar = EquilibriumBar(max_value=100, vitality_upper=33, destruction_lower=67)
        bar.shift_toward_vitality(34)  # value=16
        # intensity = (33 - 16) / 33 = 17/33 ~ 0.515
        assert bar.vitality_intensity == pytest.approx(17 / 33)

    def test_vitality_intensity_zero_in_balanced(self):
        bar = EquilibriumBar(max_value=100, vitality_upper=33, destruction_lower=67)
        assert bar.vitality_intensity == 0.0

    def test_destruction_intensity_at_max(self):
        bar = EquilibriumBar(max_value=100, vitality_upper=33, destruction_lower=67)
        bar.shift_toward_destruction(50)  # value=100
        assert bar.destruction_intensity == pytest.approx(1.0)

    def test_destruction_intensity_at_threshold(self):
        bar = EquilibriumBar(max_value=100, vitality_upper=33, destruction_lower=67)
        bar.shift_toward_destruction(17)  # value=67
        assert bar.destruction_intensity == pytest.approx(0.0)

    def test_destruction_intensity_midway(self):
        bar = EquilibriumBar(max_value=100, vitality_upper=33, destruction_lower=67)
        bar.shift_toward_destruction(34)  # value=84
        # intensity = (84 - 67) / (100 - 67) = 17/33 ~ 0.515
        assert bar.destruction_intensity == pytest.approx(17 / 33)

    def test_destruction_intensity_zero_in_balanced(self):
        bar = EquilibriumBar(max_value=100, vitality_upper=33, destruction_lower=67)
        assert bar.destruction_intensity == 0.0


class TestEquilibriumBarEdgeCases:
    def test_zero_max_value(self):
        bar = EquilibriumBar(max_value=0, vitality_upper=0, destruction_lower=0)
        assert bar.value == 0
        assert bar.vitality_intensity == 0.0
        assert bar.destruction_intensity == 0.0
