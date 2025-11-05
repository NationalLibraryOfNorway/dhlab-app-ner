"""Tests for generate_default_filename function."""

from app_helpers import generate_default_filename


def test_generate_default_filename():
    """Test generating default filename from URN and page range."""
    urn = "URN:NBN:no-nb_digibok_123456"
    start, stop = (10, 50)

    result = generate_default_filename(urn, start, stop)

    assert "123456" in result
    assert "10" in result
    assert "50" in result
    assert result.endswith(".xlsx")
