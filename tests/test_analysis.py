"""
Tests for analysis processing functions.

These tests verify the NER and POS analysis processing logic.
"""

from unittest.mock import patch


class TestAnalysisProcessing:
    """Test analysis processing functions."""

    @patch("app_helpers.get_ner")
    def test_process_ner_analysis(self, mock_get_ner, mock_ner_dataframe):
        """Test NER analysis processing."""
        from app_helpers import process_ner_analysis

        # Setup mock
        personer = mock_ner_dataframe[mock_ner_dataframe["ner"].str.contains("PER")]
        steder = mock_ner_dataframe[mock_ner_dataframe["ner"].str.contains("LOC")]
        organisasjoner = mock_ner_dataframe[
            mock_ner_dataframe["ner"].str.contains("ORG")
        ]
        produkter = mock_ner_dataframe[mock_ner_dataframe["ner"].str.contains("PROD")]
        andre = mock_ner_dataframe[
            (~mock_ner_dataframe["ner"].str.contains("PER"))
            & (~mock_ner_dataframe["ner"].str.contains("ORG"))
            & (~mock_ner_dataframe["ner"].str.contains("PROD"))
            & (~mock_ner_dataframe["ner"].str.contains("LOC"))
        ]

        mock_get_ner.return_value = (
            mock_ner_dataframe,
            personer,
            steder,
            organisasjoner,
            produkter,
            andre,
        )

        # Execute
        df, lab_to_frame = process_ner_analysis(
            urn="URN:NBN:no-nb_digibok_123", model="nb_core_news_sm", start_to=(0, 100)
        )

        # Verify
        assert df is not None
        assert isinstance(lab_to_frame, dict)
        assert "Navn" in lab_to_frame
        assert "Steder" in lab_to_frame
        assert "Organisasjoner" in lab_to_frame
        assert "Produkter" in lab_to_frame
        assert "Andre" in lab_to_frame

    @patch("app_helpers.get_pos")
    def test_process_pos_analysis(self, mock_get_pos, mock_pos_dataframe):
        """Test POS analysis processing."""
        from app_helpers import process_pos_analysis

        # Setup mock
        noun = mock_pos_dataframe[mock_pos_dataframe["pos"].str.contains("NOUN")]
        verb = mock_pos_dataframe[mock_pos_dataframe["pos"].str.contains("VERB")]
        adjektiv = mock_pos_dataframe[mock_pos_dataframe["pos"].str.contains("ADJ")]
        prep = mock_pos_dataframe[mock_pos_dataframe["pos"].str.contains("ADP")]
        andre = mock_pos_dataframe[
            (~mock_pos_dataframe["pos"].str.contains("NOUN"))
            & (~mock_pos_dataframe["pos"].str.contains("VERB"))
            & (~mock_pos_dataframe["pos"].str.contains("ADJ"))
            & (~mock_pos_dataframe["pos"].str.contains("ADP"))
        ]

        mock_get_pos.return_value = (
            mock_pos_dataframe,
            noun,
            verb,
            adjektiv,
            prep,
            andre,
        )

        # Execute
        df, lab_to_frame = process_pos_analysis(
            urn="URN:NBN:no-nb_digibok_123", model="nb_core_news_sm", start_to=(0, 100)
        )

        # Verify
        assert df is not None
        assert isinstance(lab_to_frame, dict)
        assert "Substantiv" in lab_to_frame
        assert "Verb" in lab_to_frame
        assert "Adjektiv" in lab_to_frame
        assert "Preposisjon" in lab_to_frame
        assert "Andre" in lab_to_frame


class TestPageRangeValidation:
    """Test page range validation."""

    def test_validate_page_range_normal(self):
        """Test normal page range validation."""
        from app_helpers import validate_page_range

        result = validate_page_range((10, 50), max_pages=100)
        assert result == (10, 50)

    def test_validate_page_range_too_small(self):
        """Test that very small ranges are adjusted."""
        from app_helpers import validate_page_range

        result = validate_page_range((0, 2), max_pages=100)
        assert result == (0, 4)

    def test_validate_page_range_exceeds_max(self):
        """Test that ranges exceeding max are capped."""
        from app_helpers import validate_page_range

        result = validate_page_range((0, 150), max_pages=100)
        assert result == (0, 100)

    def test_validate_page_range_zero_max(self):
        """Test handling of zero or negative max pages."""
        from app_helpers import validate_page_range

        # When max_pages is 0, it should be set to default 500
        # But if the range (0, 100) is within that, it stays (0, 100)
        result = validate_page_range((0, 100), max_pages=0)
        assert result == (0, 100)  # Range is valid, so not changed


class TestDefaultFilename:
    """Test default filename generation."""

    def test_generate_default_filename(self):
        """Test generating default filename from URN and page range."""
        from app_helpers import generate_default_filename

        urn = "URN:NBN:no-nb_digibok_123456"
        start_to = (10, 50)

        result = generate_default_filename(urn, start_to)

        assert "123456" in result
        assert "10" in result
        assert "50" in result
        assert result.endswith(".xlsx")

    def test_generate_default_filename_full_range(self):
        """Test generating filename for full document."""
        from app_helpers import generate_default_filename

        urn = "URN:NBN:no-nb_digibok_789"
        start_to = (0, 200)

        result = generate_default_filename(urn, start_to)

        assert "789" in result
        assert "0" in result
        assert "200" in result
