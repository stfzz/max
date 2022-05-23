from os import path
from unicodedata import name

import numpy as np
import pandas as pd
import streamlit as st
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from this import d

st.set_page_config(
    page_title="Controllo Errori TAGESMÜTTER", layout="wide", page_icon="😃"  # 👽
)

DATAINIZIOMINIMA = pd.to_datetime("18.05.2020", format="%d.%m.%Y")
DATAFINEMASSIMA = pd.to_datetime("05.03.2020", format="%d.%m.%Y")
DATAFINEMASSIMA_COVID4 = pd.to_datetime("17.05.2020", format="%d.%m.%Y")

ORE2020 = 1920
KONTROLLEKINDERGARTEN_DATANASCITA_1 = pd.to_datetime("28.02.2017", format="%d.%m.%Y")
KONTROLLEKINDERGARTEN_DATAFINEASSISTENZA_1 = pd.to_datetime(
    "15.09.2019", format="%d.%m.%Y"
)
KONTROLLEKINDERGARTEN_DATANASCITA_2 = pd.to_datetime("01.03.2017", format="%d.%m.%Y")
KONTROLLEKINDERGARTEN_DATAFINEASSISTENZA_2 = pd.to_datetime(
    "15.09.2019", format="%d.%m.%Y"
)
EINGEWÖHNUNG_DATAINIZIO_MIN = pd.to_datetime("13.02.2020", format="%d.%m.%Y")
EINGEWÖHNUNG_DATAINIZIO_MAX = pd.to_datetime("05.03.2020", format="%d.%m.%Y")
KONTROLLECOVID_DATAINIZIOASSISTENZA = pd.to_datetime("05.03.2020", format="%d.%m.%Y")
KONTROLLECOVID_DATAFINEASSISTENZA2 = pd.to_datetime("30.10.2020", format="%d.%m.%Y")
KONTROLLECOVID2_DATAINIZIOASSISTENZA = pd.to_datetime("24.11.2020", format="%d.%m.%Y")
KONTROLLEEINGEWÖHNUNG543NOTBETREUUNG_DATAINIZIOMIN = pd.to_datetime(
    "26.10.2020", format="%d.%m.%Y"
)
KONTROLLEEINGEWÖHNUNG543NOTBETREUUNG_DATAINIZIOMAX = pd.to_datetime(
    "16.11.2020", format="%d.%m.%Y"
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

    "errCodFisc1": "Controllo formato codice fiscale",
    "errCodFisc2": "Controllo data nascita per codice fiscale",
    "errAgeChild": "Controllo età bambino",
    "errInizioMinoreFine": "Controllo date contrattuali",
    "errErrorePresenza": "Controllo errore presenza",
    "errErroreDati543": "Controllo errore dati 543",
    "errFineAssistenzaMax4Anni": "Controllo fine contratto assistenza",
    "errKindergarten_1": "Controllo Kindergarten #1",
    "errKindergarten_2": "Controllo Kindergarten #2",
    "errErroreFinanziamentoCompensativo": "Controllo finanziamento compensativo",
    "errErroreFinanziamentoCompensativo2": "Controllo finanziamento compensativo #2",
    "errErroreCovid": "Controllo Covid #1",
    "errErroreCovid2": "Controllo Covid #2",
    "errErroreCovid3": "Controllo Covid #3",
    "errErroreCovid4": "Contratti lockdown sospetti (Covid #4)",
    "errFehlerEingewöhnung": "Controllo Fehler Eingewöhnung",
    "errFehlerEingewöhnung543Lockdown": "Controllo Fehler Eingewöhnung 543 Lockdown",
    "errFehlerEingewöhnung543Notbetreuung": "Controllo Fehler Eingewöhnung 543 Notbetreuung",
    "errGesamtstundenVertragszeitraum": "Controllo ore complessive periodo contrattuale",
    "errSuperatoOreMassime1920": "Controllo ore complessive superiore a 1920",
    "errBambinoInPiuComuni": "Bambino presente in più comuni",
    "errPresentiAnnotazioni": "Bambini con annotazioni",
    "errMassimo543": "Controllo valore massimo ore 543",
    "errOreRendicontateZero": "Controllo ore rendicontate uguali a zero",
}


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


# aggiungiamo le colonne bool per ogni errore che abbiamo definito in ERRORDICT
# ci serve per creare la tabella finale e per avere uno storico
def make_bool_columns(df):
    for e in ERRORDICT.keys():
        df[e] = np.nan
        df[e] = df[e].astype("boolean")

    return df


# lancia i singoli controlli in base alla selezione fatta in GUI
def check_data2(df, checks):
    # definiamo come variabile globale la condizione logica per evitare i record con 
    # ore rendicontate 2020 = 0
    global NO_ZERO 
    NO_ZERO = df["Ore totali rendicontate per il 2020"] > 0
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

##################################
##################### START CHECKS

def errOreRendicontateZero(df):
    condizione = df['Ore totali rendicontate per il 2020'] == 0

    if not df[condizione].empty:
        expndr = st.expander(f"Trovati bambini con ore totali rendicontate = 0 ({len(df[condizione])} errori)")
        with expndr:
            st.info(f"Elenco dei bambini che hanno un valore di zero nelle ore rendicontate per l'anno 2020")
            make_grid(df[condizione])
            # settiamo la colonna bool
            df.loc[condizione, "errOreRendicontateZero"] = True
            x = dwnld(
                df[condizione],
                "SCARICARE TABELLA CON VALORE ZERO PER ORE RENDICONTATE 2020",
                "errOreRendicontateZero",
            )
        return df
    else:
        return df



def errFehlerEingewöhnung543Notbetreuung(df):
    data_inizio_minima = (
        df["Data inizio contratto (o data inizio assistenza se diversa)"]
        >= KONTROLLEEINGEWÖHNUNG543NOTBETREUUNG_DATAINIZIOMIN
    )
    data_inizio_massima = (
        df["Data inizio contratto (o data inizio assistenza se diversa)"]
        <= KONTROLLEEINGEWÖHNUNG543NOTBETREUUNG_DATAINIZIOMAX
    )
    ore_543 = (
        df[
            "Ore contrattualizzate non erogate\nai sensi della delibera\nn. 543_1025/2020"
        ]
        > 0
    )

    #NO_ZERO =  df["Ore totali rendicontate per il 2020"] > 0

    condizione_logica = data_inizio_minima & data_inizio_massima & ore_543 & NO_ZERO

    
    if not df[condizione_logica].empty:
        expndr = st.expander(f"Trovato errore Eingewöhnung 543 Notbetreuung ({len(df[condizione_logica])} errori)")
        with expndr:
            st.info(
                "Elenco dei bambini per cui è stato trovato un errore secondo la condizione:  (dataInizio >= 26.10.2020 e dataInizio <= 16.11.2020 e ore543 > 0)"
            )
            make_grid(df[condizione_logica])
            # settiamo la colonna bool
            df.loc[
                (condizione_logica),
                "errFehlerEingewöhnung543Notbetreuung",
            ] = True
            x = dwnld(
                df[condizione_logica],
                "SCARICARE TABELLA CON ERRORI Fehler Eingewöhnung 543 Notbetreuung",
                "FehlerEingewoehnung543Notbetreuung",
            )

        return df
    # se non trovato errore il df è restituito come è stato ricevuto
    else:
        return df


