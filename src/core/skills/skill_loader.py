"""Carrega skills do JSON."""

from __future__ import annotations

import json

from src.core._paths import resolve_data_path
from src.core.skills.skill import Skill

SKILLS_DATA_PATH = "data/skills/skills.json"
CLASS_SKILLS_DIR = "data/skills"


def load_skills(filepath: str = SKILLS_DATA_PATH) -> dict[str, Skill]:
    """Carrega todas as skills do JSON. Retorna dict skill_id -> Skill."""
    path = resolve_data_path(filepath)
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {
        skill_id: Skill.from_dict(skill_id, data)
        for skill_id, data in raw.items()
    }


def load_class_skills(class_id: str) -> dict[str, Skill]:
    """Carrega skills de uma classe especifica de data/skills/<class_id>.json."""
    filepath = f"{CLASS_SKILLS_DIR}/{class_id}.json"
    path = resolve_data_path(filepath)
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {
        skill_id: Skill.from_dict(skill_id, data)
        for skill_id, data in raw.items()
    }
