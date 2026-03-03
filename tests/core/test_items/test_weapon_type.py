"""Testes para WeaponType enum."""

from src.core.items.weapon_type import WeaponType

EXPECTED_MEMBERS = {
    "SWORD", "DAGGER", "BOW", "STAFF",
    "HAMMER", "LANCE", "MACE", "FIST",
}


class TestWeaponTypeMembers:

    def test_has_eight_members(self) -> None:
        assert len(WeaponType) == 8

    def test_members_match_expected(self) -> None:
        assert {m.name for m in WeaponType} == EXPECTED_MEMBERS

    def test_values_are_unique(self) -> None:
        values = [m.value for m in WeaponType]
        assert len(values) == len(set(values))

    def test_accessible_by_name(self) -> None:
        for name in EXPECTED_MEMBERS:
            assert WeaponType[name].name == name
