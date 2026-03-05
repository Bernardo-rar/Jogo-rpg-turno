import pytest

from src.core.classes.monk.equilibrium_config import (
    EquilibriumConfig,
    load_equilibrium_config,
)


class TestEquilibriumConfigFrozen:
    def test_is_frozen(self):
        config = EquilibriumConfig(
            max_value=100,
            vitality_upper=33,
            destruction_lower=67,
            shift_per_attack=10,
            shift_per_defend=10,
            decay_per_turn=5,
            vitality_def_bonus=0.20,
            vitality_regen_bonus=0.15,
            destruction_atk_bonus=0.25,
            destruction_crit_bonus=0.15,
            balance_atk_bonus=0.08,
            balance_def_bonus=0.08,
            base_hit_count=2,
            destruction_extra_hits=1,
            debuff_chance_max=0.30,
        )
        with pytest.raises(AttributeError):
            config.max_value = 200


class TestEquilibriumConfigLoader:
    def test_loads_from_json(self):
        config = load_equilibrium_config()
        assert isinstance(config, EquilibriumConfig)

    def test_max_value(self):
        config = load_equilibrium_config()
        assert config.max_value == 100

    def test_vitality_upper(self):
        config = load_equilibrium_config()
        assert config.vitality_upper == 33

    def test_destruction_lower(self):
        config = load_equilibrium_config()
        assert config.destruction_lower == 67

    def test_shift_per_attack(self):
        config = load_equilibrium_config()
        assert config.shift_per_attack == 10

    def test_shift_per_defend(self):
        config = load_equilibrium_config()
        assert config.shift_per_defend == 10

    def test_decay_per_turn(self):
        config = load_equilibrium_config()
        assert config.decay_per_turn == 5

    def test_vitality_def_bonus(self):
        config = load_equilibrium_config()
        assert config.vitality_def_bonus == 0.20

    def test_vitality_regen_bonus(self):
        config = load_equilibrium_config()
        assert config.vitality_regen_bonus == 0.15

    def test_destruction_atk_bonus(self):
        config = load_equilibrium_config()
        assert config.destruction_atk_bonus == 0.25

    def test_destruction_crit_bonus(self):
        config = load_equilibrium_config()
        assert config.destruction_crit_bonus == 0.15

    def test_balance_atk_bonus(self):
        config = load_equilibrium_config()
        assert config.balance_atk_bonus == 0.08

    def test_balance_def_bonus(self):
        config = load_equilibrium_config()
        assert config.balance_def_bonus == 0.08

    def test_base_hit_count(self):
        config = load_equilibrium_config()
        assert config.base_hit_count == 2

    def test_destruction_extra_hits(self):
        config = load_equilibrium_config()
        assert config.destruction_extra_hits == 1

    def test_debuff_chance_max(self):
        config = load_equilibrium_config()
        assert config.debuff_chance_max == 0.30