def errInizioMinoreFine(df):

    inizio_minore_fine = (
        df["Data inizio contratto (o data inizio assistenza se diversa)"]
        > df["Data fine contratto\n(o data fine assistenza se diversa) *"]
    )
    condizione_logica = inizio_minore_fine & NO_ZERO

    if not df[condizione_logica].empty:
        expndr = st.expander(f"Trovato errore date contrattuali ({len(df[condizione_logica])} errori)")
        with expndr:
            st.info(
                "Elenco dei bambini per cui è stato trovato un errore secondo la condizione:  (dataInizio > dataFine)"
            )
            make_grid(df[condizione_logica])
            # settiamo la colonna bool
            df.loc[condizione_logica, "errInizioMinoreFine"] = True
            x = dwnld(
                df[condizione_logica],
                "SCARICARE TABELLA CON ERRORI data Inizio maggiore data fine",
                "FehlerInzioMinoreFine",
            )

        return df
    # se non trovato errore il df è restituito come è stato ricevuto
    else:
        return df


def errCodFisc1(df):
    # definiamo condizione logica trovare per codice fiscale invalido usando regex
    codinvalido = (
        df["Codice fiscale"].str.match(
            "[A-Z|a-z][A-Z|a-z][A-Z|a-z][A-Z|a-z][A-Z|a-z][A-Z|a-z]\d\d[A-Z|a-z]\d\d[A-Z|a-z]\d\d\d[A-Z|a-z]"
        )
        == False
    )
    condizione_logica = codinvalido & NO_ZERO

    if not df[condizione_logica].empty:
        expndr = st.expander(f"Trovato errore formato del codice fiscale ({len(df[condizione_logica])} errori)")
        with expndr:
            st.info(
                "Elenco dei bambini che hanno un codice fiscale nel formato non corretto"
            )
            make_grid(df[condizione_logica])
            # settiamo il flag bool per la tabella finale
            df.loc[condizione_logica, "errCodFisc1"] = True
            x = dwnld(
                df[condizione_logica],
                "Scaricare tabella con errore codice fiscale",
                "ErroreCodiceFiscale",
            )

        return df
    # se non trovato errore il df è restituito come è stato ricevuto
    else:
        return df


def errCodFisc2(df):
    # condizione logica via regex per usare solo records con codfisc nel formato corretto
    codvalido = (
        df["Codice fiscale"].str.match(
            "[A-Z|a-z][A-Z|a-z][A-Z|a-z][A-Z|a-z][A-Z|a-z][A-Z|a-z]\d\d[A-Z|a-z]\d\d[A-Z|a-z]\d\d\d[A-Z|a-z]"
        )
        == True
    )
    # potremmo fare a meno di usare un nuovo df??
    # è più semplice se usiamo un nuovo df
    dfcod = df[codvalido]

    # condizione logica per i maschietti
    ggnot40 = dfcod["Codice fiscale"].str[9:11].astype(int) < 40

    # condizione logica per e femmine, che hanno giorno nascita da 40 in poi
    g40 = dfcod["Codice fiscale"].str[9:11].astype(int) > 40

    # nuovi df per maschietti e femmine
    df40 = dfcod[g40]
    dfnot40 = dfcod[ggnot40]

    # condizione logica verifica giorno nascita femmine
    gg40 = (
        pd.to_datetime(df40["Data di nascita"]).dt.day
        == df40["Codice fiscale"].str[9:11].astype(int) - 40
    )
    # condizione logica verifica giorno nascita maschietti
    gg = pd.to_datetime(dfnot40["Data di nascita"]).dt.day == dfnot40[
        "Codice fiscale"
    ].str[9:11].astype(int)

    # condizione logica per ANNO NASCITA uguale anno codfisc
    anno = dfcod["Data di nascita"].dt.year == 2000 + dfcod["Codice fiscale"].str[
        6:8
    ].astype(int)

    # condizione logica per MESE NASCITA
    mese = dfcod["Data di nascita"].dt.month == dfcod["Codice fiscale"].str[8:9].astype(
        "str"
    ).replace(
        {
            "A": "1",
            "B": "2",
            "C": "3",
            "D": "4",
            "E": "5",
            "H": "6",
            "L": "7",
            "M": "8",
            "P": "9",
            "R": "10",
            "S": "11",
            "T": "12",
            "F": "99",
            "G": "99",
            "I": "99",
            "J": "99",
            "K": "99",
            "N": "99",
            "O": "99",
            "Q": "99",
            "U": "99",
            "V": "99",
            "W": "99",
            "X": "99",
            "Y": "99",
            "Z": "99",
        }
    ).astype(
        int
    )

    # se trovato errore maschietti o femmine o mese o anno per maschi/femmine
    if (
        not dfcod[~mese].empty
        or not dfnot40[~gg].empty
        or not df40[~gg40].empty
        or not dfcod[~anno].empty
    ):
        expndr = st.expander(f"Trovato errore data nascita per codice fiscale ({len(dfcod[~mese]) + len(dfnot40[~gg]) + len(df40[~gg40]) + len(dfcod[~anno])} errori)")
        with expndr:
            st.info(
                "Elenco dei bambini per cui risulta un'incongruenza relativa alla data di nascita dichiarata e il codice fiscale"
            )
            # lista dei df con errori che concateniamo per fare un unico df
            frames = [dfnot40[~gg], df40[~gg40], dfcod[~mese], dfcod[~anno]]
            result = pd.concat(frames)
            make_grid(result)
            # settiamo il flag bool per i codfisc che sono presenti in results
            df.loc[
                df["Codice fiscale"].isin(result["Codice fiscale"]), "errCodFisc2"
            ] = True

        return df

    # se non trovato errore il df è restituito come è stato ricevuto
    else:
        return df


