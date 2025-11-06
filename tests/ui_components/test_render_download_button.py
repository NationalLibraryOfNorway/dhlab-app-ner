"""Tests for render_download_button function."""

import pandas as pd
from unittest.mock import patch
from ui_components import render_download_button


class TestRenderDownloadButton:
    """Test suite for render_download_button function."""

    @patch("ui_components.st")
    @patch("ui_components.to_excel")
    def test_render_download_button_basic(self, mock_to_excel, mock_st):
        """Test basic download button rendering."""
        # Arrange
        df = pd.DataFrame({"token": ["Oslo", "Bergen"], "frekv": [10, 5]})
        df = df.set_index("token")
        filename = "test_output.xlsx"

        mock_excel_data = b"fake_excel_data"
        mock_to_excel.return_value = mock_excel_data

        # Act
        render_download_button(df, filename)

        # Assert
        mock_st.download_button.assert_called_once()
        call_args = mock_st.download_button.call_args

        # Check that the button label contains the filename
        assert filename in call_args[0][0]
        # Check that excel data is passed
        assert call_args[0][1] == mock_excel_data
        # Check that filename is passed
        assert call_args[0][2] == filename

        # Verify that to_excel was called with reset index
        mock_to_excel.assert_called_once()
        excel_call_df = mock_to_excel.call_args[0][0]
        assert "token" in excel_call_df.columns  # Index should be reset

    @patch("ui_components.st")
    @patch("ui_components.to_excel")
    def test_render_download_button_with_help_text(self, mock_to_excel, mock_st):
        """Test that download button includes help text."""
        # Arrange
        df = pd.DataFrame({"token": ["test"], "frekv": [1]})
        df = df.set_index("token")
        filename = "output.xlsx"

        mock_to_excel.return_value = b"data"

        # Act
        render_download_button(df, filename)

        # Assert
        call_kwargs = mock_st.download_button.call_args[1]
        assert "help" in call_kwargs
        assert "Excel" in call_kwargs["help"]

    @patch("ui_components.st")
    @patch("ui_components.to_excel")
    def test_render_download_button_with_different_filenames(
        self, mock_to_excel, mock_st
    ):
        """Test download button with various filenames."""
        # Arrange
        df = pd.DataFrame({"token": ["a"], "frekv": [1]})
        df = df.set_index("token")
        mock_to_excel.return_value = b"data"

        filenames = [
            "ner_results.xlsx",
            "pos_analysis.xlsx",
            "123456_0_100.xlsx",
            "custom_name.xlsx",
        ]

        for filename in filenames:
            mock_st.reset_mock()

            # Act
            render_download_button(df, filename)

            # Assert
            call_args = mock_st.download_button.call_args
            assert call_args[0][2] == filename

    @patch("ui_components.st")
    @patch("ui_components.to_excel")
    def test_render_download_button_large_dataframe(self, mock_to_excel, mock_st):
        """Test download button with large dataframe."""
        # Arrange
        df = pd.DataFrame(
            {
                "token": [f"word_{i}" for i in range(1000)],
                "frekv": list(range(1000, 0, -1)),
            }
        )
        df = df.set_index("token")
        filename = "large_output.xlsx"

        mock_to_excel.return_value = b"large_data"

        # Act
        render_download_button(df, filename)

        # Assert
        mock_to_excel.assert_called_once()
        # Verify the dataframe passed has reset index
        excel_call_df = mock_to_excel.call_args[0][0]
        assert len(excel_call_df) == 1000
        assert "token" in excel_call_df.columns

    @patch("ui_components.st")
    @patch("ui_components.to_excel")
    def test_render_download_button_empty_dataframe(self, mock_to_excel, mock_st):
        """Test download button with empty dataframe."""
        # Arrange
        df = pd.DataFrame({"token": [], "frekv": []})
        df = df.set_index("token") if len(df) > 0 else df
        filename = "empty.xlsx"

        mock_to_excel.return_value = b"empty_data"

        # Act
        render_download_button(df, filename)

        # Assert
        mock_st.download_button.assert_called_once()
        mock_to_excel.assert_called_once()
