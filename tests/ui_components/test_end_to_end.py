"""
End-to-end integration tests for the NER/POS analysis application.

These tests verify complete user workflows from corpus selection to analysis results.
They can be run manually or as part of a CI/CD pipeline with proper setup.
"""

import pytest
import pandas as pd
from unittest.mock import patch


@pytest.mark.integration
class TestWorkflowIntegration:
    """Test complete user workflows."""

    def test_document_utils_workflow(self):
        """Test the complete document processing workflow."""
        from document_utils import (
            extract_urns_from_text,
            generate_choices_from_corpus,
            generate_default_filename,
            ensure_xlsx_extension,
            validate_page_range,
        )

        # Step 1: Extract URNs from user input
        text = "Check out this document: URN:NBN:no-nb_digibok_2023010101234"
        urns = extract_urns_from_text(text)
        assert len(urns) == 1
        assert urns[0] == "URN:NBN:no-nb_digibok_2023010101234"

        # Step 2: Create corpus choices (simulated)
        corpus_df = pd.DataFrame(
            {
                "authors": ["Test Author"],
                "title": ["Test Title"],
                "year": [2023],
                "urn": [urns[0]],
            }
        )
        choices = generate_choices_from_corpus(corpus_df)
        assert len(choices) == 1
        assert "Test Author" in choices[0]

        # Step 3: Get page count (would normally call API)
        # We'll skip actual API call in test

        # Step 4: Generate filename
        filename = generate_default_filename(urns[0], 0, 100)
        assert filename.endswith(".xlsx")
        assert "2023010101234" in filename

        # Step 5: Ensure proper extension
        final_filename = ensure_xlsx_extension(filename)
        assert final_filename.endswith(".xlsx")

        # Step 6: Validate page range
        validated_range = validate_page_range((0, 100), 200)
        assert validated_range == (0, 100)

    @patch("document_utils.get_ner")
    def test_ner_analysis_workflow(self, mock_get_ner):
        """Test NER analysis workflow."""
        from document_utils import process_ner_analysis

        # Mock NER results
        mock_df = pd.DataFrame(
            {
                "token": ["Oslo", "Bergen", "Norge", "NB", "Ibsen"],
                "ner": ["LOC", "LOC", "LOC", "ORG", "PER"],
                "frekv": [10, 8, 15, 5, 12],
            }
        ).set_index("token")

        mock_personer = mock_df[mock_df["ner"] == "PER"]
        mock_steder = mock_df[mock_df["ner"] == "LOC"]
        mock_org = mock_df[mock_df["ner"] == "ORG"]
        mock_produkter = pd.DataFrame(columns=["ner", "frekv"])
        mock_andre = pd.DataFrame(columns=["ner", "frekv"])

        mock_get_ner.return_value = (
            mock_df,
            mock_personer,
            mock_steder,
            mock_org,
            mock_produkter,
            mock_andre,
        )

        # Process NER analysis
        df, lab_to_frame = process_ner_analysis(
            "URN:NBN:no-nb_digibok_123456", "nb_core_news_lg", (0, 100)
        )

        # Verify results
        assert df is not None
        assert len(df) == 5
        assert "Navn" in lab_to_frame
        assert "Steder" in lab_to_frame
        assert len(lab_to_frame["Steder"]) == 3
        assert len(lab_to_frame["Navn"]) == 1

    @patch("document_utils.get_pos")
    def test_pos_analysis_workflow(self, mock_get_pos):
        """Test POS analysis workflow."""
        from document_utils import process_pos_analysis

        # Mock POS results
        mock_df = pd.DataFrame(
            {
                "token": ["hus", "bil", "løpe", "stor"],
                "pos": ["NOUN", "NOUN", "VERB", "ADJ"],
                "frekv": [20, 15, 10, 8],
            }
        ).set_index("token")

        mock_noun = mock_df[mock_df["pos"] == "NOUN"]
        mock_verb = mock_df[mock_df["pos"] == "VERB"]
        mock_adj = mock_df[mock_df["pos"] == "ADJ"]
        mock_prep = pd.DataFrame(columns=["pos", "frekv"])
        mock_andre = pd.DataFrame(columns=["pos", "frekv"])

        mock_get_pos.return_value = (
            mock_df,
            mock_noun,
            mock_verb,
            mock_adj,
            mock_prep,
            mock_andre,
        )

        # Process POS analysis
        df, lab_to_frame = process_pos_analysis(
            "URN:NBN:no-nb_digibok_123456", "nb_core_news_lg", (0, 100)
        )

        # Verify results
        assert df is not None
        assert "Substantiv" in lab_to_frame
        assert "Verb" in lab_to_frame
        assert len(lab_to_frame["Substantiv"]) == 2
        assert len(lab_to_frame["Verb"]) == 1

    def test_excel_export_workflow(self):
        """Test Excel export workflow."""
        from dhlab_functions import to_excel

        # Create test data
        df = pd.DataFrame(
            {"token": ["Oslo", "Bergen", "Trondheim"], "frekv": [10, 8, 6]}
        )

        # Generate Excel (will actually create Excel bytes)
        result = to_excel(df)

        # Verify Excel was created
        assert result is not None
        assert isinstance(result, bytes)
        assert len(result) > 0  # Should have content

    def test_label_mapping_workflow(self):
        """Test creating label mappings for results display."""
        from document_utils import create_ner_label_mapping, create_pos_label_mapping

        # Create test dataframes
        df_person = pd.DataFrame({"token": ["Ibsen"], "frekv": [5]})
        df_loc = pd.DataFrame({"token": ["Oslo"], "frekv": [10]})
        df_org = pd.DataFrame({"token": ["NB"], "frekv": [3]})
        df_prod = pd.DataFrame({"token": ["iPhone"], "frekv": [2]})
        df_other = pd.DataFrame({"token": ["misc"], "frekv": [1]})

        # Create NER mapping
        ner_mapping = create_ner_label_mapping(
            df_person, df_loc, df_org, df_prod, df_other
        )

        assert len(ner_mapping) == 5
        assert "Navn" in ner_mapping
        assert "Steder" in ner_mapping
        assert len(ner_mapping["Navn"]) == 1

        # Create POS mapping
        df_noun = pd.DataFrame({"token": ["hus"], "frekv": [10]})
        df_verb = pd.DataFrame({"token": ["løpe"], "frekv": [8]})
        df_adj = pd.DataFrame({"token": ["stor"], "frekv": [6]})
        df_prep = pd.DataFrame({"token": ["i"], "frekv": [15]})
        df_other_pos = pd.DataFrame({"token": ["og"], "frekv": [20]})

        pos_mapping = create_pos_label_mapping(
            df_noun, df_verb, df_adj, df_prep, df_other_pos
        )

        assert len(pos_mapping) == 5
        assert "Substantiv" in pos_mapping
        assert "Verb" in pos_mapping


