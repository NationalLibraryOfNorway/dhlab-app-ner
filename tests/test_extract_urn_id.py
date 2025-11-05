"""Tests for extract_urn_id function."""

from app_helpers import extract_urn_id


def test_extract_urn_id():
    """Test extracting ID from URN."""
    urn = "URN:NBN:no-nb_digibok_123456"
    result = extract_urn_id(urn)

    # The function splits on "-" and takes the last part
    assert result == "nb_digibok_123456"
