from src.core.attributes.derived_stats import (
    calculate_hp,
    calculate_mana,
    calculate_physical_attack,
    calculate_magical_attack,
    calculate_physical_defense,
    calculate_magical_defense,
    calculate_hp_regen,
    calculate_mana_regen,
)


class TestCalculateHp:
    def test_level_1_doubles_base(self):
        # ((hit_dice + CON + vida_mod) * 2) * mod_hp
        # ((12 + 5 + 0) * 2) * 10 = 340
        result = calculate_hp(
            hit_dice=12, con=5, vida_mod=0, mod_hp=10, level=1
        )
        assert result == 340

    def test_level_2_no_doubling(self):
        # (hit_dice + CON + vida_mod) * mod_hp
        # (12 + 5 + 0) * 10 = 170
        result = calculate_hp(
            hit_dice=12, con=5, vida_mod=0, mod_hp=10, level=2
        )
        assert result == 170

    def test_vida_mod_adds_to_base(self):
        # ((12 + 5 + 3) * 2) * 10 = 400
        result = calculate_hp(
            hit_dice=12, con=5, vida_mod=3, mod_hp=10, level=1
        )
        assert result == 400


class TestCalculateMana:
    def test_warrior_level_1_multiplier(self):
        # Guerreiro lvl1: 6 * MIND * 10
        result = calculate_mana(mana_multiplier=6, mind=4)
        assert result == 240

    def test_warrior_level_2_plus_multiplier(self):
        # Guerreiro lvl2+: 4 * MIND * 10
        result = calculate_mana(mana_multiplier=4, mind=4)
        assert result == 160


class TestCalculatePhysicalAttack:
    def test_basic_formula(self):
        # (weapon_die + (STR + DEX)) * mod_atk_physical
        # (8 + (10 + 8)) * 10 = 260
        result = calculate_physical_attack(
            weapon_die=8, strength=10, dexterity=8, mod_atk_physical=10
        )
        assert result == 260


class TestCalculateMagicalAttack:
    def test_basic_formula(self):
        # (weapon_die + (WIS + INT)) * mod_atk_magical
        # (6 + (8 + 10)) * 6 = 144
        result = calculate_magical_attack(
            weapon_die=6, wisdom=8, intelligence=10, mod_atk_magical=6
        )
        assert result == 144


class TestCalculatePhysicalDefense:
    def test_basic_formula(self):
        # (DEX + CON + STR) * mod_def_physical
        # (8 + 6 + 10) * 5 = 120
        result = calculate_physical_defense(
            dexterity=8, constitution=6, strength=10, mod_def_physical=5
        )
        assert result == 120


class TestCalculateMagicalDefense:
    def test_basic_formula(self):
        # (CON + WIS + INT) * mod_def_magical
        # (6 + 8 + 10) * 3 = 72
        result = calculate_magical_defense(
            constitution=6, wisdom=8, intelligence=10, mod_def_magical=3
        )
        assert result == 72


class TestCalculateHpRegen:
    def test_basic_formula(self):
        # CON * regen_hp_mod
        # 6 * 5 = 30
        result = calculate_hp_regen(constitution=6, regen_hp_mod=5)
        assert result == 30


class TestCalculateManaRegen:
    def test_basic_formula(self):
        # MIND * regen_mana_mod
        # 4 * 3 = 12
        result = calculate_mana_regen(mind=4, regen_mana_mod=3)
        assert result == 12
