"""Testes para EncounterDifficulty enum."""

from src.dungeon.encounters.encounter_difficulty import EncounterDifficulty

EXPECTED_MEMBERS = {"EASY", "MEDIUM", "HARD", "ELITE"}


class TestEncounterDifficulty:

    def test_has_four_members(self) -> None:
        assert len(EncounterDifficulty) == 4

    def test_members_match_expected(self) -> None:
        assert {m.name for m in EncounterDifficulty} == EXPECTED_MEMBERS

    def test_accessible_by_name(self) -> None:
        for name in EXPECTED_MEMBERS:
            assert EncounterDifficulty[name].name == name
