import pytest

from src.core.attributes.attribute_types import AttributeType
from src.core.attributes.attributes import Attributes


class TestAttributesCreation:
    def test_create_with_default_values(self):
        attrs = Attributes()
        assert attrs.get(AttributeType.STRENGTH) == 0

    def test_create_with_initial_values(self):
        values = {AttributeType.STRENGTH: 10, AttributeType.DEXTERITY: 8}
        attrs = Attributes(values)
        assert attrs.get(AttributeType.STRENGTH) == 10
        assert attrs.get(AttributeType.DEXTERITY) == 8

    def test_unset_attributes_default_to_zero(self):
        values = {AttributeType.STRENGTH: 10}
        attrs = Attributes(values)
        assert attrs.get(AttributeType.CONSTITUTION) == 0


class TestAttributesModification:
    def test_set_attribute_value(self):
        attrs = Attributes()
        attrs.set(AttributeType.STRENGTH, 15)
        assert attrs.get(AttributeType.STRENGTH) == 15

    def test_increase_attribute(self):
        attrs = Attributes({AttributeType.STRENGTH: 10})
        attrs.increase(AttributeType.STRENGTH, 3)
        assert attrs.get(AttributeType.STRENGTH) == 13

    def test_decrease_attribute(self):
        attrs = Attributes({AttributeType.STRENGTH: 10})
        attrs.decrease(AttributeType.STRENGTH, 2)
        assert attrs.get(AttributeType.STRENGTH) == 8


class TestAttributesValidation:
    def test_attribute_cannot_be_negative(self):
        attrs = Attributes()
        with pytest.raises(ValueError):
            attrs.set(AttributeType.STRENGTH, -1)

    def test_decrease_below_zero_raises_error(self):
        attrs = Attributes({AttributeType.STRENGTH: 2})
        with pytest.raises(ValueError):
            attrs.decrease(AttributeType.STRENGTH, 5)


class TestAttributesIteration:
    def test_to_dict_returns_all_attributes(self):
        values = {
            AttributeType.STRENGTH: 10,
            AttributeType.DEXTERITY: 8,
        }
        attrs = Attributes(values)
        result = attrs.to_dict()
        assert result[AttributeType.STRENGTH] == 10
        assert result[AttributeType.DEXTERITY] == 8
        assert result[AttributeType.CONSTITUTION] == 0
        assert len(result) == 7
