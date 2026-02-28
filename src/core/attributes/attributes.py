from __future__ import annotations

from src.core.attributes.attribute_types import AttributeType

MIN_ATTRIBUTE_VALUE = 0


class Attributes:
    """Container para os 7 atributos primarios de um personagem."""

    def __init__(self, values: dict[AttributeType, int] | None = None) -> None:
        self._values: dict[AttributeType, int] = {attr: 0 for attr in AttributeType}
        if values:
            for attr, value in values.items():
                self.set(attr, value)

    def get(self, attribute: AttributeType) -> int:
        return self._values[attribute]

    def set(self, attribute: AttributeType, value: int) -> None:
        if value < MIN_ATTRIBUTE_VALUE:
            raise ValueError(f"{attribute.name} nao pode ser negativo: {value}")
        self._values[attribute] = value

    def increase(self, attribute: AttributeType, amount: int) -> None:
        self.set(attribute, self.get(attribute) + amount)

    def decrease(self, attribute: AttributeType, amount: int) -> None:
        new_value = self.get(attribute) - amount
        if new_value < MIN_ATTRIBUTE_VALUE:
            raise ValueError(
                f"{attribute.name} ficaria negativo: {self.get(attribute)} - {amount}"
            )
        self._values[attribute] = new_value

    def to_dict(self) -> dict[AttributeType, int]:
        return dict(self._values)