def errErrorePresenza(df):
    # condizione logica
    ore_rendicontate_uguale_zero = df["Ore totali rendicontate per il 2020"] == 0
    condizione_logica = ore_rendicontate_uguale_zero & NO_ZERO

    if not df[condizione_logica].empty:
        expndr = st.expander(f"Trovato errore presenza ({len(df[condizione_logica])} errori)")
        with expndr:
            st.info(
                "Elenco dei bambini per cui è stato trovato l'errore secondo la condizione: (Ore totali rendicontate = 0)"
            )
            make_grid(df[condizione_logica])
            # settiamo la colonna bool
            df.loc[condizione_logica, "errErrorePresenza"] = True
            x = dwnld(
                df[condizione_logica],
                "Scaricare tabella con errore presenzae",
                "ErrorePresenza",
            )

        return df
    # se non trovato errore il df è restituito come è stato ricevuto
    else:
        return df


def errAgeChild(df):

    giorni = (
        df["Data inizio contratto (o data inizio assistenza se diversa)"]
        - df["Data di nascita"]
    ).dt.days < 90
    condizione_logica = giorni & NO_ZERO

    if not df[condizione_logica].empty:
        expndr = st.expander(f"Trovato errore età bambino (< 90 giorni) ({len(df[condizione_logica])} errori)")
        with expndr:
            st.info(
                "Elenco dei bambini per cui è stato trovato l'errore secondo la condizione: il bambino ha meno di 3 mesi"
            )
            make_grid(df[condizione_logica])
            # settiamo la colonna bool
            df.loc[
                condizione_logica,
                "errAgeChild",
            ] = True
            x = dwnld(
                df[condizione_logica],
                "Scaricare tabella con errore età bambino",
                "ErroreEtaBambino",
            )

        return df
    else:
        return df


def errErroreDati543(df):

    errore_dati_543p1 = (
        df["Data inizio contratto (o data inizio assistenza se diversa)"]
        > DATAINIZIOMINIMA
    )
    errore_dati_543p2 = (
        df[
            "Ore contrattualizzate non erogate\nai sensi della delibera\nn. 543_1025/2020"
        ]
        == 0
    )

    errore_dati_543p3 = (
        df["Data fine contratto\n(o data fine assistenza se diversa) *"]
        < DATAFINEMASSIMA
    )

    condizione_logica = errore_dati_543p1 & errore_dati_543p2 & errore_dati_543p3 & NO_ZERO

    if not df[condizione_logica].empty:
        expndr = st.expander(f"Trovato errore dati 543 ({len(df[condizione_logica])} errori)")
        with expndr:
            st.info(
                "Elenco dei bambini per cui è stato trovato l'errore secondo la condizione: (dataFIne < 05.03.20 e dataInizio > 18.05.20 ore543 = 0)"
            )
            make_grid(df[condizione_logica])
            df.loc[
                condizione_logica,
                "errErroreDati543",
            ] = True
            x = dwnld(
                df[condizione_logica],
                "Scaricare tabella con errore dati 543",
                "ErroreDati543",
            )

        return df
    else:
        return df


def errFineAssistenzaMax4Anni(df):

    giorni = (
        df["Data fine contratto\n(o data fine assistenza se diversa) *"]
        - df["Data di nascita"]
    ).dt.days > 1464

    condizione_logica = giorni & NO_ZERO

    if not df[condizione_logica].empty:
        expndr = st.expander(f"Trovato errore fine contratto assistenza ({len(df[condizione_logica])} errori)")
        with expndr:
            st.info(
                "Elenco dei bambini per cui è stato trovato l'erorre secondo la condizione: dataFine non può essere oltre 4 anni da dataNascita"
            )
            make_grid(df[condizione_logica])

            df.loc[
                condizione_logica,
                "errFineAssistenzaMax4Anni",
            ] = True
            x = dwnld(
                df[giorni],
                "Scaricare tabella con errore fine contratto assistenza",
                "ErroreFineContratto",
            )

        return df
    else:
        return df


def errKindergarten_1(df):

    data_nascita = df["Data di nascita"] <= KONTROLLEKINDERGARTEN_DATANASCITA_1
    data_fine_assistenza = (
        df["Data fine contratto\n(o data fine assistenza se diversa) *"]
        > KONTROLLEKINDERGARTEN_DATAFINEASSISTENZA_1
    )
    condizione_logica = data_nascita & data_fine_assistenza & NO_ZERO
    if not df[condizione_logica].empty:
        expndr = st.expander(f"Trovato errore Kindergarten #1 ({len(df[condizione_logica])} errori)")
        with expndr:
            st.info(
                "Elenco dei bambini per cui è stato trovato l'errore secondo la condizione: (dataNascita <= 28.02.2017 e dataFine > 15.09.2019)"
            )
            make_grid(df[condizione_logica])
            df.loc[
                (condizione_logica),
                "errKindergarten_1",
            ] = True
            x = dwnld(
                df[condizione_logica],
                "Scaricare tabella con errore Kindergarten 1",
                "ErroreKindergarten1",
            )

        return df
    else:
        return df


def errKindergarten_2(df):

    data_nascita = df["Data di nascita"] >= KONTROLLEKINDERGARTEN_DATANASCITA_2
    data_nascita2 = df["Data di nascita"] < pd.to_datetime("01.01.2018", format="%d.%m.%Y")
    data_fine_ass = df[
        "Data fine contratto\n(o data fine assistenza se diversa) *"
    ] > pd.to_datetime(
        "15.09." + (pd.to_datetime(df["Data di nascita"]).dt.year + 3).astype("str"),
        format="%d.%m.%Y",
    )
    condizione_logica = data_nascita & data_nascita2 & data_fine_ass & NO_ZERO
    if not df[condizione_logica].empty:
        expndr = st.expander(f"Trovato errore Kindergarten #2 ({len(df[condizione_logica])} errori)")
        with expndr:
            st.info(
                "Elenco dei bambini per cui è stato trovato l'errore secondo la condizione: (dataNascita >= 01.03.2017 e dataFine > 15.09 dell'anno di nascita + 3 anni)"
            )
            make_grid(df[condizione_logica])
            df.loc[
                (condizione_logica),
                "errKindergarten_2",
            ] = True
            x = dwnld(
                df[condizione_logica],
                "Scaricare tabella con errore Kindergarten 2",
                "ErroreKindergarten2",
            )

        return df
    else:
        return df


def errErroreFinanziamentoCompensativo2(df):

    data_fine = (
        df["Data fine contratto\n(o data fine assistenza se diversa) *"]
        <= DATAINIZIOMINIMA
    )
    ore_compensative = (
        df[
            "Ore contrattualizzate non erogate\nnella fase 2 (finanziamento compensativo)"
        ]
        > 0
    )
    condizione_logica = data_fine & ore_compensative & NO_ZERO

    if not df[condizione_logica].empty:
        expndr = st.expander(f"Trovato errore finanziamento compensativo #2 ({len(df[condizione_logica])} errori)")
        with expndr:
            st.info(
                "Elenco dei bambini per cui è stato l'errore secondo la condizione: (dataFine <= 18.05.2020 e finanzCompensativo > 0 )"
            )
            make_grid(df[condizione_logica])

            df.loc[
                (condizione_logica),
                "errErroreFinanziamentoCompensativo2",
            ] = True
            x = dwnld(
                df[condizione_logica],
                "Scaricare tabella con errore finanziamento compensativo #2",
                "ErroreFinanziamentoCompensativo2",
            )

        return df
    else:
        return df


