"""
Test utilities and fixtures for app tests.

These will be used to test the refactored functions.
"""

import pandas as pd
import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_corpus_dataframe():
    """Create a mock corpus DataFrame."""
    return pd.DataFrame({
        'authors': [['Author One'], ['Author Two']],
        'title': ['Book Title 1', 'Book Title 2'],
        'year': [2020, 2021],
        'urn': ['URN:NBN:no-nb_digibok_123', 'URN:NBN:no-nb_digibok_456']
    })


@pytest.fixture
def mock_ner_dataframe():
    """Create a mock NER results DataFrame."""
    data = {
        'token': ['Oslo', 'Norge', 'Microsoft', 'iPhone', 'xyz'],
        'ner': ['B-LOC', 'B-LOC', 'B-ORG', 'B-PROD', 'B-MISC'],
        'frekv': [10, 5, 3, 2, 1]
    }
    return pd.DataFrame(data).set_index('token')


@pytest.fixture
def mock_pos_dataframe():
    """Create a mock POS results DataFrame."""
    data = {
        'token': ['hus', 'løpe', 'rød', 'på', 'xyz'],
        'pos': ['NOUN', 'VERB', 'ADJ', 'ADP', 'PUNCT'],
        'frekv': [10, 5, 3, 2, 1]
    }
    return pd.DataFrame(data).set_index('token')


@pytest.fixture
def sample_urns():
    """Sample URN strings for testing."""
    return [
        'URN:NBN:no-nb_digibok_123',
        'URN:NBN:no-nb_digibok_456',
        'URN:NBN:no-nb_digibok_789'
    ]


@pytest.fixture
def urn_text_with_extra_content():
    """Text containing URNs along with other content."""
    return """
    Her er noen URNer:
    URN:NBN:no-nb_digibok_123, URN:NBN:no-nb_digibok_456
    og mer tekst her.
    URN:NBN:no-nb_digibok_789.
    """


@pytest.fixture
def mock_excel_file_content():
    """Mock Excel file content with URNs."""
    df = pd.DataFrame({
        'urn': ['URN:NBN:no-nb_digibok_123', 'URN:NBN:no-nb_digibok_456'],
        'title': ['Title 1', 'Title 2']
    })
    return df
