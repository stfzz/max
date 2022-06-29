from ast import Global
from calendar import c
from cmath import exp
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
    #
    # distinguiamo tra errori nei file (errData*) ed errori logici (err*)
    #
    # "dataErrMicrostruttura": "Controllo compilazione microstruttura",
    # "dataErrGestore": "Controllo compilazione gestore",
    "errNome": "Controllo compilazione cognome e nome bambino",
    # "dataErrData": "Controllo formato data inizio e fine assistenza",
    "errTipoKitas": "Controllo tipologia Kitas",
    "errDataInizioFine": "Controllo data inizio_minore_fine",
    "errInizioAnnoRiferimento": "Controllo data inizio per anno riferimento",
    "errFineAnnoRiferimento": "Controllo data fine per anno riferimento",
    "errOccorrenzeBambino": "Controllo occorrenze bambino in diverse strutture per stessa data inizio",
    "errComuneProvenienza": "Controllo comune provenienza per utente comunale",
    "errCompilazione666": "Controllo compilazione ore 666 per utente comunale",
    "errCompilazione543": "Controllo compilazione ore 543 per utente comunale",
    "errCompilazioneEntrate": "Controllo compilazione entrate per utente comunale",
    "errOre666": "Controllo ore 666 maggiore di zero",
    "errOre543DataInizio": "Controllo ore 543 su data inizio",
    "errOre543DataFine": "Controllo ore 543 su data fine",
    "errDataInizioAnnoRiferimento": "Controllo data inizio foglio 0 minore anno riferimento",
    # "errOccorrenzeBambinoKitas": "Controllo occorrenze bambino per Kitas",
}

COSTANTI = {}
costanti_2020 = {
    "datainiziomin": "01.01.2017",
    "datainiziomax": "31.12.2020",
    "datafine": "31.12.2023",
    "datainizio543": "23.11.2020",
    "datafine543": "24.02.2020",
}
COSTANTI = {"2020": costanti_2020}


def app():
    st.header("FAMILIENAGENTUR - AGENZIA PER LA FAMIGLIA")
    st.subheader("Controllo errori BETRIEBLICHE KITAS (v. 0.0.1)")
    dfout = None
    # anno_riferimento = 2020
    uploaded_files = st.file_uploader(
        "SCEGLIERE FILE EXCEL DA CONTROLLARE", accept_multiple_files=True
    )
    global ANNO_RIFERIMENTO
    ANNO_RIFERIMENTO = st.selectbox("ANNO RIFERIMENTO", ("2020", "2021", "2022"))

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
        dfout = get_data(uploaded_files)
        # dfout1, dfout2 = get_data(uploaded_files)
        # if not dfout['sheet0'].empty and not dfout['sheet1'].empty:
        dffinal = check_data2(dfout, checks)
        expndr = st.expander("TABELLA RIASSUNTIVA ELENCO UTENTI PRECEDENTI (SHEET 0)")
        with expndr:
            st.info("Tabella riassuntiva elenco utenti precedenti")
            make_grid(dffinal["sheet0"].sort_values(by=["DataInizio"]))

        expndr = st.expander("TABELLA RIASSUNTIVA ELENCO UTENTI (SHEET 1)")
        with expndr:
            st.info("Tabella riassuntiva elenco utenti")
            make_grid(dffinal["sheet1"].sort_values(by=["DataInizio"]))


#################################
## INIZIO CHECKS
#################################


def errTipoKitas(df):
    for a in (0, 1):
        sheet = "sheet" + str(a)
        condizione1 = df[sheet]["utente"] != "comunale"
        condizione2 = df[sheet]["utente"] != "aziendale"
        condizione = condizione1 & condizione2
        if not df[sheet][condizione].empty:
            expndr = st.expander(
                f"Trovati errori nella descrizione tipo Kitas nel sheet {a}"
            )
            with expndr:
                st.info("Errori riscontrati nella descrizione della tipologia Kitas")
                make_grid(df[sheet][condizione].sort_values(by=["Cognome"]))

                # settiamo flag bool
                df[sheet].loc[condizione, "errTipoKitas"] = True
                # x = dwnld(
                #    df[condizione].sort_values(by=["Cognome"]),
                #    "Scaricare tabella con errori tipologia Kitas",
                #    "errTipoKitas",
                # )
    return df


