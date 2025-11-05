"""Tests for generate_choices_from_corpus function."""

import pandas as pd

from app_helpers import generate_choices_from_corpus


def test_generate_choices_from_corpus(mock_corpus_dataframe):
    """Test generating choices list from corpus DataFrame."""
    choices = generate_choices_from_corpus(mock_corpus_dataframe)

    assert len(choices) == 2
    assert "Author One" in choices[0]
    assert "Book Title 1" in choices[0]
    assert "2020" in choices[0]
    assert "URN:NBN:no-nb_digibok_123" in choices[0]


def test_generate_choices_empty_corpus():
    """Test generating choices from empty corpus."""
    empty_df = pd.DataFrame(columns=["authors", "title", "year", "urn"])
    choices = generate_choices_from_corpus(empty_df)

    assert choices == []