def errErroreFinanziamentoCompensativo(df):

    data_inizio = (
        df["Data inizio contratto (o data inizio assistenza se diversa)"]
        >= DATAFINEMASSIMA
    )
    ore_compensative = (
        df[
            "Ore contrattualizzate non erogate\nnella fase 2 (finanziamento compensativo)"
        ]
        > 0
    )
    condizione_logica = data_inizio & ore_compensative & NO_ZERO

    if not df[condizione_logica].empty:
        expndr = st.expander(f"Trovato errore finanziamento compensativo #1 ({len(df[condizione_logica])} errori)")
        with expndr:
            st.info(
                "Elenco dei bambini per cui è stato trovato l'errore secondo la condizione:  (dataInizio >= 05.03.2020 e finanzCompensativo > 0)"
            )
            make_grid(df[condizione_logica])

            df.loc[
                (condizione_logica),
                "errErroreFinanziamentoCompensativo",
            ] = True
            x = dwnld(
                df[condizione_logica],
                "Scaricare tabella con errore finanziamento compensativo",
                "ErroreFinanziamentoCompensativo",
            )

        return df
    else:
        return df


def errFehlerEingewöhnung(df):

    data_inizio_minima = (
        df["Data inizio contratto (o data inizio assistenza se diversa)"]
        >= EINGEWÖHNUNG_DATAINIZIO_MIN
    )
    data_inizio_massima = (
        df["Data inizio contratto (o data inizio assistenza se diversa)"]
        <= EINGEWÖHNUNG_DATAINIZIO_MAX
    )
    ore_contrattualizzate = (
        df[
            "Ore contrattualizzate non erogate\nnella fase 2 (finanziamento compensativo)"
        ]
        > 0
    )
    condizione_logica = data_inizio_minima & data_inizio_massima & ore_contrattualizzate & NO_ZERO

    if not df[condizione_logica].empty:
        expndr = st.expander(f"Trovato errore Eingewöhnung ({len(df[condizione_logica])} errori)")
        with expndr:
            st.info(
                "Elenco dei bambini per cui è stato trovato l'errore secondo la condizione: (dataInizio >= 13.02.2020 e dataInizio <= 05.03.2020 e finanzCompensativo) > 0)"
            )
            make_grid(
                df[condizione_logica]
            )

            df.loc[
                (condizione_logica),
                "errFehlerEingewöhnung",
            ] = True
            x = dwnld(
                df[condizione_logica],
                "Scaricare tabella con errore Eingewöhnung",
                "ErroreEingewöhnung",
            )

        return df
    else:
        return df


def errFehlerEingewöhnung543Lockdown(df):

    data_inizio_minima = (
        df["Data inizio contratto (o data inizio assistenza se diversa)"]
        >= EINGEWÖHNUNG_DATAINIZIO_MIN
    )
    data_inizio_massima = (
        df["Data inizio contratto (o data inizio assistenza se diversa)"]
        <= EINGEWÖHNUNG_DATAINIZIO_MAX
    )
    ore_543 = (
        df[
            "Ore contrattualizzate non erogate\nai sensi della delibera\nn. 543_1025/2020"
        ]
        > 0
    )
    condizione_logica = data_inizio_minima & data_inizio_massima & ore_543 & NO_ZERO

    if not df[condizione_logica].empty:
        expndr = st.expander(f"Trovato errore Eingewöhnung 543 Lockdown ({len(df[condizione_logica])} errori)")
        with expndr:
            st.info(
                "Elenco dei bambini per cui è stato trovato l'errore secondo la condizione: (dataInizio >= 13.02.2020 e dataInizio <= 05.03.2020 e ore543 > 0)"
            )
            make_grid(df[condizione_logica])

            df.loc[
                (condizione_logica),
                "errFehlerEingewöhnung543Lockdown",
            ] = True
            x = dwnld(
                df[condizione_logica],
                "Scaricare tabella con errore Eingewöhnung 543 Lockdown",
                "ErroreLockdown543",
            )

        return df
    else:
        return df


def errErroreCovid(df):

    data_fine_assistenza = (
        df["Data fine contratto\n(o data fine assistenza se diversa) *"]
        < KONTROLLECOVID_DATAINIZIOASSISTENZA
    )
    ore_543 = (
        df[
            "Ore contrattualizzate non erogate\nai sensi della delibera\nn. 543_1025/2020"
        ]
        > 0
    )
    ore_733 = (
        df["Ore contrattualizzate non erogate\nai sensi della delibera\nn. 733/2020"]
        > 0
    )
    ore_contrattualizzate = (
        df[
            "Ore contrattualizzate non erogate\nnella fase 2 (finanziamento compensativo)"
        ]
        > 0
    )
    condizione_logica = data_fine_assistenza & (ore_543 | ore_733 | ore_contrattualizzate) & NO_ZERO

    if not df[condizione_logica].empty:
        expndr = st.expander(f"Trovato errore Covid #1 ({len(df[condizione_logica])} errori)")
        with expndr:
            st.info(
                "Elenco dei bambini per cui è stato trovato l'errore secondo la condizione: (dataFine < 05.03.2020 e Ore543 > 0) oppure (dataFine < 05.03.2020 e Ore733 > 0) oppure (dataFine < 05.03.2020 e finanzCompensativo) > 0)"
            )
            make_grid(
                df[condizione_logica]
            )

            df.loc[
                (condizione_logica),
                "errErroreCovid",
            ] = True
            x = dwnld(
                df[condizione_logica],
                "Scaricare tabella con errore Covid 1",
                "ErroreCovid1",
            )

        return df
    else:
        return df


