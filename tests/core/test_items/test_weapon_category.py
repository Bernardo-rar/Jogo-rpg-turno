"""Testes para WeaponCategory enum."""

from src.core.items.weapon_category import WeaponCategory

EXPECTED_MEMBERS = {"SIMPLE", "MARTIAL", "MAGICAL"}


class TestWeaponCategoryMembers:

    def test_has_three_members(self) -> None:
        assert len(WeaponCategory) == 3

    def test_members_match_expected(self) -> None:
        assert {m.name for m in WeaponCategory} == EXPECTED_MEMBERS

    def test_accessible_by_name(self) -> None:
        for name in EXPECTED_MEMBERS:
            assert WeaponCategory[name].name == name

    def test_values_are_unique(self) -> None:
        values = [m.value for m in WeaponCategory]
        assert len(values) == len(set(values))
