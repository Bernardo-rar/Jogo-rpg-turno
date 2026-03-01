"""Testes para ModifiableStat enum."""

from src.core.effects.modifiable_stat import ModifiableStat


class TestModifiableStat:
    def test_has_physical_attack(self):
        assert ModifiableStat.PHYSICAL_ATTACK is not None

    def test_has_magical_attack(self):
        assert ModifiableStat.MAGICAL_ATTACK is not None

    def test_has_physical_defense(self):
        assert ModifiableStat.PHYSICAL_DEFENSE is not None

    def test_has_magical_defense(self):
        assert ModifiableStat.MAGICAL_DEFENSE is not None

    def test_has_speed(self):
        assert ModifiableStat.SPEED is not None

    def test_has_max_hp(self):
        assert ModifiableStat.MAX_HP is not None

    def test_has_max_mana(self):
        assert ModifiableStat.MAX_MANA is not None

    def test_has_hp_regen(self):
        assert ModifiableStat.HP_REGEN is not None

    def test_has_mana_regen(self):
        assert ModifiableStat.MANA_REGEN is not None