def errDataInizioFine(df):
    for a in (0, 1):
        sheet = "sheet" + str(a)
        condizione = df[sheet]["DataInizio"] > df[sheet]["DataFine"]
        if not df[sheet][condizione].empty:
            expndr = st.expander(
                f"Trovati errori data inizio maggiore di data fine nel sheet {a}"
            )
            with expndr:
                st.info("Errori riscontrati; data inizio_maggiore data_fine")
                make_grid(df[sheet][condizione].sort_values(by=["Cognome"]))
                # settiamo flag bool
                df[sheet].loc[condizione, "errDataInizioFine"] = True
                # x = dwnld(
                #    df[condizione].sort_values(by=["Cognome"]),
                #    "Scaricare tabella con errori data inizio maggiore di data fine",
                #    "errDataInizioFine",
                # )
    return df


def errNome(df):
    for a in (0, 1):
        sheet = "sheet" + str(a)
        condizione1 = pd.isnull(df[sheet]["Nome"])
        condizione2 = pd.isnull(df[sheet]["Cognome"])
        condizione = condizione1 | condizione2
        if not df[sheet][condizione].empty:
            expndr = st.expander(
                f"Trovati valori nulli per cognome o nome o entrambi nel sheet {a}"
            )
            with expndr:
                st.info("Tabella con cognome o nome o entrambi assenti")
                make_grid(df[sheet][condizione].sort_values(by=["Cognome"]))
                # settiamo flag bool
                df[sheet].loc[condizione, "errNome"] = True
                # x = dwnld(
                #    df[condizione].sort_values(by=["Cognome"]),
                #    "Scaricare tabella con errori data inizio maggiore di data fine",
                #    "errNome",
                #
    return df


def errInizioAnnoRiferimento(df):
    for a in (0, 1):
        sheet = "sheet" + str(a)
        condizione1 = df[sheet]["DataInizio"] > pd.to_datetime(
            COSTANTI[ANNO_RIFERIMENTO]["datainiziomin"], format="%d.%m.%Y"
        )
        condizione2 = df[sheet]["DataInizio"] < pd.to_datetime(
            COSTANTI[ANNO_RIFERIMENTO]["datainiziomax"], format="%d.%m.%Y"
        )
        condizione = condizione1 & condizione2
        # invertiamo la condizione
        if not df[sheet][~condizione].empty:
            expndr = st.expander(
                f"Trovati errori per data inizio in riferimento ad anno di riferimento {ANNO_RIFERIMENTO}"
            )
            with expndr:
                st.info(
                    "Tabella con errori riscontrati per data inizio in riferimento ad anno di riferimento"
                )
                make_grid(df[sheet][~condizione].sort_values(by=["Cognome"]))
                # settiamo flag bool
                df[sheet].loc[~condizione, "errInizioAnnoRiferimento"] = True
                # x = dwnld(
                #    df[sheet][~condizione].sort_values(by=["Cognome"]),
                #    "Scaricare tabella con errori data inizio maggiore di data fine",
                #    "errInizioAnnoRiferimento",
                #
    return df