def errErroreCovid2(df):

    data_inizio_ass = (
        df["Data inizio contratto (o data inizio assistenza se diversa)"]
        >= KONTROLLECOVID2_DATAINIZIOASSISTENZA
    )
    ore_543 = (
        df[
            "Ore contrattualizzate non erogate\nai sensi della delibera\nn. 543_1025/2020"
        ]
        > 0
    )
    ore_contrattualizzate = (
        df[
            "Ore contrattualizzate non erogate\nnella fase 2 (finanziamento compensativo)"
        ]
        > 0
    )

    # non abbiamo messo la condizione per evitare records con ore rendicontate = 0
    if not df[
        (data_inizio_ass & ore_543) | (data_inizio_ass & ore_contrattualizzate)
    ].empty:
        expndr = st.expander(f"Trovato errore Covid #2 ({len(df[(data_inizio_ass & ore_543) | (data_inizio_ass & ore_contrattualizzate)])} errori)")
        with expndr:
            st.info(
                "Elenco dei bambini per cui risulta l'errore secondo la condizione: (data inizio >= 24.11.2020 e ore543 > 0) oppure (data inizio >= 24.11.2020 e finanzCompensativo > 0)"
            )
            make_grid(
                df[
                    (data_inizio_ass & ore_543)
                    | (data_inizio_ass & ore_contrattualizzate)
                ]
            )

            df.loc[
                (
                    (data_inizio_ass & ore_543)
                    | (data_inizio_ass & ore_contrattualizzate)
                ),
                "errErroreCovid2",
            ] = True
            x = dwnld(
                df[
                    (data_inizio_ass & ore_543)
                    | (data_inizio_ass & ore_contrattualizzate)
                ],
                "Scaricare tabella con errore Covid 2",
                "ErroreCovid2",
            )

        return df
    else:
        return df


def errErroreCovid3(df):
    data_inizio = (
        df["Data inizio contratto (o data inizio assistenza se diversa)"]
        >= KONTROLLECOVID_DATAINIZIOASSISTENZA
    )
    data_fine = (
        df["Data fine contratto\n(o data fine assistenza se diversa) *"]
        <= KONTROLLECOVID_DATAFINEASSISTENZA2
    )
    ore_543 = (
        df[
            "Ore contrattualizzate non erogate\nai sensi della delibera\nn. 543_1025/2020"
        ]
        > 0
    )
    condizione_logica = data_inizio & data_fine & ore_543 & NO_ZERO

    if not df[condizione_logica].empty:
        expndr = st.expander(f"Trovato errore Covid #3 ({len(df[condizione_logica])} errori)")
        with expndr:
            st.info(
                "Elenco dei bambini per cui risulta l'errore secondo la condizione: (dataInizio >= 5/3/20) e (dataFine <= 30/10/20) e (ore543 > 0)"
            )
            make_grid(df[condizione_logica])

            df.loc[
                condizione_logica,
                "errErroreCovid3",
            ] = True
            x = dwnld(
                df[condizione_logica],
                "Scaricare tabella con errore Covid 3",
                "ErroreCovid3",
            )

        return df
    else:
        return df


def errErroreCovid4(df):
    condizione1 = (
        df["Data inizio contratto (o data inizio assistenza se diversa)"]
        >= DATAFINEMASSIMA
    )
    condizione2 = (
        df["Data inizio contratto (o data inizio assistenza se diversa)"]
        <= DATAFINEMASSIMA_COVID4
    )
    condizione_logica = condizione1 & condizione2 & NO_ZERO

    if not df[condizione_logica].empty:
        expndr = st.expander(f"Trovato contratti lockdown da controllare (Covid #4) ({len(df[condizione_logica])} errori)")
        with expndr:
            st.info(
                "Elenco dei bambini per cui è soddisfatta la condizione: (5/3/2020 <= dataInizio <= 17/5/2020)"
            )
            make_grid(df[condizione_logica])

            df.loc[
                condizione_logica,
                "errErroreCovid4",
            ] = True
            x = dwnld(
                df[condizione_logica],
                "Scaricare tabella con contratti lockdown da controllare (Covid #4)",
                "ErroreCovid4",
            )

        return df
    else:
        return df


def errGesamtstundenVertragszeitraum(
    df,
):  # incompleto perchè va verificato su più file Excel
    # la condizione logica per trovare l'errore
    #condizioneerrore1 = ((1920 * (df["GiorniAssistenzaAnnoRiferimento"])) / 366) < df[
    #    "Ore totali rendicontate per il 2020"
    #]

    #conta_cod_fiscale = (
    #    df.groupby("Codice fiscale")["Codice fiscale"].transform("count") == 1
    #)
    #condizione_logica = condizioneerrore1 & conta_cod_fiscale & NO_ZERO
    
    # presenza errore in caso di codfisc che occorre solo una volta
    #df1 = df[condizioneerrore1 & conta_cod_fiscale]

    condizioneerrore2 = (
        (
            1920
            * (
                df.groupby("Codice fiscale")[
                    "GiorniAssistenzaAnnoRiferimento"
                ].transform("sum")
            )
            / 366
        )
    ) < df.groupby("Codice fiscale")["Ore totali rendicontate per il 2020"].transform(
        "sum"
    )

    condizione_logica = condizioneerrore2 & NO_ZERO

    if not df[condizione_logica].empty:
        expndr = st.expander(
            f"Trovato errore ore -Proportion Maximalstunden überschritten- (ATTENZIONE: va verificato!) (trovati {len(df[condizione_logica])} errori)"
        )
        with expndr:
            st.info(
                "Elenco dei bambini per cui la proporzione delle ore per i giorni di assistenza è inferiore alla somma delle ore rendicontate per il 2020. Secondo la formula: (1920*(giorniAssistenzaAnnoRiferimento)/366) < (oreTotaliRendicontate2020))"
            )
            make_grid(df[condizione_logica])

            # settiamo il flag bool per la tabella finale
            df.loc[condizione_logica, "errGesamtstundenVertragszeitraum"] = True
            x = dwnld(
                df[condizione_logica],
                "Scaricare tabella con errore ore complessive per durata contrattuale",
                "ErroreOreComplessive",
            )

        return df
    # se non trovato errore il df è restituito come è stato ricevuto
    else:
        return df


def errSuperatoOreMassime1920(df):
    # condizionlogica = (
    #    df.groupby("Codice fiscale")["Codice fiscale"].transform("count") > 1
    # )
    condizionelogica2 = (
        df.groupby("Codice fiscale")["Ore totali rendicontate per il 2020"].transform(
            "sum"
        )
        > 1920
    )
    condizione_logica = condizionelogica2 & NO_ZERO

    if not df[condizione_logica].empty:
        expndr = st.expander(f"Trovato errore ore complessive maggiore di 1920 (trovati {len(df[condizione_logica])} errori)")
        with expndr:
            st.info(
                "Elenco dei bambini per cui la somma delle ore totali rendicontate per il 2020 è maggiore di 1920"
            )
            make_grid(df[condizione_logica])

            # settiamo flag per tabella finale
            df.loc[condizione_logica, "errSuperatoOreMassime1920"] = True
            x = dwnld(
                df[condizione_logica],
                "Scaricare tabella con errore ore complessive maggiore 1920",
                "ErroreOre1920",
            )

        return df
    else:
        return df


