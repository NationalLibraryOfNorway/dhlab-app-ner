import streamlit as st
from PIL import Image

from app_helpers import (
    define_corpus_from_ui,
    render_text_selection_ui,
    render_analysis_config_ui,
    display_dataframes_in_columns,
    render_download_button,
    process_ner_analysis,
    process_pos_analysis,
)


def header():
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
corpus_defined, corpus, choices = define_corpus_from_ui()

# Step 2: Configure text selection and analysis (if corpus is defined)
df_defined = False

if choices:
    # Render text selection UI
    result = render_text_selection_ui(choices)
    if result:
        urn, start_to, filename = result
    else:
        st.stop()

    # Render analysis configuration UI
    analyse_type, model, types = render_analysis_config_ui()

    # Step 3: Run analysis
    with st.form(key="my_form"):
        submit_button = st.form_submit_button(
            label="Analyser dokumentet (det kan ta inntil et halvt minutt å analysere teksten)",
        )

        if submit_button:
            # Process analysis based on type
            if analyse_type == "NER":
                df, lab_to_frame = process_ner_analysis(urn, model, start_to)
            else:  # POS
                df, lab_to_frame = process_pos_analysis(urn, model, start_to)

            df_defined = True

            # Display results in columns
            display_dataframes_in_columns(types, lab_to_frame)

    # Step 4: Download button
    if df_defined:
        render_download_button(df, filename)
else:
    st.write("Her dukker det opp en tekstvelger så snart listen av tekster er definert")
