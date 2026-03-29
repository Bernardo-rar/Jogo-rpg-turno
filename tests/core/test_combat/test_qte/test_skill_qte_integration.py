"""Tests for QTE integration into Skill dataclass."""

from src.core.skills.skill import Skill


class TestSkillQteParsing:

    def test_skill_without_qte_has_none(self) -> None:
        data = {
            "name": "Fire Bolt",
            "mana_cost": 10,
            "action_type": "ACTION",
            "target_type": "SINGLE_ENEMY",
            "effects": [{"effect_type": "DAMAGE", "base_power": 25}],
            "slot_cost": 3,
        }
        skill = Skill.from_dict("fire_bolt", data)
        assert skill.qte is None

    def test_skill_with_qte_parses(self) -> None:
        data = {
            "name": "Legend",
            "mana_cost": 10,
            "action_type": "ACTION",
            "target_type": "SINGLE_ENEMY",
            "effects": [{"effect_type": "DAMAGE", "base_power": 80}],
            "slot_cost": 8,
            "qte": {
                "keys": ["LEFT", "RIGHT", "UP", "DOWN"],
                "time_window_ms": 2500,
                "difficulty": "HARD",
            },
        }
        skill = Skill.from_dict("legend", data)
        assert skill.qte is not None
        assert skill.qte.keys == ("LEFT", "RIGHT", "UP", "DOWN")
        assert skill.qte.time_window_ms == 2500
        assert skill.qte.difficulty == "HARD"

    def test_skill_qte_defaults(self) -> None:
        data = {
            "name": "Quick",
            "mana_cost": 5,
            "action_type": "ACTION",
            "target_type": "SINGLE_ENEMY",
            "effects": [{"effect_type": "DAMAGE", "base_power": 40}],
            "slot_cost": 5,
            "qte": {"keys": ["UP"]},
        }
        skill = Skill.from_dict("quick", data)
        assert skill.qte is not None
        assert skill.qte.time_window_ms == 2500
        assert skill.qte.difficulty == "MEDIUM"
