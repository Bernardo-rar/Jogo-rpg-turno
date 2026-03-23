"""Testes para EncounterTemplate e EncounterSlot."""

from src.dungeon.encounters.encounter_difficulty import EncounterDifficulty
from src.dungeon.encounters.encounter_template import (
    EncounterSlot,
    EncounterTemplate,
)
from src.dungeon.enemies.enemy_archetype import EnemyArchetype


class TestEncounterSlot:

    def test_from_dict_basic(self) -> None:
        slot = EncounterSlot.from_dict({"archetype": "DPS"})
        assert slot.archetype == EnemyArchetype.DPS
        assert slot.is_elite is False

    def test_from_dict_elite(self) -> None:
        slot = EncounterSlot.from_dict({"archetype": "TANK", "is_elite": True})
        assert slot.archetype == EnemyArchetype.TANK
        assert slot.is_elite is True

    def test_frozen(self) -> None:
        slot = EncounterSlot(archetype=EnemyArchetype.DPS)
        try:
            slot.archetype = EnemyArchetype.TANK  # type: ignore[misc]
            assert False, "Should be frozen"
        except AttributeError:
            pass


class TestEncounterTemplate:

    def test_from_dict(self) -> None:
        data = {
            "template_id": "easy_3dps",
            "difficulty": "EASY",
            "slots": [
                {"archetype": "DPS"},
                {"archetype": "DPS"},
                {"archetype": "DPS"},
            ],
        }
        template = EncounterTemplate.from_dict(data)
        assert template.template_id == "easy_3dps"
        assert template.difficulty == EncounterDifficulty.EASY
        assert len(template.slots) == 3
        assert all(s.archetype == EnemyArchetype.DPS for s in template.slots)

    def test_from_dict_mixed(self) -> None:
        data = {
            "template_id": "medium_balanced",
            "difficulty": "MEDIUM",
            "slots": [
                {"archetype": "TANK"},
                {"archetype": "DPS"},
                {"archetype": "HEALER"},
                {"archetype": "CONTROLLER"},
            ],
        }
        template = EncounterTemplate.from_dict(data)
        assert template.difficulty == EncounterDifficulty.MEDIUM
        archetypes = [s.archetype for s in template.slots]
        assert EnemyArchetype.TANK in archetypes
        assert EnemyArchetype.HEALER in archetypes

    def test_frozen(self) -> None:
        template = EncounterTemplate(
            template_id="test",
            difficulty=EncounterDifficulty.EASY,
            slots=(),
        )
        try:
            template.template_id = "changed"  # type: ignore[misc]
            assert False, "Should be frozen"
        except AttributeError:
            pass
