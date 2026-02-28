from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from src.core.attributes.attribute_types import AttributeType


@dataclass(frozen=True)
class ThresholdEntry:
    """Um marco de atributo que da bonus extra."""

    value: int
    tier: int
    bonuses: dict[str, int]


class ThresholdCalculator:
    """Calcula bonus extras ao atingir marcos de atributo."""

    def __init__(
        self, thresholds: dict[AttributeType, list[ThresholdEntry]]
    ) -> None:
        self._thresholds = thresholds

    @classmethod
    def from_json(cls, filepath: str) -> ThresholdCalculator:
        path = Path(filepath)
        raw = json.loads(path.read_text(encoding="utf-8"))
        thresholds = _parse_thresholds(raw)
        return cls(thresholds)

    def get_thresholds(self, attribute: AttributeType) -> list[ThresholdEntry]:
        return self._thresholds.get(attribute, [])

    def calculate_bonuses(
        self, attribute: AttributeType, value: int
    ) -> dict[str, int]:
        result: dict[str, int] = {}
        for entry in self.get_thresholds(attribute):
            if value >= entry.value:
                for bonus_name, bonus_value in entry.bonuses.items():
                    result[bonus_name] = result.get(bonus_name, 0) + bonus_value
        return result


def _parse_thresholds(
    raw: dict,
) -> dict[AttributeType, list[ThresholdEntry]]:
    thresholds: dict[AttributeType, list[ThresholdEntry]] = {}
    for attr_name, data in raw.items():
        attr_type = AttributeType[attr_name]
        entries = [
            ThresholdEntry(
                value=entry["value"],
                tier=entry["tier"],
                bonuses=dict(entry["bonuses"]),
            )
            for entry in data["thresholds"]
        ]
        thresholds[attr_type] = entries
    return thresholds
