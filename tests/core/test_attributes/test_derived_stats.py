from src.core.attributes.derived_stats import (
    AttackInput,
    DefenseInput,
    HpInput,
    calculate_attack,
    calculate_defense,
    calculate_hp,
    calculate_hp_regen,
    calculate_mana,
    calculate_mana_regen,
)


class TestCalculateHp:
    def test_level_1_doubles_base(self):
        # ((hit_dice + CON + vida_mod) * 2) * mod_hp
        # ((12 + 5 + 0) * 2) * 10 = 340
        hp_input = HpInput(hit_dice=12, con=5, vida_mod=0, mod_hp=10, level=1)
        assert calculate_hp(hp_input) == 340

    def test_level_2_no_doubling(self):
        # (hit_dice + CON + vida_mod) * mod_hp
        # (12 + 5 + 0) * 10 = 170
        hp_input = HpInput(hit_dice=12, con=5, vida_mod=0, mod_hp=10, level=2)
        assert calculate_hp(hp_input) == 170

    def test_vida_mod_adds_to_base(self):
        # ((12 + 5 + 3) * 2) * 10 = 400
        hp_input = HpInput(hit_dice=12, con=5, vida_mod=3, mod_hp=10, level=1)
        assert calculate_hp(hp_input) == 400


class TestCalculateMana:
    def test_warrior_level_1_multiplier(self):
        # Guerreiro lvl1: 6 * MIND * 10
        result = calculate_mana(mana_multiplier=6, mind=4)
        assert result == 240

    def test_warrior_level_2_plus_multiplier(self):
        # Guerreiro lvl2+: 4 * MIND * 10
        result = calculate_mana(mana_multiplier=4, mind=4)
        assert result == 160


class TestCalculateAttack:
    def test_physical_attack_formula(self):
        # (weapon_die + (STR + DEX)) * mod_atk_physical
        # (8 + (10 + 8)) * 10 = 260
        attack_input = AttackInput(
            weapon_die=8, primary_stat=10, secondary_stat=8, modifier=10,
        )
        assert calculate_attack(attack_input) == 260

    def test_magical_attack_formula(self):
        # (weapon_die + (WIS + INT)) * mod_atk_magical
        # (6 + (8 + 10)) * 6 = 144
        attack_input = AttackInput(
            weapon_die=6, primary_stat=8, secondary_stat=10, modifier=6,
        )
        assert calculate_attack(attack_input) == 144


class TestCalculateDefense:
    def test_physical_defense_formula(self):
        # (DEX + CON + STR) * mod_def_physical
        # (8 + 6 + 10) * 5 = 120
        defense_input = DefenseInput(
            primary_stat=8, secondary_stat=6, tertiary_stat=10, modifier=5,
        )
        assert calculate_defense(defense_input) == 120

    def test_magical_defense_formula(self):
        # (CON + WIS + INT) * mod_def_magical
        # (6 + 8 + 10) * 3 = 72
        defense_input = DefenseInput(
            primary_stat=6, secondary_stat=8, tertiary_stat=10, modifier=3,
        )
        assert calculate_defense(defense_input) == 72


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
