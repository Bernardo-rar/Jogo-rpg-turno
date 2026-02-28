import pytest

from src.core.classes.fighter.stance import (
    Stance,
    StanceModifier,
    load_stance_modifiers,
)


class TestStanceEnum:
    def test_has_normal(self):
        assert Stance.NORMAL is not None

    def test_has_offensive(self):
        assert Stance.OFFENSIVE is not None

    def test_has_defensive(self):
        assert Stance.DEFENSIVE is not None

    def test_has_three_values(self):
        assert len(list(Stance)) == 3


class TestStanceModifier:
    def test_is_frozen(self):
        mod = StanceModifier(atk_multiplier=1.0, def_multiplier=1.0)
        with pytest.raises(AttributeError):
            mod.atk_multiplier = 2.0


class TestLoadStanceModifiers:
    def test_loads_all_three_stances(self):
        modifiers = load_stance_modifiers()
        assert len(modifiers) == 3

    def test_normal_has_neutral_multipliers(self):
        mods = load_stance_modifiers()
        assert mods[Stance.NORMAL].atk_multiplier == pytest.approx(1.0)
        assert mods[Stance.NORMAL].def_multiplier == pytest.approx(1.0)

    def test_offensive_increases_attack(self):
        mods = load_stance_modifiers()
        assert mods[Stance.OFFENSIVE].atk_multiplier > 1.0

    def test_offensive_decreases_defense(self):
        mods = load_stance_modifiers()
        assert mods[Stance.OFFENSIVE].def_multiplier < 1.0

    def test_defensive_decreases_attack(self):
        mods = load_stance_modifiers()
        assert mods[Stance.DEFENSIVE].atk_multiplier < 1.0

    def test_defensive_increases_defense(self):
        mods = load_stance_modifiers()
        assert mods[Stance.DEFENSIVE].def_multiplier > 1.0
