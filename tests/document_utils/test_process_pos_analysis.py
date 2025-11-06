"""Tests for process_pos_analysis function."""

from unittest.mock import patch

from document_utils import process_pos_analysis


@patch("document_utils.get_pos")
def test_process_pos_analysis(mock_get_pos, mock_pos_dataframe):
    """Test POS analysis processing."""
    # Setup mock
    noun = mock_pos_dataframe[mock_pos_dataframe["pos"].str.contains("NOUN")]
    verb = mock_pos_dataframe[mock_pos_dataframe["pos"].str.contains("VERB")]
    adjective = mock_pos_dataframe[mock_pos_dataframe["pos"].str.contains("ADJ")]
    prep = mock_pos_dataframe[mock_pos_dataframe["pos"].str.contains("ADP")]
    others = mock_pos_dataframe[
        (~mock_pos_dataframe["pos"].str.contains("NOUN"))
        & (~mock_pos_dataframe["pos"].str.contains("VERB"))
        & (~mock_pos_dataframe["pos"].str.contains("ADJ"))
        & (~mock_pos_dataframe["pos"].str.contains("ADP"))
    ]

    mock_get_pos.return_value = (
        mock_pos_dataframe,
        noun,
        verb,
        adjective,
        prep,
        others,
    )

    # Execute
    df, lab_to_frame = process_pos_analysis(
        urn="URN:NBN:no-nb_digibok_123",
        model="nb_core_news_sm",
        selected_start_page=0,
        selected_stop_page=100,
    )

    # Verify
    assert df is not None
    assert isinstance(lab_to_frame, dict)
    assert "Substantiv" in lab_to_frame
    assert "Verb" in lab_to_frame
    assert "Adjektiv" in lab_to_frame
    assert "Preposisjon" in lab_to_frame
    assert "Andre" in lab_to_frame
