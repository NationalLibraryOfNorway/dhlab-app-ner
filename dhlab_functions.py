import streamlit as st
import dhlab as dh
import pandas as pd

from io import BytesIO


@st.cache_data()
def get_corpus(
    freetext: str | None = None,
    title: str | None = None,
    from_year: int = 1900,
    to_year: int = 2020,
    urns: list[str] = [],
) -> pd.DataFrame:
    if urns:
        corpus = dh.Corpus(doctype="digibok", limit=0)
        corpus.extend_from_identifiers(urns)
    else:
        corpus = dh.Corpus(
            freetext=freetext, title=title, from_year=from_year, to_year=to_year
        )
    return corpus.corpus


@st.cache_data()
def get_ner(
    urn: str, model: str, start_page: int, to_page: int
) -> tuple[
    pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame
]:
    df = dh.NER(
        urn=urn, model=model, start_page=start_page, to_page=to_page
    ).ner.set_index("token")
    persons = df[df["ner"].str.contains("PER")]
    locations = df[df["ner"].str.contains("LOC")]
    organizations = df[df["ner"].str.contains("ORG")]
    products = df[df["ner"].str.contains("PROD")]

    others = df[
        (~df["ner"].str.contains("PER"))
        & (~df.ner.str.contains("ORG"))
        & (~df.ner.str.contains("PROD"))
        & (~df["ner"].str.contains("LOC"))
    ]
    return df, persons, locations, organizations, products, others


@st.cache_data()
def get_pos(
    urn: str, model: str, start_page: int, to_page: int
) -> tuple[
    pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame
]:
    df = dh.POS(
        urn=urn, model=model, start_page=start_page, to_page=to_page
    ).pos.set_index("token")
    noun = df[df.pos.str.contains("NOUN")]
    verb = df[df.pos.str.contains("VERB")]
    adjective = df[df.pos.str.contains("ADJ")]
    prep = df[df.pos.str.contains("ADP")]
    other = df[
        (~df.pos.str.contains("NOUN"))
        & (~df.pos.str.contains("VERB"))
        & (~df.pos.str.contains("ADJ"))
        & (~df.pos.str.contains("ADP"))
    ]
    return df, noun, verb, adjective, prep, other


@st.cache_data()
def to_excel(df: pd.DataFrame) -> bytes:
    """Make an excel object out of a dataframe as an IO-object"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    processed_data = output.getvalue()
    return processed_data
