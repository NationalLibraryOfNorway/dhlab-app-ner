import streamlit as st
from PIL import Image

from ui_components import (
    define_corpus_from_ui,
    render_text_selection_ui,
    render_analysis_config_ui,
    display_dataframes_in_columns,
    render_download_button,
)
from document_utils import (
    process_ner_analysis,
    process_pos_analysis,
)


def header() -> None:
    head_col1, head_col2 = st.columns(2)

    with head_col1:
        st.title("Navn og steder")
        st.markdown(
            "Her kan du bruke språkmodellene i [SpaCy](https://spacy.io/models/nb) for å analysere spesifikke dokumenter i NBs digitale samling."
        )
        st.markdown(
            "Du kan velge NER (named entity recognition) for å hente ut navn fra teksten, eller POS (part of speech) for å hente ut ordklasser."
        )
    with head_col2:
        image = Image.open("DHlab_logo_web_en_black.png")
        st.image(image)

        st.markdown("Les mer om [DH-laben på NB](https://nb.no/dh-lab)")


st.set_page_config(layout="wide")
header()
st.markdown("----")

# Step 1: Define corpus
corpus, choices = define_corpus_from_ui()
corpus_defined = corpus is not None

# Step 2: Configure text selection and analysis (if corpus is defined)
df_defined = False

if choices:
    # Render text selection UI
    result = render_text_selection_ui(choices)
    if result:
        urn, selected_start_page, selected_stop_page, filename = result
    else:
        st.stop()

    # Render analysis configuration UI
    analyse_type, model, types = render_analysis_config_ui()

    # Step 3: Run analysis
    if st.button(
        "Analyser dokumentet (det kan ta inntil et halvt minutt å analysere teksten)",
        type="primary",
    ):
        # Process analysis based on type
        if analyse_type == "NER":
            df, lab_to_frame = process_ner_analysis(
                urn, model, selected_start_page, selected_stop_page
            )
        else:  # POS
            df, lab_to_frame = process_pos_analysis(
                urn, model, selected_start_page, selected_stop_page
            )

        df_defined = True

        # Display results in columns
        display_dataframes_in_columns(types, lab_to_frame)

        # Step 4: Download button (shown immediately after analysis)
        render_download_button(df, filename)
else:
    st.write("Her dukker det opp en tekstvelger så snart listen av tekster er definert")
