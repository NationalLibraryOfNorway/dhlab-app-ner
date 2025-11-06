"""Tests for process_ner_analysis function."""

from unittest.mock import patch

from document_utils import process_ner_analysis


@patch("document_utils.get_ner")
def test_process_ner_analysis(mock_get_ner, mock_ner_dataframe):
    """Test NER analysis processing."""
    # Setup mock
    personer = mock_ner_dataframe[mock_ner_dataframe["ner"].str.contains("PER")]
    steder = mock_ner_dataframe[mock_ner_dataframe["ner"].str.contains("LOC")]
    organisasjoner = mock_ner_dataframe[mock_ner_dataframe["ner"].str.contains("ORG")]
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
