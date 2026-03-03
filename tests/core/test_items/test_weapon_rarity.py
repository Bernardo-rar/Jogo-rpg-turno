"""Testes para WeaponRarity enum."""

from src.core.items.weapon_rarity import WeaponRarity

EXPECTED_MEMBERS = {"COMMON", "UNCOMMON", "RARE", "LEGENDARY"}


class TestWeaponRarityMembers:

    def test_has_four_members(self) -> None:
        assert len(WeaponRarity) == 4

    def test_members_match_expected(self) -> None:
        assert {m.name for m in WeaponRarity} == EXPECTED_MEMBERS

    def test_values_are_unique(self) -> None:
        values = [m.value for m in WeaponRarity]
        assert len(values) == len(set(values))

    def test_accessible_by_name(self) -> None:
        for name in EXPECTED_MEMBERS:
            assert WeaponRarity[name].name == name
