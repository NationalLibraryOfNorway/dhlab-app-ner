"""
Tests for corpus definition and URN extraction logic.

These tests cover the functionality that will be extracted from the main app
into separate helper functions.
"""

import pandas as pd


class TestURNExtraction:
    """Test URN extraction from text."""

    def test_extract_urns_from_clean_text(self, sample_urns):
        """Test extracting URNs from a clean URN list."""
        from app_helpers import extract_urns_from_text

        text = "\n".join(sample_urns)
        result = extract_urns_from_text(text)

        assert len(result) == 3
        assert all(urn in result for urn in sample_urns)

    def test_extract_urns_from_mixed_content(
        self, urn_text_with_extra_content, sample_urns
    ):
        """Test extracting URNs from text with extra content."""
        from app_helpers import extract_urns_from_text

        result = extract_urns_from_text(urn_text_with_extra_content)

        assert len(result) == 3
        assert all(urn in result for urn in sample_urns)

    def test_extract_urns_empty_string(self):
        """Test extracting URNs from empty string."""
        from app_helpers import extract_urns_from_text

        result = extract_urns_from_text("")

        assert result == []

    def test_extract_urns_no_urns_found(self):
        """Test extracting URNs when none are present."""
        from app_helpers import extract_urns_from_text

        text = "This is just some random text with no URNs"
        result = extract_urns_from_text(text)

        assert result == []


class TestLabelMapping:
    """Test creation of label-to-dataframe mappings."""

    def test_create_ner_label_mapping(self, mock_ner_dataframe):
        """Test NER label mapping creation."""
        from app_helpers import create_ner_label_mapping

        # Split the mock dataframe into categories
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

        result = create_ner_label_mapping(
            personer, steder, organisasjoner, produkter, andre
        )

        assert "Navn" in result
        assert "Steder" in result
        assert "Organisasjoner" in result
        assert "Produkter" in result
        assert "Andre" in result
        assert len(result) == 5

    def test_create_pos_label_mapping(self, mock_pos_dataframe):
        """Test POS label mapping creation."""
        from app_helpers import create_pos_label_mapping

        # Split the mock dataframe into categories
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

        result = create_pos_label_mapping(noun, verb, adjektiv, prep, andre)

        assert "Substantiv" in result
        assert "Verb" in result
        assert "Adjektiv" in result
        assert "Preposisjon" in result
        assert "Andre" in result
        assert len(result) == 5


class TestChoicesGeneration:
    """Test generation of text choices from corpus."""

    def test_generate_choices_from_corpus(self, mock_corpus_dataframe):
        """Test generating choices list from corpus DataFrame."""
        from app_helpers import generate_choices_from_corpus

        choices = generate_choices_from_corpus(mock_corpus_dataframe)

        assert len(choices) == 2
        assert "Author One" in choices[0]
        assert "Book Title 1" in choices[0]
        assert "2020" in choices[0]
        assert "URN:NBN:no-nb_digibok_123" in choices[0]

    def test_generate_choices_empty_corpus(self):
        """Test generating choices from empty corpus."""
        from app_helpers import generate_choices_from_corpus

        empty_df = pd.DataFrame(columns=["authors", "title", "year", "urn"])
        choices = generate_choices_from_corpus(empty_df)

        assert choices == []


class TestFilenameValidation:
    """Test filename validation and correction."""

    def test_ensure_xlsx_extension_missing(self):
        """Test adding .xlsx extension when missing."""
        from app_helpers import ensure_xlsx_extension

        result = ensure_xlsx_extension("myfile")
        assert result == "myfile.xlsx"

    def test_ensure_xlsx_extension_present(self):
        """Test that existing .xlsx extension is preserved."""
        from app_helpers import ensure_xlsx_extension

        result = ensure_xlsx_extension("myfile.xlsx")
        assert result == "myfile.xlsx"

    def test_ensure_xlsx_extension_other_extension(self):
        """Test replacing non-.xlsx extension."""
        from app_helpers import ensure_xlsx_extension

        result = ensure_xlsx_extension("myfile.xls")
        assert result == "myfile.xls.xlsx"


class TestURNParsing:
    """Test parsing URN to extract identifiers."""

    def test_extract_urn_id(self):
        """Test extracting ID from URN."""
        from app_helpers import extract_urn_id

        urn = "URN:NBN:no-nb_digibok_123456"
        result = extract_urn_id(urn)

        # The function splits on "-" and takes the last part
        assert result == "nb_digibok_123456"

    def test_extract_urn_id_complex(self):
        """Test extracting ID from complex URN."""
        from app_helpers import extract_urn_id

        urn = "URN:NBN:no-nb_digibok_2023072145678"
        result = extract_urn_id(urn)

        # The function splits on "-" and takes the last part
        assert result == "nb_digibok_2023072145678"
