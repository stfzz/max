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


def get_data(uploaded_files, anno_riferimento):
    dfout1 = None
    dfout2 = None
    st.info("Sono stati caricati " + str(len(uploaded_files)) + " files")
    status = st.empty()
    for uploaded_file in uploaded_files:
        try:
            status.info("[*] " + uploaded_file.name + " caricato")
            df1 = pd.read_excel(uploaded_file,0)   #, usecols="A:M")
            df2 = pd.read_excel(uploaded_file,1)
        except:
            st.error(uploaded_file.name + " non è un file Excel")
            continue
        

        # lasciamo prepare_data qui?
        try:
            status.info(f"[*] {uploaded_file.name} elaborato")
            df1 = prepare_data(df1,0)
            df2 = prepare_data(df2,1)
        except:
            st.error(
                f"{uploaded_file.name} --> ERRORE CONTROLLO GENERALE --> Il file non viene usato per l'elaborazione"
            )
            continue

        st.write(df1)
        st.write(df2)

        # se dfout1 non esiste lo creiamo
        if dfout1 is None:
            dfout1 = pd.DataFrame(columns=df1.columns)
            dfout1 = df1
        else:
            # inserire qui il controllo del nome ente, che deve essere lo stesso per i file caricati?
            dfout1 = pd.concat([dfout1, df1])

        # se dfout2 non esiste lo creiamo
        if dfout2 is None:
            dfout2 = pd.DataFrame(columns=df2.columns)
            dfout2 = df2
        else:
            # inserire qui il controllo del nome ente, che deve essere lo stesso per i file caricati?
            dfout2 = pd.concat([dfout2, df2])

    # ora sono tutti concatenati e possiamo restituire il dataframe
    if dfout1 is not None and dfout2 is not None:
        status.success(
            "[*] Tutti i dati sono stati elaborati -  PER INIZIARE DA CAPO: RICARICARE LA PAGINA"
        )

    return dfout1, dfout2

def prepare_data(df, foglio):
    st.write(foglio)
    if foglio == 0:
        df = df.drop(['Unnamed: 6', 'Unnamed: 7'], axis=1)
        df.columns = ["Cognome", "Nome", "utente", "ComuneProvenienza", "DataInizio","DataFine"]
    elif foglio == 1:
        df.columns = ["Cognome", "Nome", "utente", "ComuneProvenienza", "DataInizio","DataFine","delibera666", "delibera543","delibera733","Entrate"]
        #st.dataframe(df)
        # selezioniamo solo le righe che hanno un valore numerico in *Numero progressivo*
        # in questo modo eliminiamo le righe inutili dopo l'ultimo *numero progressivo*
        #validi = df["Cognome"].notna()

        # teniamo solo record validi
        #df = df[validi]


    microstruttura = df.iloc[1]
    microstruttura = microstruttura[1]
    ente = df.iloc[2]
    ente = ente[1]
    df.insert(0, "Microstruttura", microstruttura)
    df.insert(0, "Ente", ente)
    df = df.drop(labels=range(0, 8), axis=0)



    return df







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

    f = st.form("Auswahl", clear_on_submit=True)
    flag = 0

    with f:
        # soluzione un po' assurda, ma vogliamo spostare gli expander fuori dalla form
        # altrimenti non possiamo usare il button per download
        submit = f.form_submit_button("Iniziare elaborazione e controllo errori")
        if submit:
            if len(uploaded_files) == 0:
                st.error("Nessun file caricato!")
            else:
                flag = 1

    # se button pigiato, allora esegui...
    if flag == 1:
        dfout1, dfout2 = get_data(uploaded_files, anno_riferimento)


app()