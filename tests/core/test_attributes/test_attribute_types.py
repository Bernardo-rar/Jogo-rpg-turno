from src.core.attributes.attribute_types import AttributeType


class TestAttributeType:
    def test_has_seven_primary_attributes(self):
        attributes = list(AttributeType)
        assert len(attributes) == 7

    def test_strength_exists(self):
        assert AttributeType.STRENGTH is not None

    def test_dexterity_exists(self):
        assert AttributeType.DEXTERITY is not None

    def test_constitution_exists(self):
        assert AttributeType.CONSTITUTION is not None

    def test_intelligence_exists(self):
        assert AttributeType.INTELLIGENCE is not None

    def test_wisdom_exists(self):
        assert AttributeType.WISDOM is not None

    def test_charisma_exists(self):
        assert AttributeType.CHARISMA is not None

    def test_mind_exists(self):
        assert AttributeType.MIND is not None