def errFineAnnoRiferimento(df):
    for a in (0, 1):
        sheet = "sheet" + str(a)
        condizione = df[sheet]["DataFine"] < pd.to_datetime(
            COSTANTI[ANNO_RIFERIMENTO]["datafine"], format="%d.%m.%Y"
        )
        # invertiamo la condizione
        if not df[sheet][~condizione].empty:
            expndr = st.expander(
                f"Trovati errori per data fine in riferimento ad anno di riferimento {ANNO_RIFERIMENTO}"
            )
            with expndr:
                st.info(
                    "Tabella con errori riscontrati per data fine in riferimento ad anno di riferimento"
                )
                make_grid(df[sheet][~condizione].sort_values(by=["Cognome"]))
                # settiamo flag bool
                df[sheet].loc[~condizione, "errFineAnnoRiferimento"] = True
                # x = dwnld(
                #    df[sheet][~condizione].sort_values(by=["Cognome"]),
                #    "Scaricare tabella con errori data inizio maggiore di data fine",
                #    "errInizioAnnoRiferimento",

    return df


def errOre666(df):
    sheet = "sheet1"
    condizione = df[sheet]["delibera666"] > 0
    if not df[sheet][~condizione].empty:
        expndr = st.expander(f"Trovati errori per valori in Delibera 666")
        with expndr:
            st.info("Tabella con errori riscontrati per delibera 666")
            make_grid(df[sheet][~condizione].sort_values(by=["Cognome"]))
            # settiamo flag bool
            df[sheet].loc[~condizione, "errOre666"] = True
            # x = dwnld(
            #    df[sheet][~condizione].sort_values(by=["Cognome"]),
            #    "Scaricare tabella con errori data inizio maggiore di data fine",
            #    "errOre666",

    return df


def errOre543DataInizio(df):
    sheet = "sheet1"
    condizione1 = df[sheet]["DataInizio"] > pd.to_datetime(
        COSTANTI[ANNO_RIFERIMENTO]["datainizio543"], format="%d.%m.%Y"
    )
    condizione2 = df[sheet]["delibera543"] > 0
    condizione = condizione1 & condizione2
    if not df[sheet][condizione].empty:
        expndr = st.expander("Trovati errori inserimento post Notbetreuung")
        with expndr:
            st.info("Tabella con errori inserimento post Notbetreuung")
            make_grid(df[sheet][condizione].sort_values(by=["Cognome"]))
            # settiamo flag bool
            df[sheet].loc[condizione, "errOre543DataInizio"] = True
            # x = dwnld(
            #    df[sheet][condizione].sort_values(by=["Cognome"]),
            #    "Scaricare tabella con errori data inizio maggiore di data fine",
            #    "errOre543DataInizio",

    return df


def errOre543DataFine(df):
    sheet = "sheet1"
    condizione1 = df[sheet]["DataFine"] < pd.to_datetime(
        COSTANTI[ANNO_RIFERIMENTO]["datafine543"], format="%d.%m.%Y"
    )
    condizione2 = df[sheet]["delibera543"] > 0
    condizione = condizione1 & condizione2
    if not df[sheet][condizione].empty:
        expndr = st.expander("Trovati errori fine prima di lockdown")
        with expndr:
            st.info("Tabella con errori fine prima di lockdown")
            make_grid(df[sheet][condizione].sort_values(by=["Cognome"]))
            # settiamo flag bool
            df[sheet].loc[condizione, "errOre543DataFine"] = True
            # x = dwnld(
            #    df[sheet][condizione].sort_values(by=["Cognome"]),
            #    "Scaricare tabella con errori data inizio maggiore di data fine",
            #    "errOre543DataFine",

    return df


def errComuneProvenienza(df):
    sheet = "sheet1"
    condizione1 = df[sheet]["utente"] == "comunale"
    condizione2 = pd.isnull(df[sheet]["ComuneProvenienza"])
    condizione = condizione1 & condizione2
    if not df[sheet][condizione].empty:
        expndr = st.expander(
            "Trovati errori inserimento comune provenienza per utente comunale"
        )
        with expndr:
            st.info(
                "Tabella con valori mancanti per comune di proivenienza per utente comunale"
            )
            make_grid(df[sheet][condizione].sort_values(by=["Cognome"]))
            # settiamo flag bool
            df[sheet].loc[condizione, "errComuneProvenienza"] = True
            # x = dwnld(
            #    df[sheet][condizione].sort_values(by=["Cognome"]),
            #    "Scaricare tabella con errori data inizio maggiore di data fine",
            #    "errComuneProvenienza",

    return df


