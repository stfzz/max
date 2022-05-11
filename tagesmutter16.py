from this import d
from unicodedata import name

from os import path
import pandas as pd
import streamlit as st
import numpy as np

from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder

st.set_page_config(
    page_title="Controllo TAGESMÜTTER", layout="wide", page_icon="🤔"  # 👽
)

DATAINIZIOMINIMA = pd.to_datetime("18.05.2020", format="%d.%m.%Y")
DATAFINEMASSIMA = pd.to_datetime("05.03.2020", format="%d.%m.%Y")
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
KONTROLLECOVID_DATAFINEASSISTENZA = pd.to_datetime("03.05.2020", format="%d.%m.%Y")
KONTROLLECOVID2_DATAINIZIOASSISTENZA = pd.to_datetime("24.11.2020", format="%d.%m.%Y")
KONTROLLEEINGEWÖHNUNG543NOTBETREUUNG_DATAINIZIOMIN = pd.to_datetime(
    "26.10.2020", format="%d.%m.%Y"
)
KONTROLLEEINGEWÖHNUNG543NOTBETREUUNG_DATAINIZIOMAX = pd.to_datetime(
    "16.11.2020", format="%d.%m.%Y"
)


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


def errorChecksList():
    # gestiamo tutto quello che riguarda i controlli da fare qui
    # in seguito usiamo la key del dict per creare sia le checkbox
    # sia per chiamare le funzioni
    error_dict = {
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
        "errFehlerEingewöhnung": "Controllo Fehler Eingewöhnung",
        "errErroreCovid": "Controllo Covid #1",
        "errErroreCovid2": "Controllo Covid #2",
        "errFehlerEingewöhnung543Lockdown": "Controllo Fehler Eingewöhnung 543 Lockdown",
        "errFehlerEingewöhnung543Notbetreuung": "Controllo Fehler Eingewöhnung 543 Notbetreuung",
        "errGesamtstundenVertragszeitraum": "Controllo ore complessive per periodo contrattuale",
        "errSuperatoOreMassime1920": "Controllo ore complessive superiore a 1920",
    }
    return error_dict


ERRORDICT = errorChecksList()

# aggiungiamo le colonne bool per ogni errore che abbiamo definito in ERRORDICT
# ci serve per creare la tabella finale e per avere uno storico
def make_bool_columns(df):
    for e in ERRORDICT.keys():
        df[e] = np.nan
        df[e] = df[e].astype("boolean")

    return df