def errBambinoInPiuComuni(df):
    condizionlogica1 = df.groupby("Codice fiscale")["Comune"].transform("nunique") > 1
    condizione_logica = condizionlogica1 & NO_ZERO
    if not df[condizione_logica].empty:
        expndr = st.expander(f"Trovati bambini presenti in più comuni (trovati {len(df[condizione_logica])} errori)")
        with expndr:
            st.info("Elenco dei bambini trovati in più comuni (in più file Excel)")
            make_grid(df[condizione_logica])

            # settiamo flag bool per tabella finale
            df.loc[condizione_logica, "errBambinoInPiuComuni"] = True
            x = dwnld(
                df[condizione_logica],
                "Scaricare tabella con bambini in più comuni",
                "errBambinoInPiuComuni",
            )
        return df
    else:
        return df


def errPresentiAnnotazioni(df):
    condizione = (
        df["Cognome e nome bambino"].str.contains("[@_!#$%^&*()<>?/|}{~:]") == True
    )
    condizione_logica = condizione & NO_ZERO

    if not df[condizione_logica].empty:
        expndr = st.expander(f"Trovati bambini con annotazioni (trovati {len(df[condizione_logica])} errori)")
        with expndr:
            st.info(
                "Elenco dei bambini che hanno una annotazione, o direttamente nel nome o nella colonna del numero progressivo (dal quale viene cancellato e aggiunto al nome)"
            )
            make_grid(df[condizione_logica])

            # settiamo flag bool
            df.loc[condizione_logica, "errPresentiAnnotazioni"] = True
            x = dwnld(
                df[condizione_logica],
                "Scaricare tabella con bambini con annotazioni",
                "errPresentiAnnotazioni",
            )
        return df
    else:
        return df


def errMassimo543(df):

    cond1 = df[
        "Data inizio contratto (o data inizio assistenza se diversa)"
    ] <= pd.to_datetime("05.03.2020", format="%d.%m.%Y")
    cond1b = df[
        "Data fine contratto\n(o data fine assistenza se diversa) *"
    ] > pd.to_datetime("17.05.2020", format="%d.%m.%Y")

    cond2 = df[
        "Data inizio contratto (o data inizio assistenza se diversa)"
    ] <= pd.to_datetime("16.11.2020", format="%d.%m.%Y")
    cond2b = df[
        "Data fine contratto\n(o data fine assistenza se diversa) *"
    ] >= pd.to_datetime("23.11.2020", format="%d.%m.%Y")

    cond3 = df[
        "Data inizio contratto (o data inizio assistenza se diversa)"
    ] <= pd.to_datetime("05.11.2020", format="%d.%m.%Y")
    cond3b = df[
        "Data fine contratto\n(o data fine assistenza se diversa) *"
    ] > pd.to_datetime("06.11.2020", format="%d.%m.%Y")

    cond3c = (
        df["Comune di residenza assistente domiciliare all'infanzia"].str.lower().str.contains(
            "eppan"
        )
        | df["Comune di residenza assistente domiciliare all'infanzia"].str.lower().str.contains(
            "bozen"
        )
        | df["Comune di residenza assistente domiciliare all'infanzia"].str.lower().str.contains(
            "branzoll"
        )
        | df["Comune di residenza assistente domiciliare all'infanzia"].str.lower().str.contains(
            "freienfeld"
        )
        | df["Comune di residenza assistente domiciliare all'infanzia"].str.lower().str.contains(
            "auer"
        )
        | df["Comune di residenza assistente domiciliare all'infanzia"].str.lower().str.contains(
            "leifers"
        )
        | df["Comune di residenza assistente domiciliare all'infanzia"].str.lower().str.contains(
            "mals"
        )
        | df["Comune di residenza assistente domiciliare all'infanzia"].str.lower().str.contains(
            "nals"
        )
        | df["Comune di residenza assistente domiciliare all'infanzia"].str.lower().str.contains(
            "welschnofen"
        )
        | df["Comune di residenza assistente domiciliare all'infanzia"].str.lower().str.contains(
            "ratschings"
        )
        | df["Comune di residenza assistente domiciliare all'infanzia"].str.lower().str.contains(
            "pfatten"
        )
        | df["Comune di residenza assistente domiciliare all'infanzia"].str.lower().str.contains(
            "feldthurns"
        )
        | df["Comune di residenza assistente domiciliare all'infanzia"].str.lower().str.contains(
            "sterzing"
        )
        | df["Comune di residenza assistente domiciliare all'infanzia"].str.lower().str.contains(
            "bolzano"
        )
        | df["Comune di residenza assistente domiciliare all'infanzia"].str.lower().str.contains(
            "bronzolo"
        )
        | df["Comune di residenza assistente domiciliare all'infanzia"].str.lower().str.contains(
            "trens"
        )
        | df["Comune di residenza assistente domiciliare all'infanzia"].str.lower().str.contains(
            "egna"
        )
        | df["Comune di residenza assistente domiciliare all'infanzia"].str.lower().str.contains(
            "laives"
        )
        | df["Comune di residenza assistente domiciliare all'infanzia"].str.lower().str.contains(
            "malles"
        )
        | df["Comune di residenza assistente domiciliare all'infanzia"].str.lower().str.contains(
            "nalles"
        )
        | df["Comune di residenza assistente domiciliare all'infanzia"].str.lower().str.contains(
            "levante"
        )
        | df["Comune di residenza assistente domiciliare all'infanzia"].str.lower().str.contains(
            "racines"
        )
        | df["Comune di residenza assistente domiciliare all'infanzia"].str.lower().str.contains(
            "vadena"
        )
        | df["Comune di residenza assistente domiciliare all'infanzia"].str.lower().str.contains(
            "velturno"
        )
        | df["Comune di residenza assistente domiciliare all'infanzia"].str.lower().str.contains(
            "vipiteno"
        )
    )



    if not df[cond1 & cond1b & NO_ZERO].empty:
        df.loc[cond1 & cond1b & NO_ZERO,"gg1"] = 74
    else:
        df[cond1 & cond1b & NO_ZERO,"gg1"] = 0

    if not df[cond2 & cond2b & NO_ZERO].empty:
        df.loc[cond2 & cond2b & NO_ZERO,"gg2"] = 8
    else:
        df.loc[cond2 & cond2b & NO_ZERO,"gg2"] = 0

    if not df[cond3 & cond3b & cond3c & NO_ZERO].empty:
        df.loc[cond3 & cond3b & cond3c & NO_ZERO, "gg3"] = 2
    else:
        df.loc[cond3 & cond3b & cond3c & NO_ZERO, "gg3"] = 0

    df.insert(13, "massimo543", 0)

    df["massimo543"] = (
        (
            (
                0.055
                * (
                    df["Ore totali rendicontate per il 2020"]
                    / df["GiorniAssistenzaAnnoRiferimento"]
                )
            )
            + df["Ore totali rendicontate per il 2020"]
        )
        / df["GiorniAssistenzaAnnoRiferimento"]
    ) * (df["gg1"] + df["gg2"] + df["gg3"])

    df["massimo543"] = df["massimo543"].astype(int)



    if not df[(cond1 & cond1b & NO_ZERO) | (cond2 & cond2b & NO_ZERO) | (cond3 & cond3b & cond3c & NO_ZERO)].empty:
        expndr = st.expander(f"Calcolata colonna massimo ore 543 (trovati {len(df[(cond1 & cond1b & NO_ZERO) | (cond2 & cond2b & NO_ZERO) | (cond3 & cond3b & cond3c & NO_ZERO)])} errori)")
        with expndr:
            st.info(
                "Elenco dei bambini per cui è stato calcolato il valore ore massime 543"
            )
            make_grid(
                df[(cond1 & cond1b & NO_ZERO) | (cond2 & cond2b & NO_ZERO) | (cond3 & cond3b & cond3c & NO_ZERO)]
            )

            # settiamo flag bool
            df.loc[
                (cond1 & cond1b & NO_ZERO) | (cond2 & cond2b & NO_ZERO) | (cond3 & cond3b & cond3c & NO_ZERO),
                "errMassimo543",
            ] = True
            x = dwnld(
                df[(cond1 & cond1b & NO_ZERO) | (cond2 & cond2b & NO_ZERO) | (cond3 & cond3b & cond3c & NO_ZERO)],
                "Scaricare tabella con bambini con valore massimo 543 calcolato",
                "errMassimo543",
            )
        # st.write(df[(cond1 & cond1b) | (cond2 & cond2b) | (cond3 & cond3b & cond3c)])
        return df
    else:
        return df