def errCompilazione666(df):
    sheet = "sheet1"
    condizione1 = df[sheet]["utente"] == "comunale"
    condizione2 = pd.isnull(df[sheet]["delibera666"])
    condizione = condizione1 & condizione2
    if not df[sheet][condizione].empty:
        expndr = st.expander(
            "Trovati errori inserimento delibera 666 per utente comunale"
        )
        with expndr:
            st.info("Tabella con valori mancanti per delibera 666 per utente comunale")
            make_grid(df[sheet][condizione].sort_values(by=["Cognome"]))
            # settiamo flag bool
            df[sheet].loc[condizione, "errCompilazione666"] = True
            # x = dwnld(
            #    df[sheet][condizione].sort_values(by=["Cognome"]),
            #    "Scaricare tabella con errori data inizio maggiore di data fine",
            #    "errCompilazione666",

    return df


def errCompilazione543(df):
    sheet = "sheet1"
    condizione1 = df[sheet]["utente"] == "comunale"
    condizione2 = pd.isnull(df[sheet]["delibera543"])
    condizione = condizione1 & condizione2
    if not df[sheet][condizione].empty:
        expndr = st.expander(
            "Trovati errori inserimento delibera 543 per utente comunale"
        )
        with expndr:
            st.info("Tabella con valori mancanti per delibera 543 per utente comunale")
            make_grid(df[sheet][condizione].sort_values(by=["Cognome"]))
            # settiamo flag bool
            df[sheet].loc[condizione, "errCompilazione543"] = True
            # x = dwnld(
            #    df[sheet][condizione].sort_values(by=["Cognome"]),
            #    "Scaricare tabella con errori data inizio maggiore di data fine",
            #    "errCompilazione543",

    return df


def errCompilazioneEntrate(df):
    sheet = "sheet1"
    condizione1 = df[sheet]["utente"] == "comunale"
    condizione2 = pd.isnull(df[sheet]["Entrate"])
    condizione = condizione1 & condizione2
    if not df[sheet][condizione].empty:
        expndr = st.expander("Trovati errori inserimento entrate per utente comunale")
        with expndr:
            st.info("Tabella con valori mancanti per entrate per utente comunale")
            make_grid(df[sheet][condizione].sort_values(by=["Cognome"]))
            # settiamo flag bool
            df[sheet].loc[condizione, "errCompilazioneEntrate"] = True
            # x = dwnld(
            #    df[sheet][condizione].sort_values(by=["Cognome"]),
            #    "Scaricare tabella con errori data inizio maggiore di data fine",
            #    "errCompilazioneEntrate",

    return df


def errDataInizioAnnoRiferimento(df):
    sheet = "sheet0"
    condizione = df[sheet]["DataInizio"].dt.year >= int(ANNO_RIFERIMENTO)

    if not df[sheet][condizione].empty:
        expndr = st.expander(
            f"Trovati errori anno inizio utenti precedenti (foglio 0) maggiore di anno riferimento {ANNO_RIFERIMENTO}"
        )
        with expndr:
            st.info(
                f"Tabella con valori erratti per anno inizio utenti precedenti (foglio 0) maggiore di anno riferimento {ANNO_RIFERIMENTO}"
            )
            make_grid(df[sheet][condizione].sort_values(by=["Cognome"]))
            # settiamo flag bool
            df[sheet].loc[condizione, "errDataInizioAnnoRiferimento"] = True
            # x = dwnld(
            #    df[sheet][condizione].sort_values(by=["Cognome"]),
            #    "Scaricare tabella con errori data inizio maggiore di data fine",iloc

            #    "errDataInizioAnnoRiferimento",

    return df


