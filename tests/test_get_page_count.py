"""Tests for get_page_count function with mocked HTTP requests."""

from unittest.mock import Mock, patch
from document_utils import get_page_count


class TestGetPageCount:
    """Test suite for get_page_count function."""

    @patch("document_utils.requests.get")
    def test_get_page_count_success(self, mock_get):
        """Test successful page count retrieval."""
        # Arrange
        urn = "URN:NBN:no-nb_digibok_2023010101234"
        mock_response = Mock()
        mock_response.text = "<mods><physicalDescription><extent>250 pages</extent></physicalDescription></mods>"
        mock_get.return_value = mock_response

        # Act
        result = get_page_count(urn)

        # Assert
        assert result == 250
        mock_get.assert_called_once_with(
            f"https://api.nb.no/catalog/v1/metadata/{urn}/mods"
        )

    @patch("document_utils.requests.get")
    def test_get_page_count_with_different_formats(self, mock_get):
        """Test page count extraction with various extent formats."""
        test_cases = [
            ("<extent>100 s.</extent>", 100),
            ("<extent>42 pages</extent>", 42),
            ("<extent>999</extent>", 999),
            ("<extent>1 page</extent>", 1),
        ]

        for extent_xml, expected_count in test_cases:
            # Arrange
            urn = "URN:NBN:no-nb_digibok_test"
            mock_response = Mock()
            mock_response.text = f"<mods>{extent_xml}</mods>"
            mock_get.return_value = mock_response

            # Act
            result = get_page_count(urn)

            # Assert
            assert result == expected_count, f"Failed for XML: {extent_xml}"

    @patch("document_utils.requests.get")
    def test_get_page_count_no_extent_tag(self, mock_get):
        """Test when extent tag is missing from response."""
        # Arrange
        urn = "URN:NBN:no-nb_digibok_noextent"
        mock_response = Mock()
        mock_response.text = "<mods><title>Some Book</title></mods>"
        mock_get.return_value = mock_response

        # Act
        result = get_page_count(urn)

        # Assert
        assert result == -1

    @patch("document_utils.requests.get")
    def test_get_page_count_empty_response(self, mock_get):
        """Test when API returns empty response."""
        # Arrange
        urn = "URN:NBN:no-nb_digibok_empty"
        mock_response = Mock()
        mock_response.text = ""
        mock_get.return_value = mock_response

        # Act
        result = get_page_count(urn)

        # Assert
        assert result == -1

    @patch("document_utils.requests.get")
    def test_get_page_count_request_exception(self, mock_get):
        """Test when requests.get raises an exception."""
        # Arrange
        urn = "URN:NBN:no-nb_digibok_error"
        mock_get.side_effect = Exception("Network error")

        # Act
        result = get_page_count(urn)

        # Assert
        assert result == -1

    @patch("document_utils.requests.get")
    def test_get_page_count_timeout(self, mock_get):
        """Test when request times out."""
        # Arrange
        urn = "URN:NBN:no-nb_digibok_timeout"
        import requests

        mock_get.side_effect = requests.Timeout("Request timed out")

        # Act
        result = get_page_count(urn)

        # Assert
        assert result == -1

    @patch("document_utils.requests.get")
    def test_get_page_count_connection_error(self, mock_get):
        """Test when connection fails."""
        # Arrange
        urn = "URN:NBN:no-nb_digibok_connection"
        import requests

        mock_get.side_effect = requests.ConnectionError("Connection failed")

        # Act
        result = get_page_count(urn)

        # Assert
        assert result == -1

    @patch("document_utils.requests.get")
    def test_get_page_count_invalid_xml(self, mock_get):
        """Test when response contains malformed XML."""
        # Arrange
        urn = "URN:NBN:no-nb_digibok_invalid"
        mock_response = Mock()
        mock_response.text = "<extent>not a number</extent>"
        mock_get.return_value = mock_response

        # Act
        result = get_page_count(urn)

        # Assert
        assert result == -1

    @patch("document_utils.requests.get")
    def test_get_page_count_multiple_extent_tags(self, mock_get):
        """Test when multiple extent tags exist (should return first match)."""
        # Arrange
        urn = "URN:NBN:no-nb_digibok_multiple"
        mock_response = Mock()
        mock_response.text = """<mods>
            <extent>150 pages</extent>
            <extent>200 pages</extent>
        </mods>"""
        mock_get.return_value = mock_response

        # Act
        result = get_page_count(urn)

        # Assert
        assert result == 150  # Should return the first match

    @patch("document_utils.requests.get")
    def test_get_page_count_constructs_correct_url(self, mock_get):
        """Test that the correct API URL is constructed."""
        # Arrange
        urn = "URN:NBN:no-nb_digibok_2023010101234"
        expected_url = "https://api.nb.no/catalog/v1/metadata/URN:NBN:no-nb_digibok_2023010101234/mods"
        mock_response = Mock()
        mock_response.text = "<extent>100 pages</extent>"
        mock_get.return_value = mock_response

        # Act
        get_page_count(urn)

        # Assert
        mock_get.assert_called_once_with(expected_url)

    @patch("document_utils.requests.get")
    def test_get_page_count_return_type_is_int(self, mock_get):
        """Test that return type is always int."""
        # Test success case
        urn = "URN:NBN:no-nb_digibok_typecheck"
        mock_response = Mock()
        mock_response.text = "<extent>100 pages</extent>"
        mock_get.return_value = mock_response

        result = get_page_count(urn)
        assert isinstance(result, int)

        # Test error case
        mock_get.side_effect = Exception("Error")
        result = get_page_count(urn)
        assert isinstance(result, int)
        assert result == -1
