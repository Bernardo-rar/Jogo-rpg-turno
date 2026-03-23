"""Testes para EncounterTemplateLoader."""

from src.dungeon.encounters.encounter_difficulty import EncounterDifficulty
from src.dungeon.encounters.encounter_template_loader import (
    load_encounter_templates,
    load_templates_by_difficulty,
)


class TestLoadEncounterTemplates:

    def test_loads_all_templates(self) -> None:
        templates = load_encounter_templates()
        assert len(templates) == 8

    def test_template_ids_match_keys(self) -> None:
        templates = load_encounter_templates()
        for tid, template in templates.items():
            assert template.template_id == tid

    def test_all_templates_have_slots(self) -> None:
        templates = load_encounter_templates()
        for template in templates.values():
            assert len(template.slots) >= 2


class TestLoadByDifficulty:

    def test_easy_templates(self) -> None:
        easy = load_templates_by_difficulty(EncounterDifficulty.EASY)
        assert len(easy) == 2
        assert all(
            t.difficulty == EncounterDifficulty.EASY for t in easy.values()
        )

    def test_medium_templates(self) -> None:
        medium = load_templates_by_difficulty(EncounterDifficulty.MEDIUM)
        assert len(medium) == 2

    def test_hard_templates(self) -> None:
        hard = load_templates_by_difficulty(EncounterDifficulty.HARD)
        assert len(hard) == 2

    def test_elite_templates(self) -> None:
        elite = load_templates_by_difficulty(EncounterDifficulty.ELITE)
        assert len(elite) == 2