def errOccorrenzeBambino(df):
    sheet = "sheet0"
    condizione1 = df[sheet].groupby("Cognome")["DataInizio"].transform("nunique") == 1
    condizione2 = df[sheet].groupby("Cognome")["Ente"].transform("nunique") > 1
    condizione = condizione1 & condizione2
    if not df[sheet][condizione].empty:
        expndr = st.expander(
            "Trovati errori occorrenze bambino in diverse strutture per stessa data inizio"
        )
        with expndr:
            st.info(
                "Tabella con errori occorrenze bambino in diverse strutture per stessa data inizio"
            )
            make_grid(df[sheet][condizione].sort_values(by=["Cognome"]))
            # settiamo flag bool
            df[sheet].loc[condizione, "errOccorrenzeBambino"] = True
            # x = dwnld(
            #    df[sheet][condizione].sort_values(by=["Cognome"]),
            #    "Scaricare tabella con errori data inizio maggiore di data fine",iloc

            #    "errOccorrenzeBambino")

    return df


################################# FINE CHECKS


def get_data(uploaded_files):
    df = {}
    dfout = {}
    dfout["sheet0"] = None
    dfout["sheet1"] = None

    st.info("Sono stati caricati " + str(len(uploaded_files)) + " files")
    status = st.empty()
    for uploaded_file in uploaded_files:
        try:
            status.info("[*] " + uploaded_file.name + " caricato")
            df1 = pd.read_excel(uploaded_file, 0)  # , usecols="A:F")
            df2 = pd.read_excel(uploaded_file, 1)
            df["sheet0"] = df1
            df["sheet1"] = df2
        except ValueError as errore_Riscontrato:
            st.error(
                uploaded_file.name
                + " non è un file Excel. Errore riscontrato: "
                + str(errore_Riscontrato)
            )
            continue

        # lasciamo prepare_data qui?
        try:
            status.info(f"[*] {uploaded_file.name} elaborato")
            df = prepare_data(df, uploaded_file.name)
        except ValueError as errore_Riscontrato:
            st.error(
                f"{str(uploaded_file.name)} --> ERRORE CONTROLLO GENERALE --> Il file non viene usato per l'elaborazione. Errore: {str(errore_Riscontrato)}"
            )
            continue
        # st.write('after prepare')
        # st.write(df['sheet0'])
        # st.write(df['sheet1'])

        # se dfout non esiste lo creiamo
        if dfout["sheet0"] is None:
            dfout["sheet0"] = pd.DataFrame(columns=df["sheet0"].columns)
            dfout["sheet0"] = df["sheet0"].copy()
            del df["sheet0"]
        else:
            # inserire qui il controllo del nome ente, che deve essere lo stesso per i file caricati?
            dfout["sheet0"] = pd.concat([dfout["sheet0"], df["sheet0"]])
            del df["sheet0"]
        # se dfout2 non esiste lo creiamo
        if dfout["sheet1"] is None:
            dfout["sheet1"] = pd.DataFrame(columns=df["sheet1"].columns)
            dfout["sheet1"] = df["sheet1"].copy()
            del df["sheet1"]
        else:
            # inserire qui il controllo del nome ente, che deve essere lo stesso per i file caricati?
            dfout["sheet1"] = pd.concat([dfout["sheet1"], df["sheet1"]])
            del df["sheet1"]

    # ora sono tutti concatenati e possiamo restituire il dataframe

    if not dfout["sheet0"].empty and not dfout["sheet1"].empty:
        status.success(
            "[*] Tutti i dati sono stati elaborati -  PER INIZIARE DA CAPO: RICARICARE LA PAGINA"
        )

    return dfout


