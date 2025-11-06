"""
Utility functions for document processing and analysis.

This module contains functions for:
- URN extraction and parsing
- Corpus and choices generation
- Page count and validation
- Analysis processing (NER and POS)
- Label-to-dataframe mapping
- File handling utilities
"""

import re
import requests
import pandas as pd
from dhlab_functions import get_ner, get_pos


# Constants
NER_OPTIONS = ["Navn", "Steder", "Organisasjoner", "Produkter", "Andre"]
POS_OPTIONS = ["Substantiv", "Verb", "Adjektiv", "Preposisjon", "Andre"]


def get_page_count(urn: str) -> int:
    """
    Get the number of pages in a document from the NB API.

    Args:
        urn: Document URN

    Returns:
        Number of pages, or -1 if not found
    """
    try:
        url = f"https://api.nb.no/catalog/v1/metadata/{urn}/mods"
        response = requests.get(url)
        page_count_match = re.findall("extent>([0-9]+).*</extent", response.text)[0]
        return int(page_count_match)
    except Exception:
        return -1


def extract_urns_from_text(text: str) -> list[str]:
    """
    Extract URNs from a text string.

    Args:
        text: String that may contain URNs

    Returns:
        List of URN strings found in the text
    """
    if not text:
        return []

    urns = re.findall(r"URN:NBN[^\s.,]+", text)
    return urns


def generate_choices_from_corpus(corpus: pd.DataFrame) -> list[str]:
    """
    Generate choice strings from corpus DataFrame.

    Args:
        corpus: DataFrame with columns ['authors', 'title', 'year', 'urn']

    Returns:
        List of formatted choice strings
    """
    if corpus.empty:
        return []

    choices = [
        ", ".join([str(value) for value in row])
        for row in corpus[["authors", "title", "year", "urn"]].values.tolist()
    ]
    return choices


def extract_urn_id(urn: str) -> str:
    """
    Extract the ID portion from a URN.

    Args:
        urn: Full URN string (e.g., "URN:NBN:no-nb_digibok_123456")

    Returns:
        The ID portion (e.g., "123456")
    """
    return urn.split("-")[-1]


def ensure_xlsx_extension(filename: str) -> str:
    """
    Ensure filename has .xlsx extension.

    Args:
        filename: Original filename

    Returns:
        Filename with .xlsx extension
    """
    if not filename.endswith(".xlsx"):
        return f"{filename}.xlsx"
    return filename


def generate_default_filename(
    urn: str, selected_start_page: int, selected_stop_page: int
) -> str:
    """
    Generate a filename from URN and page range.

    Args:
        urn: Document URN
        selected_start_page: first page of document for analysis
        selected_stop_page: last page of document for analysis

    Returns:
        Default filename with .xlsx extension
    """
    urn_id = extract_urn_id(urn)
    return f"{urn_id}_{selected_start_page}_{selected_stop_page}.xlsx"


def validate_page_range(start_to: tuple[int, int], max_pages: int) -> tuple[int, int]:
    """
    Validate and adjust page range.

    Args:
        start_to: Tuple of (start_page, end_page)
        max_pages: Maximum number of pages in document

    Returns:
        Validated (start_page, end_page) tuple
    """
    start, end = start_to

    # If max_pages is invalid, use default
    if max_pages < 1:
        max_pages = 500

    # Ensure minimum range
    if end < 4:
        end = 4

    # Cap at max_pages
    if end > max_pages:
        end = max_pages

    return (start, end)


def create_ner_label_mapping(
    personer: pd.DataFrame,
    steder: pd.DataFrame,
    organisasjoner: pd.DataFrame,
    produkter: pd.DataFrame,
    andre: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """
    Create mapping from Norwegian labels to NER dataframes.

    Args:
        personer: DataFrame of person entities
        steder: DataFrame of location entities
        organisasjoner: DataFrame of organization entities
        produkter: DataFrame of product entities
        andre: DataFrame of other entities

    Returns:
        Dictionary mapping labels to dataframes
    """
    return {
        "Navn": personer,
        "Steder": steder,
        "Organisasjoner": organisasjoner,
        "Produkter": produkter,
        "Andre": andre,
    }


def create_pos_label_mapping(
    noun: pd.DataFrame,
    verb: pd.DataFrame,
    adjektiv: pd.DataFrame,
    prep: pd.DataFrame,
    andre: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    """
    Create mapping from Norwegian labels to POS dataframes.

    Args:
        noun: DataFrame of nouns
        verb: DataFrame of verbs
        adjektiv: DataFrame of adjectives
        prep: DataFrame of prepositions
        andre: DataFrame of other parts of speech

    Returns:
        Dictionary mapping labels to dataframes
    """
    return {
        "Substantiv": noun,
        "Verb": verb,
        "Adjektiv": adjektiv,
        "Preposisjon": prep,
        "Andre": andre,
    }


def process_ner_analysis(
    urn: str, model: str, start_to: tuple[int, int]
) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    """
    Process NER analysis for a document.

    Args:
        urn: Document URN
        model: SpaCy model name
        start_to: Tuple of (start_page, end_page)

    Returns:
        Tuple of (full_dataframe, label_to_frame_mapping)
    """
    df, personer, steder, organisasjoner, produkter, andre = get_ner(
        urn, model, start_to[0], start_to[1]
    )

    lab_to_frame = create_ner_label_mapping(
        personer, steder, organisasjoner, produkter, andre
    )

    return df, lab_to_frame


def process_pos_analysis(
    urn: str, model: str, start_to: tuple[int, int]
) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    """
    Process POS analysis for a document.

    Args:
        urn: Document URN
        model: SpaCy model name
        start_to: Tuple of (start_page, end_page)

    Returns:
        Tuple of (full_dataframe, label_to_frame_mapping)
    """
    df, noun, verb, adjektiv, prep, andre = get_pos(
        urn, model, start_to[0], start_to[1]
    )

    lab_to_frame = create_pos_label_mapping(noun, verb, adjektiv, prep, andre)

    return df, lab_to_frame


def get_selection_options(analyse_type: str) -> list[str]:
    """
    Get selection options based on analysis type.

    Args:
        analyse_type: Either "NER" or "POS"

    Returns:
        List of selection options
    """
    if analyse_type == "NER":
        return NER_OPTIONS
    elif analyse_type == "POS":
        return POS_OPTIONS
    else:
        # Default to NER options
        return NER_OPTIONS
