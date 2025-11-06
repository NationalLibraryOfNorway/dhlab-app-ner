"""Tests for extract_urns_from_text function."""

from document_utils import extract_urns_from_text


def test_extract_urns_from_clean_text(sample_urns):
    """Test extracting URNs from a clean URN list."""
    text = "\n".join(sample_urns)
    result = extract_urns_from_text(text)

    assert len(result) == 3
    assert all(urn in result for urn in sample_urns)


def test_extract_urns_from_mixed_content(urn_text_with_extra_content, sample_urns):
    """Test extracting URNs from text with extra content."""
    result = extract_urns_from_text(urn_text_with_extra_content)

    assert len(result) == 3
    assert all(urn in result for urn in sample_urns)


def test_extract_urns_empty_string():
    """Test extracting URNs from empty string."""
    result = extract_urns_from_text("")

    assert result == []


def test_extract_urns_no_urns_found():
    """Test extracting URNs when none are present."""
    text = "This is just some random text with no URNs"
    result = extract_urns_from_text(text)

    assert result == []
