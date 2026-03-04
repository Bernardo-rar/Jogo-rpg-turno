import pytest

from src.core.classes.paladin.aura import Aura, AuraModifier, load_aura_modifiers


class TestAuraEnum:
    def test_has_none(self):
        assert Aura.NONE.value is not None

    def test_has_protection(self):
        assert Aura.PROTECTION.value is not None

    def test_has_attack(self):
        assert Aura.ATTACK.value is not None

    def test_has_vitality(self):
        assert Aura.VITALITY.value is not None


class TestAuraModifier:
    def test_is_frozen(self):
        mod = AuraModifier(def_multiplier=1.0, atk_multiplier=1.0, regen_multiplier=1.0)
        with pytest.raises(AttributeError):
            mod.def_multiplier = 2.0  # type: ignore[misc]


class TestLoadAuraModifiers:
    def test_load_returns_dict(self):
        mods = load_aura_modifiers()
        assert isinstance(mods, dict)

    def test_all_auras_present(self):
        mods = load_aura_modifiers()
        for aura in Aura:
            assert aura in mods

    def test_none_is_neutral(self):
        mods = load_aura_modifiers()
        none_mod = mods[Aura.NONE]
        assert none_mod.def_multiplier == 1.0
        assert none_mod.atk_multiplier == 1.0
        assert none_mod.regen_multiplier == 1.0

    def test_protection_boosts_def(self):
        mods = load_aura_modifiers()
        assert mods[Aura.PROTECTION].def_multiplier == 1.15
        assert mods[Aura.PROTECTION].atk_multiplier == 1.0

    def test_attack_boosts_atk(self):
        mods = load_aura_modifiers()
        assert mods[Aura.ATTACK].atk_multiplier == 1.15
        assert mods[Aura.ATTACK].def_multiplier == 1.0

    def test_vitality_boosts_regen(self):
        mods = load_aura_modifiers()
        assert mods[Aura.VITALITY].regen_multiplier == 1.15
        assert mods[Aura.VITALITY].atk_multiplier == 1.0
