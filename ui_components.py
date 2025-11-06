"""
Streamlit UI component functions for the NER/POS analysis application.

This module contains functions for:
- Corpus definition UI
- Text selection UI
- Analysis configuration UI
- Results display
- Download functionality
"""

import streamlit as st
import pandas as pd
import dhlab as dh
from dhlab_functions import get_corpus, to_excel
from document_utils import (
    extract_urns_from_text,
    generate_choices_from_corpus,
    get_page_count,
    generate_default_filename,
    ensure_xlsx_extension,
    get_selection_options,
    NER_OPTIONS,
    POS_OPTIONS,
)


def define_corpus_from_ui() -> tuple[pd.DataFrame | None, list[str]]:
    """
    Handle corpus definition from UI (Urnliste, Excelkorpus, or Stikkord).

    Returns:
        Tuple of (corpus_dataframe, choices_list)
    """
    icol1, icol2 = st.columns([1, 3])

    corpus = None

    with icol1:
        method = st.selectbox(
            "Velg metode for å finne dokument",
            options=["Stikkord", "URN", "Excelkorpus"],
            help="Du kan skrive inn URN-koden til dokumentet direkte, søke etter dokumenter med stikkord, eller last opp et korpus-excelark fra DH-labens korpusbygger",
        )

    with icol2:
        match method:
            case "URN":
                text_with_urns = st.text_area(
                    "Lim inn URN:",
                    help="Lim tekst med en eller flere URNer",
                )
                if text_with_urns != "":
                    urns = extract_urns_from_text(text_with_urns)
                    if urns:
                        corpus = get_corpus(urns=urns)
                    else:
                        st.write("Fant ingen URNer")

            case "Excelkorpus":
                uploaded_file = st.file_uploader(
                    "Last opp et korpus (excelfil fra DH-labens korpusbygger: https://dh.nb.no/run/corp-conc-coll-webapp/app/)"
                )
                if uploaded_file is not None:
                    dataframe = pd.read_excel(uploaded_file)
                    urns = list(dataframe.urn)
                    if urns:
                        corpus = get_corpus(urns=urns)

            case "Stikkord":
                stikkord = st.text_input(
                    label="Søk i dokumenttitler for å lage et utvalg tekster",
                    help="Skriv inn for eksempel forfatter og tittel for bøker, og avisnavn og dato (YYYYMMDD) for aviser.",
                )

                stikkord = stikkord if stikkord != "" else None
                corpus = get_corpus(freetext=stikkord)

    # Generate choices from corpus
    if corpus is not None:
        choices = generate_choices_from_corpus(corpus)
    else:
        choices = []

    return corpus, choices


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