@pytest.mark.integration
class TestModuleIntegrity:
    """Test that all modules work together correctly."""

    def test_all_modules_import(self):
        """Test that all modules can be imported."""
        import app
        import ui_components
        import document_utils
        import dhlab_functions

        assert app is not None
        assert ui_components is not None
        assert document_utils is not None
        assert dhlab_functions is not None

    def test_ui_components_dependencies(self):
        """Test that ui_components has all required dependencies."""
        import ui_components

        # Check that UI components import what they need
        assert hasattr(ui_components, "st")
        assert hasattr(ui_components, "pd")
        assert hasattr(ui_components, "dh")
        assert hasattr(ui_components, "get_corpus")
        assert hasattr(ui_components, "to_excel")

    def test_document_utils_exports(self):
        """Test that document_utils exports all expected functions."""
        from document_utils import (
            NER_OPTIONS,
            POS_OPTIONS,
            get_page_count,
            extract_urns_from_text,
            generate_choices_from_corpus,
        )

        # All should be callable except constants
        assert isinstance(NER_OPTIONS, list)
        assert isinstance(POS_OPTIONS, list)
        assert callable(get_page_count)
        assert callable(extract_urns_from_text)
        assert callable(generate_choices_from_corpus)

    def test_dhlab_functions_exports(self):
        """Test that dhlab_functions exports all expected functions."""
        from dhlab_functions import (
            get_corpus,
            get_ner,
            get_pos,
            to_excel,
        )

        assert callable(get_corpus)
        assert callable(get_ner)
        assert callable(get_pos)
        assert callable(to_excel)

    def test_ui_components_exports(self):
        """Test that ui_components exports all expected functions."""
        from ui_components import (
            define_corpus_from_ui,
            render_text_selection_ui,
            render_analysis_config_ui,
            display_dataframes_in_columns,
            render_download_button,
        )

        assert callable(define_corpus_from_ui)
        assert callable(render_text_selection_ui)
        assert callable(render_analysis_config_ui)
        assert callable(display_dataframes_in_columns)
        assert callable(render_download_button)


