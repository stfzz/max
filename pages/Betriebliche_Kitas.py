from os import path

# from unicodedata import name

import numpy as np
import pandas as pd
import xlsxwriter
import streamlit as st
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder

from this import d

from datetime import date

st.set_page_config(
    page_title="Controllo Errori Betriebliche Kitas", layout="wide", page_icon="🤗"  # 👽
)


# riferimento centrale e unico per la gestione dei controlli
ERRORDICT = {
    # gestiamo tutto quello che riguarda i controlli da fare qui
    # in seguito usiamo la key del dict per creare sia le checkbox
    # sia per chiamare le funzioni, sia per creare la colonna bool
    # per la tabella con soli errori
    #
    # in sostanza: vogliamo che ERRORDICT sia il riferimento unico
    # per tutti i controlli che facciamo
    #
    # basta aggiungere qui un nuovo errore e la descrizione
    # e i checkbox etc vengono creati automaticamente
    "errMicrostruttura":"Controllo compilazione microstruttura",
    "errGestore":"Controllo compilazione gestore",
    "errNome": "Controllo compilazione cognome e nome bambino",
    "errDataInizio": "Controllo data inizio",
    "errDataFine": "Controllo data fine",
    "errDataInizioFine": "Controllo data inizio_minore_fine",
    "errOccorrenzeBambino": "Controllo occorrenze bambino",
    "errComuneProvenienza": "Controllo comune provenienza del bambino",
    "errCompilazione666": "Controllo compilazione ore 666",
    "errCompilazione543": "Controllo compilazione ore 543",
    "errOre666": "Controllo ore 666 maggiore di zero",
    "errOre543DataInizio": "Controllo ore 543 su data inizio",
    "errOre543DataFine": "Controllo ore 543 su data fine",
    "errDataInizio2": "Controllo data inizio foglio 1 minore anno riferimento",
    "errOccorrenzeBambinoKitas": "Controllo occorrenze bambino per Kitas",
    

}


def choose_checks2():
    checks = {}
    st.write("")
    a = 1
    # creiamo le checkbox e i valori dinamicamente in base al dictionary che contiene
    # la lista degli errori
    expndr = st.expander("SELEZIONE CONTROLLI DA ESEGUIRE", expanded=True)
    c1, c2, c3, c4 = expndr.columns(4)
    with expndr:
        st.write("")
        attivatutti = expndr.checkbox(
            "Selezionare/deselezionare tutti i controlli", value=True
        )
        for e in ERRORDICT.keys():
            # creiamo i nomi delle variabili in modo dinamico
            locals()[f"{e}"] = locals()[f"c{a}"].checkbox(
                ERRORDICT[e], value=attivatutti, key=e
            )
            if a == 4:
                a = 1
            else:
                a = a + 1
            # scriviamo nel dict il nome del controllo e il valore bool della checkbox
            checks[e] = locals()[f"{e}"]

    return checks

def check_data2(df, checks):
    # definiamo come variabile globale la condizione logica per evitare i record con
    # ore rendicontate 2020 = 0
    #global NO_ZERO
    #NO_ZERO = df["Ore totali rendicontate per il 2020"] > 0
    for e in checks.keys():
        # per ogni errore vediamo se è stato scelto come checkbox
        # se è true, eseguiamo...
        if checks[e]:
            # il nome della funzione da chiamare è contenuta nel dict
            # ed è lo stesso nome dell'errore
            funzione = globals()[e]
            # abbiamo creato il nome della funzione da chiamare e salvato in "funzione"
            # in questo modo vengono chiamate tutte le funzioni che hanno la
            # checkbox == True
            df = funzione(df)
    return df


def app():

    st.header("FAMILIENAGENTUR - AGENZIA PER LA FAMIGLIA")
    st.subheader("Controllo errori BETRIEBLICHE KITAS (v. 0.0.1)")
    dfout = None
    # anno_riferimento = 2020
    uploaded_files = st.file_uploader(
        "SCEGLIERE FILE EXCEL DA CONTROLLARE", accept_multiple_files=True
    )

    anno_riferimento = st.selectbox("ANNO RIFERIMENTO", ("2020", "2021", "2022"))

    checks = choose_checks2()




app()