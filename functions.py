import streamlit as st
import dhlab as dh
import re
import requests
import pandas as pd

from io import BytesIO


@st.cache_data()
def get_corpus(freetext=None, title=None, from_year=1900, to_year=2020):
    c = dh.Corpus(freetext=freetext, title=title, from_year=from_year, to_year=to_year)
    return c.corpus


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


@st.cache_data()
def get_ner(urn, model, s, t):
    df = dh.NER(urn=urn, model=model, start_page=s, to_page=t).ner.set_index("token")
    personer = df[df["ner"].str.contains("PER")]
    steder = df[df["ner"].str.contains("LOC")]
    organisasjoner = df[df["ner"].str.contains("ORG")]
    produkter = df[df["ner"].str.contains("PROD")]

    andre = df[
        (~df["ner"].str.contains("PER"))
        & (~df.ner.str.contains("ORG"))
        & (~df.ner.str.contains("PROD"))
        & (~df["ner"].str.contains("LOC"))
    ]
    return df, personer, steder, organisasjoner, produkter, andre


@st.cache_data()
def get_pos(urn, model, s, t):
    df = dh.POS(urn=urn, model=model, start_page=s, to_page=t).pos.set_index("token")
    noun = df[df.pos.str.contains("NOUN")]
    verb = df[df.pos.str.contains("VERB")]
    adj = df[df.pos.str.contains("ADJ")]
    prep = df[df.pos.str.contains("ADP")]
    andre = df[
        (~df.pos.str.contains("NOUN"))
        & (~df.pos.str.contains("VERB"))
        & (~df.pos.str.contains("ADJ"))
        & (~df.pos.str.contains("ADP"))
    ]
    return df, noun, verb, adj, prep, andre


@st.cache_data()
def to_excel(df):
    """Make an excel object out of a dataframe as an IO-object"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    processed_data = output.getvalue()
    return processed_data
