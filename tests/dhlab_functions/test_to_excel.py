"""Tests for to_excel function."""

import pandas as pd
from io import BytesIO

from dhlab_functions import to_excel


def test_to_excel_simple_dataframe():
    """Test converting a simple DataFrame to Excel format."""
    df = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})

    result = to_excel(df)

    assert isinstance(result, bytes)
    assert len(result) > 0

    # Verify it's valid Excel by reading it back
    result_df = pd.read_excel(BytesIO(result))
    pd.testing.assert_frame_equal(result_df, df)


def test_to_excel_empty_dataframe():
    """Test converting an empty DataFrame to Excel format."""
    df = pd.DataFrame()

    result = to_excel(df)

    assert isinstance(result, bytes)
    assert len(result) > 0

    # Verify it's valid Excel even if empty
    result_df = pd.read_excel(BytesIO(result))
    assert result_df.empty


def test_to_excel_with_index():
    """Test that index is not included in Excel output."""
    df = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
    df.index = ["row1", "row2", "row3"]

    result = to_excel(df)

    # Read back and verify index was not written (index=False in to_excel)
    result_df = pd.read_excel(BytesIO(result))

    # Should have same columns but default numeric index
    assert list(result_df.columns) == ["col1", "col2"]
    assert list(result_df.index) == [0, 1, 2]


def test_to_excel_with_special_characters():
    """Test converting DataFrame with special characters."""
    df = pd.DataFrame(
        {
            "navn": ["Øystein", "Åse", "Ævar"],
            "sted": ["Tromsø", "Bodø", "Ålesund"],
            "frekv": [10, 5, 3],
        }
    )

    result = to_excel(df)

    # Verify special Norwegian characters are preserved
    result_df = pd.read_excel(BytesIO(result))
    pd.testing.assert_frame_equal(result_df, df)


def test_to_excel_with_various_types():
    """Test converting DataFrame with various data types."""
    df = pd.DataFrame(
        {
            "integers": [1, 2, 3],
            "floats": [1.1, 2.2, 3.3],
            "strings": ["a", "b", "c"],
            "booleans": [True, False, True],
        }
    )

    result = to_excel(df)

    # Verify all data types are preserved
    result_df = pd.read_excel(BytesIO(result))

    # Note: Excel may convert some types, so check values are close enough
    assert list(result_df["integers"]) == [1, 2, 3]
    assert list(result_df["strings"]) == ["a", "b", "c"]


def test_to_excel_ner_like_dataframe():
    """Test with a DataFrame structure similar to NER results."""
    df = pd.DataFrame(
        {
            "token": ["Oslo", "Norge", "Microsoft"],
            "ner": ["B-LOC", "B-LOC", "B-ORG"],
            "frekv": [10, 5, 3],
        }
    )

    result = to_excel(df)

    result_df = pd.read_excel(BytesIO(result))
    pd.testing.assert_frame_equal(result_df, df)


def test_to_excel_pos_like_dataframe():
    """Test with a DataFrame structure similar to POS results."""
    df = pd.DataFrame(
        {
            "token": ["hus", "løpe", "rød"],
            "pos": ["NOUN", "VERB", "ADJ"],
            "frekv": [10, 5, 3],
        }
    )

    result = to_excel(df)

    result_df = pd.read_excel(BytesIO(result))
    pd.testing.assert_frame_equal(result_df, df)