@pytest.mark.integration
class TestDataFlow:
    """Test data flow between modules."""

    def test_corpus_to_choices_flow(self):
        """Test data flow from corpus creation to choice generation."""
        from document_utils import generate_choices_from_corpus

        # Simulate corpus data
        corpus = pd.DataFrame(
            {
                "authors": ["Author1", "Author2"],
                "title": ["Title1", "Title2"],
                "year": [2020, 2021],
                "urn": ["URN:NBN:no-nb_digibok_111", "URN:NBN:no-nb_digibok_222"],
            }
        )

        choices = generate_choices_from_corpus(corpus)

        assert len(choices) == 2
        assert "Author1" in choices[0]
        assert "Title2" in choices[1]

    def test_urn_extraction_to_filename_flow(self):
        """Test flow from URN extraction to filename generation."""
        from document_utils import (
            extract_urns_from_text,
            extract_urn_id,
            generate_default_filename,
        )

        # Extract URN
        text = "Document URN:NBN:no-nb_digibok_2023010101234 is interesting"
        urns = extract_urns_from_text(text)

        # Extract ID
        urn_id = extract_urn_id(urns[0])
        # extract_urn_id splits on '-' and takes the last part
        # URN:NBN:no-nb_digibok_2023010101234 -> nb_digibok_2023010101234
        assert "2023010101234" in urn_id

        # Generate filename
        filename = generate_default_filename(urns[0], 0, 100)
        # Filename should contain the ID and page range
        assert filename.endswith("_0_100.xlsx")
        assert "2023010101234" in filename

    @patch("document_utils.get_ner")
    @patch("dhlab_functions.to_excel")
    def test_analysis_to_export_flow(self, mock_to_excel, mock_get_ner):
        """Test flow from analysis to Excel export."""
        from document_utils import process_ner_analysis

        # Mock NER analysis
        mock_df = pd.DataFrame(
            {"token": ["Oslo"], "ner": ["LOC"], "frekv": [10]}
        ).set_index("token")

        mock_get_ner.return_value = (
            mock_df,
            pd.DataFrame(columns=["ner", "frekv"]),  # personer
            mock_df,  # steder
            pd.DataFrame(columns=["ner", "frekv"]),  # org
            pd.DataFrame(columns=["ner", "frekv"]),  # produkter
            pd.DataFrame(columns=["ner", "frekv"]),  # andre
        )

        mock_to_excel.return_value = b"excel_data"

        # Process analysis
        df, lab_to_frame = process_ner_analysis(
            "URN:NBN:no-nb_digibok_123456", "nb_core_news_lg", (0, 100)
        )

        # Export to Excel
        from dhlab_functions import to_excel

        excel_data = to_excel(df.reset_index())

        assert excel_data == b"excel_data"
        mock_to_excel.assert_called_once()