# lancia i singoli controlli in base alla selezione fatta in GUI
def check_data2(df, checks):
    for e in checks.keys():
        if checks[e]:
            # st.write(e + " is " + str(checks[e]))
            funzione = globals()[e]
            df = funzione(df)
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
    if not df[data_inizio_minima & data_inizio_massima & ore_543].empty:
        expndr = st.expander(
            "Trovato errore Eingewöhnung 543 Notbetreuung (data inizio >= 26.10.2020 e <= 16.11.2020 e ore 543 > 0)"
        )
        with expndr:
            make_grid(df[data_inizio_minima & data_inizio_massima & ore_543])
            # settiamo la colonna bool
            df.loc[
                (data_inizio_minima & data_inizio_massima & ore_543),
                "errFehlerEingewöhnung543Notbetreuung",
            ] = True
            x = dwnld(
                df[data_inizio_minima & data_inizio_massima & ore_543],
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

    if not df[inizio_minore_fine].empty:
        expndr = st.expander(
            "Trovato errore date contrattuali (Vertragsbeginn > Vertragsende)"
        )
        with expndr:
            make_grid(df[inizio_minore_fine])

            df.loc[inizio_minore_fine, "errInizioMinoreFine"] = True
            x = dwnld(
                df[inizio_minore_fine],
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

    if not df[codinvalido].empty:
        expndr = st.expander("Trovato errore formato del codice Fiscale")
        with expndr:
            make_grid(df[codinvalido])
            # settiamo il flag bool per la tabella finale
            df.loc[codinvalido, "errCodFisc1"] = True
            x = dwnld(
                df[codinvalido],
                "Scaricare tabella con errore codice fiscale",
                "ErroreCodiceFiscale",
            )

        return df
    # se non trovato errore il df è restituito come è stato ricevuto
    else:
        return df


def errCodFisc2(df):  # da finire, fa acqua da tutte le parti
    # condizione logica via regex per usare solo records con codfisc nel formato corretto
    codvalido = (
        df["Codice fiscale"].str.match(
            "[A-Z|a-z][A-Z|a-z][A-Z|a-z][A-Z|a-z][A-Z|a-z][A-Z|a-z]\d\d[A-Z|a-z]\d\d[A-Z|a-z]\d\d\d[A-Z|a-z]"
        )
        == True
    )
    # potremmo fare a meno di usare un nuovo df
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

    # invertiamo la condizione logica per trovare errori
    # l = len(dfnot40[~gg])
    # l40 = len(df40[~gg40])

    # se trovato errore maschhietti o femmine
    if not dfnot40[~gg].empty or not df40[~gg40].empty:
        expndr = st.expander("Trovato errore data nascita (giorno) per codice fiscale")
        with expndr:
            # lista dei due df con errori che concateniamo per fare un df
            frames = [dfnot40[~gg], df40[~gg40]]
            result = pd.concat(frames)
            make_grid(result)
            # non stiamo restituendo il df con errore gg nascita e non stiamo settando la colonna bool

    # condizione logica per ANNO NASCITA uguale anno codfisc
    anno = dfcod["Data di nascita"].dt.year == 2000 + dfcod["Codice fiscale"].str[
        6:8
    ].astype(int)
    # invertiamo condizione logica per trovare errore
    # trovato almeno un errore
    if not dfcod[~anno].empty:
        expndr = st.expander("Trovato errore data nascita (anno) per codice fiscale")
        with expndr:
            make_grid(dfcod[~anno])
            # non stiamo settando la colonna bool

        return df
    # se non trovato errore il df è restituito come è stato ricevuto
    else:
        return df


def errErrorePresenza(df):
    # condizione logica
    ore_rendicontate_uguale_zero = df["Ore totali rendicontate per il 2020"] == 0
    if not df[ore_rendicontate_uguale_zero].empty:
        expndr = st.expander("Trovato errore presenza (Ore totali rendicontate = 0)")
        with expndr:
            make_grid(df[ore_rendicontate_uguale_zero])
            df.loc[ore_rendicontate_uguale_zero, "errErrorePresenza"] = True
            x = dwnld(
                df[ore_rendicontate_uguale_zero],
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
    # st.dataframe(giorni.values)
    if not df[giorni].empty:
        expndr = st.expander("Trovato errore età bambino (< 90 giorni)")
        with expndr:
            make_grid(df[giorni])
            df.loc[
                giorni,
                "errAgeChild",
            ] = True
            x = dwnld(
                df[giorni],
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

    if not df[errore_dati_543p1 & errore_dati_543p2 & errore_dati_543p3].empty:
        expndr = st.expander(
            "Trovato errore dati 543 (Vertragsende vor 05.03.20 UND Vertragsbeginn nach 18.05.20 dann dürfen Stunden 543 nicht 0 sein)"
        )
        with expndr:
            make_grid(df[errore_dati_543p1 & errore_dati_543p2 & errore_dati_543p3])
            df.loc[
                errore_dati_543p1 & errore_dati_543p2 & errore_dati_543p3,
                "errErroreDati543",
            ] = True
            x = dwnld(
                df[errore_dati_543p1 & errore_dati_543p2 & errore_dati_543p3],
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
    l = len(df[giorni])
    if not df[giorni].empty:
        expndr = st.expander(
            "Trovato errore fine contratto assistenza (Vertragsende darf höchstens 4 Jahre größer als Geburtsdatum sein)"
        )
        with expndr:
            make_grid(df[giorni])

            df.loc[
                giorni,
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
    if not df[data_nascita & data_fine_assistenza].empty:
        expndr = st.expander(
            "Trovato errore Kindergarten #1 (Geburtsdatum kleiner/gleich 28.02.2017 ist, dann muss Vertragende kleiner/gleich 15.09.2019)"
        )
        with expndr:
            make_grid(df[data_nascita & data_fine_assistenza])
            df.loc[
                (data_nascita & data_fine_assistenza),
                "errKindergarten_1",
            ] = True
            x = dwnld(
                df[data_nascita & data_fine_assistenza],
                "Scaricare tabella con errore Kindergarten 1",
                "ErroreKindergarten1",
            )

        return df
    else:
        return df


def errKindergarten_2(df):

    data_nascita = df["Data di nascita"] >= KONTROLLEKINDERGARTEN_DATANASCITA_2
    data_fine_ass = df[
        "Data fine contratto\n(o data fine assistenza se diversa) *"
    ] > pd.to_datetime(
        "15.09." + (pd.to_datetime(df["Data di nascita"]).dt.year + 3).astype("str"),
        format="%d.%m.%Y",
    )
    if not df[data_nascita & data_fine_ass].empty:
        expndr = st.expander(
            "Trovato errore controllo Kindergarten #2 (Geburtsdatum größer/gleich 01.03.2017 muss Vertragende <= 15.09 des Geburtsjahrs +3 Jahre sein)"
        )
        with expndr:
            make_grid(df[data_nascita & data_fine_ass])
            df.loc[
                (data_nascita & data_fine_ass),
                "errKindergarten_2",
            ] = True
            x = dwnld(
                df[data_nascita & data_fine_ass],
                "Scaricare tabella con errore Kindergarten 2",
                "ErroreKindergarten2",
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

    if not df[data_inizio & ore_compensative].empty:
        expndr = st.expander(
            "Trovato errore finanziamento compensativo (Data inizio >= 05.03.2020 e OreContrattualizzateNonErogateFase2 (finanziamento compensativo) > 0 )"
        )
        with expndr:
            make_grid(df[data_inizio & ore_compensative])

            df.loc[
                (data_inizio & ore_compensative),
                "errErroreFinanziamentoCompensativo",
            ] = True
            x = dwnld(
                df[data_inizio & ore_compensative],
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
    if not df[data_inizio_minima & data_inizio_massima & ore_contrattualizzate].empty:
        expndr = st.expander(
            "Trovato errore Eingewöhnung (data inizio >= 13.02.2020 e <= 05.03.2020 e OreContrattualizzateNonErogateFase2 (finanziamento compensativo) > 0)"
        )
        with expndr:
            make_grid(
                df[data_inizio_minima & data_inizio_massima & ore_contrattualizzate]
            )

            df.loc[
                (data_inizio_minima & data_inizio_massima & ore_contrattualizzate),
                "errFehlerEingewöhnung",
            ] = True
            x = dwnld(
                df[data_inizio_minima & data_inizio_massima & ore_contrattualizzate],
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

    if not df[data_inizio_minima & data_inizio_massima & ore_543].empty:
        expndr = st.expander(
            "Trovato errore Eingewöhnung 543 Lockdown (Vertragsbeginn >= 13.02.2020 und <= 05.03.2020 e ore543 > 0)"
        )
        with expndr:
            make_grid(df[data_inizio_minima & data_inizio_massima & ore_543])

            df.loc[
                (data_inizio_minima & data_inizio_massima & ore_543),
                "errFehlerEingewöhnung543Lockdown",
            ] = True
            x = dwnld(
                df[data_inizio_minima & data_inizio_massima & ore_543],
                "Scaricare tabella con errore Eingewöhnung 543 Lockdown",
                "ErroreLockdown543",
            )

        return df
    else:
        return df


def errErroreCovid(df):

    data_fine_assistenza = (
        df["Data fine contratto\n(o data fine assistenza se diversa) *"]
        < KONTROLLECOVID_DATAFINEASSISTENZA
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

    if not df[data_fine_assistenza & (ore_543 | ore_733 | ore_contrattualizzate)].empty:
        expndr = st.expander(
            "Trovato errore Covid #1 (data inizio < 05.03.2020 e Ore543 > 0) oppure (data fine < 05.03.2020 e Ore733 > 0) oppure (data fine < 05.03.2020 e OreContrattualizzateNonErogateFase2 (finanziamento compensativo) > 0)"
        )
        with expndr:
            make_grid(
                df[data_fine_assistenza & (ore_543 | ore_733 | ore_contrattualizzate)]
            )

            df.loc[
                (data_fine_assistenza & (ore_543 | ore_733 | ore_contrattualizzate)),
                "errErroreCovid",
            ] = True
            x = dwnld(
                df[data_fine_assistenza & (ore_543 | ore_733 | ore_contrattualizzate)],
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
    if not df[
        (data_inizio_ass & ore_543) | (data_inizio_ass & ore_contrattualizzate)
    ].empty:
        expndr = st.expander(
            "Trovato errore Covid #2 ((data inizio >= 24.11.2020 e ore543 >0) oppure (data inizio >= 24.11.2020 e OreContrattualizzateNonErogateFase2 (finanziamento compensativo >0))"
        )
        with expndr:
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


def errGesamtstundenVertragszeitraum(
    df,
):  # incompleto perchè va verificato su più file Excel
    # la condizione logica per trovare l'errore
    condizioneerrore = ((1920 * (df["GiorniAssistenzaAnnoRiferimento"])) / 366) < df[
        "Ore totali rendicontate per il 2020"
    ]

    # usiamo lunghezza del dataframe > 0 per vedere se è stato trovato l'errore
    # se maggiore di 0 allora abbiamo trovato codici fiscali invalidi
    if not df[condizioneerrore].empty:
        expndr = st.expander(
            "Trovato errore ore complessive per durata contrattuale (Gesamtstundenzahl (Abgerechnete Betreuungsstunden 2020 Gesamt) pro Kind (pro St.Nummer) darf nicht höher als 1920 sein)"
        )
        with expndr:
            make_grid(df[condizioneerrore])

            # settiamo il flag bool per la tabella finale
            df.loc[condizioneerrore, "errGesamtstundenVertragszeitraum"] = True
            x = dwnld(
                df[condizioneerrore],
                "Scaricare tabella con errore ore complessive per durata contrattuale",
                "ErroreOreComplessive",
            )

        return df
    # se non trovato errore il df è restituito come è stato ricevuto
    else:
        return df


def errSuperatoOreMassime1920(df):
    condizionlogica = (
        df.groupby("Codice fiscale")["Codice fiscale"].transform("count") > 1
    )
    condizionelogica2 = (
        df.groupby("Codice fiscale")["Ore totali rendicontate per il 2020"].transform(
            "sum"
        )
        > 1920
    )
    if not df[condizionlogica & condizionelogica2].empty:
        expndr = st.expander("Trovato errore ore complessive maggiore di 1920")
        with expndr:
            make_grid(df[condizionlogica & condizionelogica2])

            # settiamo flag per tabella finale
            df.loc[
                condizionlogica & condizionelogica2, "errSuperatoOreMassime1920"
            ] = True
            x = dwnld(
                df[condizionlogica & condizionelogica2],
                "Scaricare tabella con errore ore complessive maggiore 1920",
                "ErroreOre1920",
            )

        return df
    else:
        return df


# fine checks


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
        # st.write(uploaded_file.name)
        try:
            status.info("[*] " + uploaded_file.name + " caricato")
            df = pd.read_excel(uploaded_file)
        except:
            st.error(uploaded_file.name + " non è un file Excel")
            continue

        try:
            status.info("[*] " + uploaded_file.name + " elaborato")
            df = prepare_data(df, uploaded_file, anno_riferimento)
        except:
            st.error(
                uploaded_file.name
                + " --> ERRORE CONTROLLO GENERALE --> Il file non viene usato per l'elaborazione"
            )
            continue
        # meglio lasciare prepare_data qui
        # altrimenti diventa difficile estrarre comune ed ente

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
    return dfout


def choose_checks2():
    checks = {}
    attivatutti = st.checkbox("Selezionare/deselezionare tutti i controlli")
    st.write("")
    c1, c2, c3, c4 = st.columns(4)
    a = 1

    # creiamo i checkbox e i valori dinamicamente in base al dictionary che contiene
    # la lista degli errori

    for e in ERRORDICT.keys():
        locals()[f"{e}"] = locals()[f"c{a}"].checkbox(
            ERRORDICT[e], value=attivatutti, key=e
        )
        if a == 4:
            a = 1
        else:
            a = a + 1
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
    traeger = traeger[3].title()
    gemeinde = df.iloc[3]
    gemeinde = gemeinde[3]

    # cancelliamo le righe che non ci servono
    df = df.drop(labels=range(0, 8), axis=0)

    # prima convertiamo la colonna in numerica, forzando NaN sui non numerici
    df["Numero \nprogressivo"] = pd.to_numeric(
        df["Numero \nprogressivo"], errors="coerce"
    )

    # selezioniamo solo le righe che hanno un valore numerico in *Numero progressivo*
    # in questo modo eliminiamo le righe inutili dopo l'ultimo *numero progressivo*
    validi = df["Numero \nprogressivo"].notna()

    # teniamo solo record validi
    df = df[validi]

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
    df["Data di nascita"] = df["Data di nascita"].astype("datetime64[ns]")
    df["Data fine contratto\n(o data fine assistenza se diversa) *"] = df[
        "Data fine contratto\n(o data fine assistenza se diversa) *"
    ].astype("datetime64[ns]")
    df["Data inizio contratto (o data inizio assistenza se diversa)"] = df[
        "Data inizio contratto (o data inizio assistenza se diversa)"
    ].astype("datetime64[ns]")

    # prima convertiamo la colonna in numerica, forzando NaN sui non numerici
    df["Numero \nprogressivo"] = pd.to_numeric(
        df["Numero \nprogressivo"], errors="coerce"
    )

    # elimiamo colonne che sono servono più
    df = df.drop(["Numero \nprogressivo"], axis=1)

    # creiamo due nuove colonne e le riempiamo con comune ed ente
    # estratti prima
    df.insert(1, "Comune", gemeinde)
    df.insert(1, "Ente", traeger)

    # sostituiamo tutti i NaN con *0*
    df = df.fillna(0)

    # scriviamo anche il nome del file perché non si sa mai che non possa servire
    df.insert(0, "filename", uploaded_file.name)
    # df['filename'] = uploaded_file.name

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
    ).dt.days  # calcolo giorni anno riferimento
    # df = df.drop(['inizio','fine'], axis=1) # le colonne non servono più
    return df


def drop_columns(df):
    df = df.drop(
        df.columns[
            [
                16,
                17,
                18,
                19,
                20,
                21,
                22,
                23,
                24,
                25,
                26,
                27,
                28,
                29,
                30,
                31,
                32,
                33,
                34,
            ]
        ],
        axis=1,
    )
    return df


def dwnld(df, k, ff):
    if ff != "soloerrori":
        df = drop_columns(df)

    f = df.to_csv(sep=";").encode(
        "utf-8-sig"
    )  # dobbiamo usare questo altrimenti windoof sballa Umlaute
    st.download_button(
        label=k,
        data=f,
        file_name=ff + ".csv",
        mime="text/csv",
        key=k,
    )
    return "x"  # inutile


def make_df_solo_errori(dffinal):
    errCodFisc1 = dffinal["errCodFisc1"] == True
    errCodFisc2 = dffinal["errCodFisc2"] == True
    errAgeChild = dffinal["errAgeChild"] == True
    errInizioMinoreFine = dffinal["errInizioMinoreFine"] == True
    errErrorePresenza = dffinal["errErrorePresenza"] == True
    errErroreDati543 = dffinal["errErroreDati543"] == True
    errFineAssistenzaMax4Anni = dffinal["errFineAssistenzaMax4Anni"] == True
    errKindergarten_1 = dffinal["errKindergarten_1"] == True
    errKindergarten_2 = dffinal["errKindergarten_2"] == True
    errErroreFinanziamentoCompensativo = (
        dffinal["errErroreFinanziamentoCompensativo"] == True
    )
    errFehlerEingewöhnung = dffinal["errFehlerEingewöhnung"] == True
    errErroreCovid = dffinal["errErroreCovid"] == True
    errErroreCovid2 = dffinal["errErroreCovid2"] == True
    errFehlerEingewöhnung543Lockdown = (
        dffinal["errFehlerEingewöhnung543Lockdown"] == True
    )
    errFehlerEingewöhnung543Notbetreuung = (
        dffinal["errFehlerEingewöhnung543Notbetreuung"] == True
    )
    errGesamtstundenVertragszeitraum = (
        dffinal["errGesamtstundenVertragszeitraum"] == True
    )
    errSuperatoOreMassime1920 = dffinal["errSuperatoOreMassime1920"] == True

    # almeno 1 errore per record
    dffinal = dffinal[
        errCodFisc1
        | errCodFisc2
        | errAgeChild
        | errInizioMinoreFine
        | errErrorePresenza
        | errErroreDati543
        | errFineAssistenzaMax4Anni
        | errKindergarten_1
        | errKindergarten_2
        | errErroreFinanziamentoCompensativo
        | errFehlerEingewöhnung
        | errErroreCovid
        | errErroreCovid2
        | errFehlerEingewöhnung543Lockdown
        | errFehlerEingewöhnung543Notbetreuung
        | errGesamtstundenVertragszeitraum
        | errSuperatoOreMassime1920
    ]
    return dffinal


def app():

    st.header("FAMILIENAGENTUR - AGENZIA PER LA FAMIGLIA")
    st.subheader("Controllo errori TAGESMÜTTER (v. 0.9.16)")
    dfout = None

    # carichiamo qui la tabella dello storico??
    if path.exists("storico.xlsx"):
        c1, c2 = st.columns(2)
        c1.info("Trovato file storico")
        storico = c2.checkbox("caricare file storico?")
        if storico:
            pass

    # anno_riferimento = 2020
    uploaded_files = st.file_uploader(
        "Scegliere file Excel da caricare", accept_multiple_files=True
    )

    anno_riferimento = st.selectbox("Anno riferimento", ("2020", "2021", "2022"))

    checks = choose_checks2()

    f = st.form("Auswahl", clear_on_submit=True)
    flag = 0
    with f:
        submit = f.form_submit_button("Iniziare elaborazione e controllo errori")
        if submit:
            # soluzione un po' assurda, ma vogliamo spostare gli expander fuori dalla form
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
                gridOptions = buildGrid(dffinal)
                AgGrid(dffinal, gridOptions=gridOptions, enable_enterprise_modules=True)
                dwnld(dffinal, "SCARICARE TABELLA CON TUTTI I DATI", "tuttidati")

            # la tabella finale che contiene soltanto record con ALMENO UN ERRORE
            dffinalerr = make_df_solo_errori(dffinal)
            expndr = st.expander("TABELLA FINALE ELABORATA - SOLO ERRORI")
            with expndr:
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