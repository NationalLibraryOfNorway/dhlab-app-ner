import streamlit as st
import dhlab as dh
import re
import requests
import pandas as pd

from io import BytesIO

@st.cache_data()
def get_corpus(freetext=None, title=None, from_year=1900, to_year=2020):
    c = dh.Corpus(freetext=freetext, title=title,from_year=from_year, to_year=to_year)
    return c.corpus

def get_pages(urn):
    try:
        x = f"https://api.nb.no/catalog/v1/metadata/{urn}/mods"
        res = requests.get(x)
        y = re.findall("extent>([0-9]+).*</extent", res.text)[0]
    except:
        y = 0
    return y
                   
@st.cache_data()
def get_ner(urn, model, s, t):
    df = dh.NER(urn = urn, model = model, start_page = s, to_page = t).ner.set_index('token')
    df_defined = True
    personer = df[df["ner"].str.contains("PER")] 
    steder = df[df['ner'].str.contains('LOC')]
    organisasjoner = df[df["ner"].str.contains("ORG")]
    produkter =  df[df["ner"].str.contains("PROD")]

    andre = df[
        (~df["ner"].str.contains("PER")) &
        (~df.ner.str.contains('ORG')) &
        (~df.ner.str.contains('PROD')) &
        (~df['ner'].str.contains('LOC'))]
    return df, personer, steder, organisasjoner, produkter, andre

@st.cache_data()
def get_pos(urn, model, s, t):
    df = dh.POS(urn = urn, model = model, start_page = s, to_page = t).pos.set_index('token')
    df_defined = True
    noun = df[df.pos.str.contains('NOUN')]
    verb = df[df.pos.str.contains('VERB')]
    adj = df[df.pos.str.contains('ADJ')]
    prep = df[df.pos.str.contains('ADP')]
    andre = df[
        (~df.pos.str.contains("NOUN")) &
        (~df.pos.str.contains('VERB')) &
        (~df.pos.str.contains('ADJ')) &
        (~df.pos.str.contains('ADP'))]
    return df, noun, verb, adj, prep, andre

@st.cache_data()
def to_excel(df):
    """Make an excel object out of a dataframe as an IO-object"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data