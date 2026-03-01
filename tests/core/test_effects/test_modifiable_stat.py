"""Testes para ModifiableStat enum."""

from src.core.effects.modifiable_stat import ModifiableStat


class TestModifiableStat:
    def test_has_physical_attack(self):
        assert isinstance(ModifiableStat.PHYSICAL_ATTACK, ModifiableStat)

    def test_has_magical_attack(self):
        assert isinstance(ModifiableStat.MAGICAL_ATTACK, ModifiableStat)

    def test_has_physical_defense(self):
        assert isinstance(ModifiableStat.PHYSICAL_DEFENSE, ModifiableStat)

    def test_has_magical_defense(self):
        assert isinstance(ModifiableStat.MAGICAL_DEFENSE, ModifiableStat)

    def test_has_speed(self):
        assert isinstance(ModifiableStat.SPEED, ModifiableStat)

    def test_has_max_hp(self):
        assert isinstance(ModifiableStat.MAX_HP, ModifiableStat)

    def test_has_max_mana(self):
        assert isinstance(ModifiableStat.MAX_MANA, ModifiableStat)

    def test_has_hp_regen(self):
        assert isinstance(ModifiableStat.HP_REGEN, ModifiableStat)

    def test_has_mana_regen(self):
        assert isinstance(ModifiableStat.MANA_REGEN, ModifiableStat)

    def test_has_healing_received(self):
        assert isinstance(ModifiableStat.HEALING_RECEIVED, ModifiableStat)