##################### FINE CHECKS
##################################


def make_grid(dff):
    # togliamo le colonne bool
    dff = drop_columns(dff)
    gridOptions = buildGrid(dff)
    AgGrid(dff, gridOptions=gridOptions, enable_enterprise_modules=True)


def get_data(uploaded_files, anno_riferimento):
    dfout = None
    st.info("Sono stati caricati " + str(len(uploaded_files)) + " files")
    status = st.empty()
    for uploaded_file in uploaded_files:
        try:
            status.info("[*] " + uploaded_file.name + " caricato")
            df = pd.read_excel(uploaded_file, usecols = "A:M")
        except:
            st.error(uploaded_file.name + " non è un file Excel")
            continue

        # lasciamo prepare_data qui?
        try:
            status.info(f"[*] {uploaded_file.name} elaborato")
            df = prepare_data(df, uploaded_file, anno_riferimento)
        except:
            st.error(
                f"{uploaded_file.name} --> ERRORE CONTROLLO GENERALE --> Il file non viene usato per l'elaborazione"
            )
            continue

        # se dfout non esiste lo creiamo
        if dfout is None:
            dfout = pd.DataFrame(columns=df.columns)
            dfout = df
        else:
            # inserire qui il controllo del nome ente, che deve essere lo stesso per i file caricati?
            dfout = pd.concat([dfout, df])

    # ora sono tutti concatenati e possiamo restituire il dataframe
    if dfout is not None:
        status.success(
            "[*] Tutti i dati sono stati elaborati -  PER INIZIARE DA CAPO: RICARICARE LA PAGINA"
        )
    
    # ci servono inizializzate per il calcolo delle ora massime 543
    dfout["gg1"] = 0
    dfout["gg2"] = 0
    dfout["gg3"] = 0

    return dfout


def choose_checks2():
    checks = {}
    st.write("")
    a = 1
    # creiamo le checkbox e i valori dinamicamente in base al dictionary che contiene
    # la lista degli errori
    expndr = st.expander("SCELTA CONTROLLI", expanded=True)
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


def prepare_data(df, uploaded_file, anno_riferimento):

    # DOBBIAMO RINOMINARE TUTTE LE COLONNE PERCHÉ ARRIVANO
    # IN TEDESCO E ITALIANO - USIAMO ITALIANO
    # E SPERIAMO SIANO TUTTE NELLO STESSO ORDINE
    df.columns = [
        "Numero \nprogressivo",
        "Cognome e nome bambino",
        "Data di nascita",
        "Codice fiscale",
        "Assistente domiciliare all'infanzia",
        "Comune di residenza assistente domiciliare all'infanzia",
        "Data inizio contratto (o data inizio assistenza se diversa)",
        "Data fine contratto\n(o data fine assistenza se diversa) *",
        "Ore di assistenza \n ai sensi della delibera\nn. 666/2019",
        "Ore contrattualizzate non erogate\nai sensi della delibera\nn. 543_1025/2020",
        "Ore contrattualizzate non erogate\nai sensi della delibera\nn. 733/2020",
        "Ore contrattualizzate non erogate\nnella fase 2 (finanziamento compensativo)",
        "Ore totali rendicontate per il 2020",
    ]

    # estraiamo comune e nome ente da dove ci aspettiamo che siano
    # nel dataframe creato dal singolo file Excel
    traeger = df.iloc[2]
    # ente e traeger in e4/e5
    if type(traeger[4]) == type("string"):
        traeger = traeger[4].title()
        gemeinde = df.iloc[3]
        gemeinde = gemeinde[4]
    # ente/traeger in d4/d5
    else:
        traeger = traeger[3].title()
        gemeinde = df.iloc[3]
        gemeinde = gemeinde[3]

    # cancelliamo le righe che non ci servono
    df = df.drop(labels=range(0, 8), axis=0)

    # dobbiamo intercettare se c'è un * nella colonna del numero progressivo
    # sostituire l'asterisco con 99 e aggiungere l'asterisco al nome
    cond = df["Numero \nprogressivo"] == "*"
    df.loc[cond, "Cognome e nome bambino"] += " *"
    df.loc[cond, "Numero \nprogressivo"] = 99


    # prima convertiamo la colonna in numerica, forzando NaN sui non numerici
    df["Numero \nprogressivo"] = pd.to_numeric(
        df["Numero \nprogressivo"], errors="coerce"
    )

    # selezioniamo solo le righe che hanno un valore numerico in *Numero progressivo*
    # in questo modo eliminiamo le righe inutili dopo l'ultimo *numero progressivo*
    validi = df["Numero \nprogressivo"].notna()

    # teniamo solo record validi
    df = df[validi]

    # elimiamo colonne che sono servono più
    df = df.drop(["Numero \nprogressivo"], axis=1)

    # se troviamo data fine vuota la mettiamo al 31/12 dell'anno riferimento
    condizione = pd.isnull(
        df["Data fine contratto\n(o data fine assistenza se diversa) *"]
    )
    df.loc[
        condizione, "Data fine contratto\n(o data fine assistenza se diversa) *"
    ] = "12-31-" + str(anno_riferimento)
    df["Data fine contratto\n(o data fine assistenza se diversa) *"] = df[
        "Data fine contratto\n(o data fine assistenza se diversa) *"
    ].astype("datetime64[ns]")

    # convertiamo colonne in data
    try:
        df["Data di nascita"] = df["Data di nascita"].astype("datetime64[ns]")
    except:
        st.error(f"{uploaded_file.name} --> data di nascita contiene valori non data")
    try:
        df["Data fine contratto\n(o data fine assistenza se diversa) *"] = df[
            "Data fine contratto\n(o data fine assistenza se diversa) *"
        ].astype("datetime64[ns]")
    except:
        st.error(
            f"{uploaded_file.name} --> data fine contratto contiene valori non data"
        )

    try:
        df["Data inizio contratto (o data inizio assistenza se diversa)"] = df[
            "Data inizio contratto (o data inizio assistenza se diversa)"
        ].astype("datetime64[ns]")
    except:
        st.error(
            f"{uploaded_file.name} --> data inizio contratto contiene valori non data"
        )

    # creiamo due nuove colonne e le riempiamo con comune ed ente
    # estratti prima
    df.insert(1, "Comune", gemeinde)
    df.insert(1, "Ente", traeger)

    # sostituiamo tutti i NaN con *0*
    df = df.fillna(0)

    # scriviamo anche il nome del file perché non si sa mai che non possa servire
    df.insert(0, "filename", uploaded_file.name)
    # df['filename'] = uploaded_file.name

    # assicuriamo che codice fiscale sia in maiuscolo
    df["Codice fiscale"] = df["Codice fiscale"].str.upper()

    # aggiungiamo le colonne che ci servono più tardi per i codici errore
    # e assegniamo un valore dummy
    dfbool = make_bool_columns(df)



    return dfbool


