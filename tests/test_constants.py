"""
Tests for constants and configuration values.
"""


class TestConstants:
    """Test application constants."""

    def test_ner_options_constant(self):
        """Test NER options are correctly defined."""
        from app_helpers import NER_OPTIONS

        assert NER_OPTIONS == ["Navn", "Steder", "Organisasjoner", "Produkter", "Andre"]
        assert len(NER_OPTIONS) == 5

    def test_pos_options_constant(self):
        """Test POS options are correctly defined."""
        from app_helpers import POS_OPTIONS

        assert POS_OPTIONS == ["Substantiv", "Verb", "Adjektiv", "Preposisjon", "Andre"]
        assert len(POS_OPTIONS) == 5


class TestGetSelectionOptions:
    """Test getting selection options based on analysis type."""

    def test_get_selection_options_ner(self):
        """Test getting selection options for NER analysis."""
        from app_helpers import get_selection_options

        result = get_selection_options("NER")

        assert result == ["Navn", "Steder", "Organisasjoner", "Produkter", "Andre"]

    def test_get_selection_options_pos(self):
        """Test getting selection options for POS analysis."""
        from app_helpers import get_selection_options

        result = get_selection_options("POS")

        assert result == ["Substantiv", "Verb", "Adjektiv", "Preposisjon", "Andre"]

    def test_get_selection_options_invalid(self):
        """Test getting selection options for invalid type."""
        from app_helpers import get_selection_options

        # Should default to NER or raise error
        result = get_selection_options("INVALID")

        # Depending on implementation, this might return NER options or raise
        assert isinstance(result, list)
