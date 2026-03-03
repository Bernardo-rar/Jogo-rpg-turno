"""Testes para DamageKind enum (sub-tipos de dano fisico)."""

from src.core.items.damage_kind import DamageKind

EXPECTED_MEMBERS = {"SLASHING", "PIERCING", "BLUDGEONING"}


class TestDamageKindMembers:

    def test_has_three_members(self) -> None:
        assert len(DamageKind) == 3

    def test_members_match_expected(self) -> None:
        assert {m.name for m in DamageKind} == EXPECTED_MEMBERS

    def test_values_are_unique(self) -> None:
        values = [m.value for m in DamageKind]
        assert len(values) == len(set(values))

    def test_accessible_by_name(self) -> None:
        for name in EXPECTED_MEMBERS:
            assert DamageKind[name].name == name
