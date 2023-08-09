
import streamlit as st
import pandas as pd
from PIL import Image
import re
import dhlab as dh


from functions import get_corpus, get_pages, get_ner, get_pos, to_excel

import re

def header():
    head_col1,_,_,head_col2, head_col3 = st.columns(5)

    with head_col1:
        st.title('Navn og steder')
    with head_col2:
        st.markdown('Les mer om [Digital Humaniora - DH](https://nb.no/dh-lab)')
        st.markdown('og språkmodellene i [spaCy](https://spacy.io/models/nb). ')
    with head_col3:
        image = Image.open("DHlab_logo_web_en_black.png")
        st.image(image)



st.set_page_config(layout="wide")
header()
st.markdown("----")

# Three possible corpora
corpus_defined = False

#st.markdown("####  Definer en gruppe tekster fra URNer, korpus eller stikkord")

icol1, icol2 = st.columns([1,3])
with icol1:
    method = st.selectbox(
        "Metode for dokumentspec - Stikkord, Urnliste eller Excel", 
        options=['Stikkord', 'Urnliste', 'Excelkorpus'], 
        help="Lim inn en tekst med URNer, eller last opp et excelark med korpus"
        " lagd for eksempel med https://beta.nb.no/dhlab/korpus/, "
        "eller antyd en grupper tekster ved hjelp av stikkord"
    )

with icol2:
    if method == 'Urnliste':
        urner = st.text_area(
            "Lim inn URNer:","", 
            help="Lim tekst med URNer. Teksten trenger ikke å være formatert, "
            "og kan inneholde mer enn URNer"
        )
        if urner != "":
            urns = re.findall("URN:NBN[^\s.,]+", urner)
            if urns != []:
                corpus_defined = True
                corpus = dh.Corpus(doctype='digibok',limit=0)
                corpus.extend_from_identifiers(urns)
                corpus = corpus.corpus
                #st.write(corpus)
            else:
                st.write('Fant ingen URNer')
                
    elif method == 'Excelkorpus':
        uploaded_file = st.file_uploader(
            "Last opp et korpus", 
            help="Dra en fil over hit, fra et nedlastningsikon, "
            "eller velg fra en mappe"
        )
        if uploaded_file is not None:
            corpus_defined = True
            dataframe = pd.read_excel(uploaded_file)
            corpus = dh.Corpus(doctype='digibok',limit=0)
            corpus.extend_from_identifiers(list(dataframe.urn))
            corpus = corpus.corpus
        
    else:
        stikkord = st.text_input(
            'Angi noen stikkord for å forme et utvalg tekster','', 
            help="Skriv inn for eksempel forfatter og tittel for bøker, "
            "eller avisnavn for aviser." 
            "For aviser kan dato skrives på formatet YYYYMMDD."
        )

        if stikkord == '':
            stikkord = None
        corpus_defined = True
        corpus = get_corpus(freetext=stikkord)

if corpus_defined:
    choices = [', '.join([str(z) for z in x]) 
               for x in corpus[['authors','title', 'year','urn']].values.tolist()]
else:
    choices = []

if 'NER' not in st.session_state:
    st.session_state['NER'] = ['Navn', 'Steder', 'Organisasjoner','Produkter', 'Andre']
    
if 'POS' not in st.session_state:
    st.session_state['POS'] = ['Substantiv', 'Verb', 'Adjektiv','Preposisjon', 'Andre']

    
 # st.markdown("#### Velg tekst for analyse, og sett navn på resultatfil")
    
df_defined = False