def prepare_data(df, fn):

    df["sheet0"] = df["sheet0"].drop(["Unnamed: 6", "Unnamed: 7"], axis=1)
    df["sheet0"].columns = [
        "Cognome",
        "Nome",
        "utente",
        "ComuneProvenienza",
        "DataInizio",
        "DataFine",
    ]

    df["sheet1"].columns = [
        "Cognome",
        "Nome",
        "utente",
        "ComuneProvenienza",
        "DataInizio",
        "DataFine",
        "delibera666",
        "delibera543",
        "delibera733",
        "Entrate",
    ]

    df = make_bool_columns(df)

    for a in (0, 1):
        sheet = "sheet" + str(a)
        # st.write("working on sheet = "+sheet)
        microstruttura = df[sheet].iloc[1]
        microstruttura = microstruttura[1]
        # st.write(f"microstruttura {microstruttura}")
        res = isinstance(microstruttura, str)
        if not res:
            st.error(
                f"Manca informazione MICROSTRUTTURA nel foglio {a} nel file --> {fn}"
            )
            microstruttura = "assente"
            # settiamo flag bool
            df[sheet]["dataErrMicrostruttura"] = True
        ente = df[sheet].iloc[2]
        ente = ente[1]
        res = isinstance(ente, str)
        if not res:
            st.error(f"Manca informazione GESTORE nel foglio {a} nel file --> {fn}")
            ente = "assente"
            # settiamo flag bool
            df[sheet]["dataErrGestore"] = True
        df[sheet].insert(0, "Microstruttura", microstruttura)
        df[sheet].insert(0, "Ente", ente)
        # scriviamo anche il nome del file perché non si sa mai che non possa servire
        df[sheet].insert(0, "filename", fn)
        df[sheet] = df[sheet].drop(labels=range(0, 6), axis=0)
        validi = df[sheet]["Cognome"].notna()
        df[sheet] = df[sheet][validi]

        conditionInizio = pd.to_datetime(
            df[sheet]["DataInizio"], errors="coerce"
        ).isnull()
        conditionFine = pd.to_datetime(df[sheet]["DataFine"], errors="coerce").isnull()
        condition = conditionInizio | conditionFine

        if not df[sheet][condition].empty:
            expndr = st.expander(
                f"Trovati {len(df[sheet][condition])} errori formato data in foglio {a} del file --> {fn}"
            )
            with expndr:
                st.info("Errori nel formato della data inizio o data fine")
                make_grid(df[sheet][condition].sort_values(by=["Cognome"]))
                # settiamo la colonna bool
                df[sheet].loc[condition, "errData"] = True

        # SOLUZIONE TEMPORANEA (?)
        # se restituiamo con la data invalida crea problemi in seguito
        df[sheet] = df[sheet][~condition]
        # infine definiamo le colonne data come data
        df[sheet]["DataInizio"] = df[sheet]["DataInizio"].astype("datetime64[ns]")
        df[sheet]["DataFine"] = df[sheet]["DataFine"].astype("datetime64[ns]")
        # st.write(df[sheet])
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
    # global NO_ZERO
    # NO_ZERO = df["Ore totali rendicontate per il 2020"] > 0
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


def make_grid(dff):
    # st.write("make grid")
    # togliamo le colonne bool
    # st.write(dff)
    dff = drop_columns(dff)
    gridOptions = buildGrid(dff)
    AgGrid(dff, gridOptions=gridOptions, enable_enterprise_modules=True)


def buildGrid(data):
    gb = GridOptionsBuilder.from_dataframe(data)
    # gb.configure_pagination()
    gb.configure_side_bar()
    gb.configure_selection(selection_mode="multiple", use_checkbox=True)
    gb.configure_default_column(
        groupable=True, value=True, enableRowGroup=True, aggFunc="count", editable=True
    )
    gridOptions = gb.build()
    return gridOptions


def make_bool_columns(df):
    # aggiungiamo le colonne bool per ogni errore che abbiamo definito in ERRORDICT
    # ci serve per creare la tabella finale e per avere uno storico
    for a in (0, 1):
        sheet = "sheet" + str(a)
        for e in ERRORDICT.keys():
            df[sheet][e] = np.nan
            df[sheet][e] = df[sheet][e].astype("boolean")

    return df


def drop_columns(df):
    # st.write(df)
    for k in ERRORDICT:
        df = df.drop([k], axis=1)
    return df


app()
