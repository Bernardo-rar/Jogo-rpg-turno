"""Carrega skills do JSON."""

from __future__ import annotations

import json

from src.core._paths import resolve_data_path
from src.core.skills.skill import Skill

SKILLS_DATA_PATH = "data/skills/skills.json"


def load_skills(filepath: str = SKILLS_DATA_PATH) -> dict[str, Skill]:
    """Carrega todas as skills do JSON. Retorna dict skill_id -> Skill."""
    path = resolve_data_path(filepath)
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {
        skill_id: Skill.from_dict(skill_id, data)
        for skill_id, data in raw.items()
    }
