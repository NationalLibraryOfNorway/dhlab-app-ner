"""Tests for validate_page_range function."""

from app_helpers import validate_page_range


def test_validate_page_range_normal():
    """Test normal page range validation."""
    result = validate_page_range((10, 50), max_pages=100)
    assert result == (10, 50)


def test_validate_page_range_too_small():
    """Test that very small ranges are adjusted."""
    result = validate_page_range((0, 2), max_pages=100)
    assert result == (0, 4)


def test_validate_page_range_exceeds_max():
    """Test that ranges exceeding max are capped."""
    result = validate_page_range((0, 150), max_pages=100)
    assert result == (0, 100)


def test_validate_page_range_zero_max():
    """Test handling of zero or negative max pages."""
    # When max_pages is 0, it should be set to default 500
    # But if the range (0, 100) is within that, it stays (0, 100)
    result = validate_page_range((0, 100), max_pages=0)
    assert result == (0, 100)  # Range is valid, so not changed