def compute_hours(df, ar):
    ar = int(ar)  # convertiamo anno riferimento in *int*
    df["inizioNorm"] = df[
        "Data inizio contratto (o data inizio assistenza se diversa)"
    ]  # intanto inseriamo i valori che ci sono
    df["fineNorm"] = df["Data fine contratto\n(o data fine assistenza se diversa) *"]

    # se data inizio minore di anno riferimento allora mettiamo il 1. gennaio dell'anno riferimento
    iniz = df["inizioNorm"].dt.year < ar  # condizione logica
    df.loc[iniz, "inizioNorm"] = "01-01-" + str(
        ar
    )  # cerchiamo i valori < anno riferimento e sostituiamo con 01/01

    fin = df["fineNorm"].dt.year > ar  # condizione logica
    df.loc[fin, "fineNorm"] = "12-31-" + str(ar)  # sostituzione
    df.insert(
        9, "GiorniAssistenzaAnnoRiferimento", 0
    )  # aggiungiamo colonna e mettiamo anno riferimento
    df["GiorniAssistenzaAnnoRiferimento"] = (
        df["fineNorm"] - df["inizioNorm"]
    ).dt.days + 1  # calcolo giorni anno riferimento. +1 perché il giorno fine va incluso
    # df = df.drop(['inizio','fine'], axis=1) # le colonne non servono più
    return df


def drop_columns(df):

    for k in ERRORDICT:
        df = df.drop([k], axis=1)

    # servivano per calcolare ore massime 543
    # non sicuro che sia il posto migliore per dropparle
    df = df.drop(["gg1", "gg2", "gg3"], axis=1)                                            

    return df


def dwnld(df, k, ff):
    if ff != "soloerrori":
        df = drop_columns(df)

    f = df.to_csv(sep=";").encode(
        "utf-8-sig"
    )  # dobbiamo usare questo encoding altrimenti windoof di m***a sballa Umlaute
    st.download_button(
        label=k,
        data=f,
        file_name=ff + ".csv",
        mime="text/csv",
        key=k,
    )
    return "x"  # inutile


def make_df_solo_errori(dffinal):
    # creiamo la condizione logica
    # almeno un errore per tipologia errore
    for e in ERRORDICT.keys():
        # non lo vogliamo nel df degli errori perché sono tanti, troppi
        if e == "errMassimo543":
            continue
        # prima instanziazione di "condizione"
        # in questo modo viene creato con type giusto
        # local() contiene variabili e functions nel namespace locale
        if "condizione" not in locals():
            condizione = dffinal[e] == True
        else:
            # soluzione semplice: concateniamo le condizioni
            # per i controlli fatti
            condizione = condizione | dffinal[e] == True
    # creiamo df con soli record con errore
    
    dffinal = dffinal[condizione]
    # droppiamo la colonna che non vogliamo
    dffinal = dffinal.drop(["errMassimo543"], axis = 1)

    return dffinal


def app():

    st.header("FAMILIENAGENTUR - AGENZIA PER LA FAMIGLIA")
    st.subheader("Controllo errori TAGESMÜTTER (v. 0.9.30)")
    dfout = None

    # carichiamo qui la tabella dello storico??
    if path.exists("storico.xlsx"):
        c1, c2 = st.columns(2)
        c1.info("Trovato file storico")
    #    storico = c2.checkbox("caricare file storico?")
    #    if storico:
    #        pass

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
        dfout = get_data(uploaded_files, anno_riferimento)
        if dfout is not None:
            dfout = compute_hours(dfout, anno_riferimento)
            dffinal = check_data2(dfout, checks)
            st.write("")
            st.info("Tabelle elaborate")

            # la tabella finale, contiene TUTTI i record
            expndr = st.expander("TABELLA FINALE ELABORATA - TUTTI I DATI")
            with expndr:
                # facciamo la grid qui così evitiamo che vengano
                # droppate le colonne flag bool
                gridOptions = buildGrid(dffinal)
                AgGrid(dffinal, gridOptions=gridOptions, enable_enterprise_modules=True)
                dwnld(dffinal, "SCARICARE TABELLA CON TUTTI I DATI", "tuttidati")

            # la tabella finale che contiene soltanto record con ALMENO UN ERRORE
            dffinalerr = make_df_solo_errori(dffinal)
            expndr = st.expander("TABELLA FINALE ELABORATA - SOLO ERRORI (senza massimo543)")
            with expndr:
                # facciamo la grid qui così evitiamo che vengano
                # droppate le colonne flag bool
                gridOptions = buildGrid(dffinalerr)
                AgGrid(
                    dffinalerr, gridOptions=gridOptions, enable_enterprise_modules=True
                )
                dwnld(dffinalerr, "SCARICARE TABELLA CON SOLO ERRORI", "soloerrori")

        # salviamo qui la tabella finale??
        st.write("")
        st.write("")
        try:
            dffinalerr.to_excel("storico.xlsx")
            st.success("Salvato file storico: OK")
        except:
            st.error("ERRORE salvataggio file storico")


app()