if choices != []:
    txt_col1, colpages, txt_col2 = st.columns([2,1,1])

    with txt_col1:
        valg = st.selectbox("Plukk et tekst/dokument", choices)
        urn = valg.split(', ')[-1]
        fname = urn.split('-')[-1]
    with colpages:
        try:
            last = int(get_pages(urn))
        except:
            last = 600
        if last < 1:
            last = 500
        start_to = st.slider(
            "Tekstområde", 
            min_value=0, 
            max_value=last, 
            value=(0, last),
            help="Sidetall for det området i teksten analysen skal gjøres."
            "Om ikke noe settes blir hele teksten analysert"
        )
        if start_to[1] < 4:
            start_to = (0,4)
        #st.write(start_to)
        
    with txt_col2:
        filename = st.text_input(
            'Foreslått filnavn', 
            f"{fname}_{start_to[0]}_{start_to[1]}.xlsx", 
            help="Det er en lagringsknapp under analysetabellen"
        )
        
    if not filename.endswith('.xlsx'):
        filename = f"{filename}.xlsx"
    
    #st.markdown("#### Angi språkmodell og type analyse — NER for navn og steder, POS for ordkategorier")




    colA, colB, colN = st.columns([1,1,2])

    with colA:
        analyse_type = st.selectbox("Analysetype — navn (NER) eller kategorier (POS)", ['NER', 'POS'])
        if analyse_type == 'NER':
            select_options = ['Navn', 'Steder', 'Organisasjoner','Produkter', 'Andre']
        else:
            select_options = ['Substantiv', 'Verb', 'Adjektiv','Preposisjon', 'Andre']

    with colB:
        model = st.selectbox(
            "Språkmodell", 
            dh.Models().models, 
            help= "Forskjellige modeller gir"
            "forskjellig resultat — da for dansk og nb for norsk bokmål")

    with colN:
        types = st.multiselect(
            "Vis analyse for", 
            options = select_options, 
            default = st.session_state[analyse_type]
        )
        if types == []:
            types = select_options[0]
        
        st.session_state[analyse_type] = types 
       
    with st.form(key='my_form'):
        submit_button = st.form_submit_button(label=f'Analyser URN', help = "det kan ta inntil"
        " et halvt minutt å analysere teksten")
        
        if submit_button and analyse_type == 'NER':
             
            df, personer, steder, organisasjoner, produkter, andre = get_ner(urn, model, start_to[0], start_to[1])
            df_defined = True
            
            lab_to_frame = dict(Navn=personer, Steder=steder, Organisasjoner=organisasjoner, Produkter=produkter, Andre=andre)
            
            size = len(types)
            
            if len(types) == 1:
                 col1 = st.columns(1)
            if len(types) == 2:
                 (col1, col2) = st.columns(2)
            elif len(types) == 3:
                (col1,col2, col3) = st.columns(3)
            elif len(types) == 4:
                (col1, col2, col3, col4) = st.columns(4)
            else:
                (col1, col2, col3, col4, col5) = st.columns(5)
            
             
            with col1:

                st.header(types[0])
                st.dataframe(lab_to_frame[types[0]].sort_values(by='frekv', ascending = False))
                
            if size > 1:
                with col2:
                    st.header(types[1])
                    st.dataframe(lab_to_frame[types[1]].sort_values(by='frekv', ascending = False))    
            if size > 2:
                with col3:
                    st.header(types[2])
                    st.dataframe(lab_to_frame[types[2]].sort_values(by='frekv', ascending = False))
            if size > 3:
                with col4:
                    st.header(types[3])
                    st.dataframe(lab_to_frame[types[3]].sort_values(by='frekv', ascending = False))
            if size > 4:
                with col5:

                    st.header(types[4])
                    st.dataframe(lab_to_frame[types[4]].sort_values(by='frekv', ascending = False))
                    
        elif submit_button and analyse_type == 'POS':
            
                    
            df, noun, verb, adjektiv, prep, andre = get_pos(urn, model, start_to[0], start_to[1])
            df_defined = True

            lab_to_frame = dict(Substantiv=noun, Verb=verb, Adjektiv=adjektiv, Preposisjon=prep, Andre=andre)
            
            size = len(types)
            
            if len(types) == 1:
                 col1 = st.columns(1)
            if len(types) == 2:
                 (col1, col2) = st.columns(2)
            elif len(types) == 3:
                (col1,col2, col3) = st.columns(3)
            elif len(types) == 4:
                (col1, col2, col3, col4) = st.columns(4)
            else:
                (col1, col2, col3, col4, col5) = st.columns(5)
            
             
            with col1:

                st.header(types[0])
                st.dataframe(lab_to_frame[types[0]].sort_values(by='frekv', ascending = False))
                
            if size > 1:
                with col2:
                    st.header(types[1])
                    st.dataframe(lab_to_frame[types[1]].sort_values(by='frekv', ascending = False))    
            if size > 2:
                with col3:
                    st.header(types[2])
                    st.dataframe(lab_to_frame[types[2]].sort_values(by='frekv', ascending = False))
            if size > 3:
                with col4:
                    st.header(types[3])
                    st.dataframe(lab_to_frame[types[3]].sort_values(by='frekv', ascending = False))
            if size > 4:
                with col5:

                    st.header(types[4])
                    st.dataframe(lab_to_frame[types[4]].sort_values(by='frekv', ascending = False))
    if df_defined:
        if st.download_button(
            f"Last ned data i excelformat til '{filename}'", 
            to_excel(df.reset_index()),filename, 
            help = "Åpnes i Excel eller tilsvarende - alle kategorier er med i nedlastingen"):
            
            True
else:
    st.write("Her dukker det opp en tekstvelger så snart listen av tekster er definert")