"""
Helper functions extracted from app.py for better code organization.

This module contains utility functions for:
- URN extraction and parsing
- Corpus and choices generation
- Label-to-dataframe mapping
- Analysis processing
- UI helper functions
"""

import re
import requests
import pandas as pd
import streamlit as st
import dhlab as dh
from dhlab_functions import get_corpus, get_ner, get_pos, to_excel


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
    if not filename.endswith(".xlsx"):
        return f"{filename}.xlsx"
    return filename


def generate_default_filename(
    urn: str, selected_start_page: int, selected_stop_page: int
) -> str:
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


# ============================================================================
# UI Component Functions
# ============================================================================


def define_corpus_from_ui() -> tuple[bool, pd.DataFrame | None, list[str]]:
    """
    Handle corpus definition from UI (Urnliste, Excelkorpus, or Stikkord).

    Returns:
        Tuple of (corpus_defined, corpus_dataframe, choices_list)
    """
    icol1, icol2 = st.columns([1, 3])

    corpus_defined = False
    corpus = None

    with icol1:
        method = st.selectbox(
            "Velg metode for å finne dokument",
            options=["Stikkord", "URN", "Excelkorpus"],
            help="Du kan skrive inn URN-koden til dokumentet direkte, søke etter dokumenter med stikkord, eller last opp et korpus-excelark fra DH-labens korpusbygger",
        )

    with icol2:
        if method == "URN":
            urner = st.text_area(
                "Lim inn URN:",
                help="Lim tekst med en eller flere URNer",
            )
            if urner != "":
                urns = extract_urns_from_text(urner)
                if urns:
                    corpus_defined = True
                    corpus = dh.Corpus(doctype="digibok", limit=0)
                    corpus.extend_from_identifiers(urns)
                    corpus = corpus.corpus
                else:
                    st.write("Fant ingen URNer")

        elif method == "Excelkorpus":
            uploaded_file = st.file_uploader(
                "Last opp et korpus (excelfil fra DH-labens korpusbygger: https://dh.nb.no/run/corp-conc-coll-webapp/app/)"
            )
            if uploaded_file is not None:
                corpus_defined = True
                dataframe = pd.read_excel(uploaded_file)
                corpus = dh.Corpus(doctype="digibok", limit=0)
                corpus.extend_from_identifiers(list(dataframe.urn))
                corpus = corpus.corpus

        else:  # Stikkord
            stikkord = st.text_input(
                label="Søk i dokumenttitler for å lage et utvalg tekster",
                help="Skriv inn for eksempel forfatter og tittel for bøker, og avisnavn og dato (YYYYMMDD) for aviser.",
            )

            if stikkord == "":
                stikkord = None
            corpus_defined = True
            corpus = get_corpus(freetext=stikkord)

    # Generate choices from corpus
    if corpus_defined and corpus is not None:
        choices = generate_choices_from_corpus(corpus)
    else:
        choices = []

    return corpus_defined, corpus, choices


def render_text_selection_ui(
    choices: list[str],
) -> tuple[str, tuple[int, int], str] | None:
    """
    Render text selection UI with document picker, page range, and filename.

    Args:
        choices: List of formatted document choices

    Returns:
        Tuple of (urn, start_to, filename) or None if no choices
    """
    if not choices:
        return None

    txt_col1, colpages, txt_col2 = st.columns([2, 1, 1])

    with txt_col1:
        valg = st.selectbox("Velg én tekst fra utvalget", choices)
        urn = valg.split(", ")[-1]

    with colpages:
        last = get_page_count(urn)
        if last < 1:
            last = 500

        selected_start_page, selected_stop_page = st.slider(
            "Velg sidetall (om ingenting endres blir hele teksten analysert)",
            min_value=0,
            max_value=last,
            value=(0, last),
            help="Sidetall for det området i teksten analysen skal gjøres.",
        )
        if selected_stop_page < 4:
            selected_start_page = 0
            selected_stop_page = 4

    with txt_col2:
        default_filename = generate_default_filename(
            urn, selected_start_page, selected_stop_page
        )
        filename = st.text_input(
            "Filnavn utfil",
            default_filename,
            help="Det kommer en lagringsknapp under analysetabellen",
        )

    filename = ensure_xlsx_extension(filename)

    return urn, (selected_start_page, selected_stop_page), filename


def render_analysis_config_ui() -> tuple[str, str, list[str]]:
    """
    Render analysis configuration UI (analysis type, model, filters).

    Returns:
        Tuple of (analyse_type, model, types)
    """
    # Initialize session state if needed
    if "NER" not in st.session_state:
        st.session_state["NER"] = NER_OPTIONS
    if "POS" not in st.session_state:
        st.session_state["POS"] = POS_OPTIONS

    colA, colB, colN = st.columns([1, 1, 2])

    with colA:
        analyse_type = st.selectbox(
            "Analysetype — navn (NER) eller ordklasser (POS)", ["NER", "POS"]
        )
        select_options = get_selection_options(analyse_type)

    with colB:
        model = st.selectbox(
            "Velg språkmodell",
            dh.Models().models,
            help="Modellnavnet inneholder språkkode, treningsmateriale og størrelse (nb = norsk bokmål, en=engelsk, lg=large, md=medium, sm=small)",
        )

    with colN:
        types = st.multiselect(
            "Velg analysekategorier",
            options=select_options,
            default=st.session_state[analyse_type],
        )
        if types == []:
            types = [select_options[0]]

        st.session_state[analyse_type] = types

    return analyse_type, model, types


def display_dataframes_in_columns(
    types: list[str], lab_to_frame: dict[str, pd.DataFrame]
) -> None:
    """
    Display dataframes in columns based on selected types.

    Args:
        types: List of selected analysis types to display
        lab_to_frame: Mapping from type labels to dataframes
    """
    if not types:
        return

    cols = st.columns(len(types))

    for col, type_name in zip(cols, types):
        with col:
            st.header(type_name)
            st.dataframe(
                lab_to_frame[type_name].sort_values(by="frekv", ascending=False)
            )


def render_download_button(df: pd.DataFrame, filename: str) -> None:
    """
    Render download button for analysis results.

    Args:
        df: DataFrame to download
        filename: Name for the downloaded file
    """
    st.download_button(
        f"Last ned data i excelformat til '{filename}'",
        to_excel(df.reset_index()),
        filename,
        help="Åpnes i Excel eller tilsvarende - alle kategorier er med i nedlastingen",
    )
