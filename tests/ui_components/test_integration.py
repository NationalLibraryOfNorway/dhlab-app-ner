"""
Integration tests for ui_components.

These tests verify that UI components can be imported and have correct signatures.
Full UI testing is done through the end-to-end tests in test_end_to_end.py.
"""

import pytest
import pandas as pd


@pytest.mark.integration
class TestDefineCorpusFromUIIntegration:
    """Integration tests for define_corpus_from_ui function."""

    def test_function_imports_successfully(self):
        """Test that the function can be imported."""
        from ui_components import define_corpus_from_ui

        assert callable(define_corpus_from_ui)

    def test_function_signature(self):
        """Test that function has correct signature."""
        from ui_components import define_corpus_from_ui
        import inspect

        sig = inspect.signature(define_corpus_from_ui)
        # Should return tuple[pd.DataFrame | None, list[str]]
        assert len(sig.parameters) == 0  # No parameters


@pytest.mark.integration
class TestRenderTextSelectionUIIntegration:
    """Integration tests for render_text_selection_ui function."""

    def test_function_imports_successfully(self):
        """Test that the function can be imported."""
        from ui_components import render_text_selection_ui

        assert callable(render_text_selection_ui)

    def test_function_returns_none_for_empty_choices(self):
        """Test that function handles empty choices correctly."""
        from ui_components import render_text_selection_ui

        # This should return None without Streamlit context
        # In actual Streamlit context, it would render UI
        result = render_text_selection_ui([])
        assert result is None


@pytest.mark.integration
class TestRenderAnalysisConfigUIIntegration:
    """Integration tests for render_analysis_config_ui function."""

    def test_function_imports_successfully(self):
        """Test that the function can be imported."""
        from ui_components import render_analysis_config_ui

        assert callable(render_analysis_config_ui)


@pytest.mark.integration
class TestDisplayDataframesInColumnsIntegration:
    """Integration tests for display_dataframes_in_columns function."""

    def test_function_imports_successfully(self):
        """Test that the function can be imported."""
        from ui_components import display_dataframes_in_columns

        assert callable(display_dataframes_in_columns)

    def test_function_handles_empty_types(self):
        """Test that function handles empty types list."""
        from ui_components import display_dataframes_in_columns

        df = pd.DataFrame({"token": ["test"], "frekv": [1]})
        lab_to_frame = {"Navn": df}

        # Should return early without error
        result = display_dataframes_in_columns([], lab_to_frame)
        assert result is None


@pytest.mark.integration
class TestRenderDownloadButtonIntegration:
    """Integration tests for render_download_button function."""

    def test_function_imports_successfully(self):
        """Test that the function can be imported."""
        from ui_components import render_download_button

        assert callable(render_download_button)
