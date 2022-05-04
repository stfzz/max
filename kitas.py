from unicodedata import name
import pandas as pd
import streamlit as st
import numpy as np

from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder

st.set_page_config(
    page_title="Dashboard - Familienagentur - Controllo KITAS",
    layout="wide",
    page_icon="👽",
)

DATAINIZIOMINIMA = "05.03.2020"
ORE2020 = 1920
KONTROLLEKINDERGARTEN_DATANASCITA_1 = "28.02.2017"
KONTROLLEKINDERGARTEN_DATAFINEASSISTENZA_1 = "15.09.2019"
KONTROLLEKINDERGARTEN_DATANASCITA_2 = "01.03.2017"
KONTROLLEKINDERGARTEN_DATAFINEASSISTENZA_2 = "15.09.2019"
EINGEWÖHNUNG_DATAINIZIO_MIN = "13.02.2020"
EINGEWÖHNUNG_DATAINIZIO_MAX = "03.05.2020"
KONTROLLECOVID_DATAFINEASSISTENZA = "03.05.2020"
KONTROLLECOVID2_DATAINIZIOASSISTENZA = "24.11.2020"


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
    df['errCodFisc1'] = np.nan
    df['errCodFisc1'] = df['errCodFisc1'].astype('boolean')

    df['errCodFisc2'] = np.nan
    df['errCodFisc2'] = df['errCodFisc1'].astype('boolean')

    df['errAgeChild'] = np.nan
    df['errAgeChild'] = df['errAgeChild'].astype('boolean')

    df['errInizioMinoreFine'] = np.nan
    df['errInizioMinoreFine'] = df['errInizioMinoreFine'].astype('boolean')   

    df['errErrorePresenza'] = np.nan
    df['errErrorePresenza'] = df['errErrorePresenza'].astype('boolean') 

    df['errErroreDati543'] = np.nan
    df['errErroreDati543'] = df['errErroreDati543'].astype('boolean') 

    df['errFineAssistenzaMax4Anni'] = np.nan
    df['errFineAssistenzaMax4Anni'] = df['errFineAssistenzaMax4Anni'].astype('boolean') 

    df['errKindergarten_1'] = np.nan
    df['errKindergarten_1'] = df['errKindergarten_1'].astype('boolean') 

    df['errKindergarten_2'] = np.nan
    df['errKindergarten_2'] = df['errKindergarten_2'].astype('boolean')

    df['errErroreFinanziamentoCompensativo'] = np.nan
    df['errErroreFinanziamentoCompensativo'] = df['errErroreFinanziamentoCompensativo'].astype('boolean')

    df['errFehlerEingewöhnung'] = np.nan
    df['errFehlerEingewöhnung'] = df['errFehlerEingewöhnung'].astype('boolean')

    df['errErroreCovid'] = np.nan
    df['errErroreCovid'] = df['errErroreCovid'].astype('boolean')

    df['errErroreCovid2'] = np.nan
    df['errErroreCovid2'] = df['errErroreCovid2'].astype('boolean')
    
    return df


# inizio checks
def check_data(df, checks):
    df_codfisc = check_codfisc(df, checks)
    check_AgeChild(df, checks)
    check_InizioMinoreFine(df, checks)
    check_ErrorePresenza(df, checks)
    check_ErroreDati543(df, checks)
    check_FineAssistenzaMax4Anni(df, checks)
    check_Kindergarten_1(df, checks)
    check_Kindergarten_2(df, checks)
    check_ErroreFinanziamentoCompensativo(df, checks)
    check_FehlerEingewöhnung(df, checks)
    check_ErroreCovid(df, checks)
    check_ErroreCovid2(df, checks)
    check_codfisc2(df, checks)


def check_InizioMinoreFine(df, checks):
    if "check_InizioMinoreFine" in checks:
        inizio_minore_fine = (
            df["Data inizio contratto (o data inizio assistenza se diversa)"]
            > df["Data fine contratto\n(o data fine assistenza se diversa) *"]
        )
        l = len(df[inizio_minore_fine])
        if l > 0:
            st.error("Errore date contrattuali")
            # st.table(df[inizio_minore_fine])
            gridOptions = buildGrid(df[inizio_minore_fine])
            AgGrid(
                df[inizio_minore_fine],
                gridOptions=gridOptions,
                enable_enterprise_modules=True,
            )


def check_codfisc(df, checks):
    if "check_codfisc" in checks:
        # definiamo condizione logica per codice fiscale invalido
        codinvalido = (
            df["Codice fiscale"].str.match(
                "[A-Z|a-z][A-Z|a-z][A-Z|a-z][A-Z|a-z][A-Z|a-z][A-Z|a-z]\d\d[A-Z|a-z]\d\d[A-Z|a-z]\d\d\d[A-Z|a-z]"
            )
            == False
        )
        # se maggiore di 0 allora abbiamo trovato codici fiscali invalidi
        l = len(df[codinvalido])
        if l > 0:
            df_codfisc = df[codinvalido]
            st.error("Codice Fiscale errore formato")
            gridOptions = buildGrid(df_codfisc)
            AgGrid(df_codfisc, gridOptions=gridOptions, enable_enterprise_modules=True)
            
            return df_codfisc


def check_codfisc2(df, checks):
    # definiamo condizione logica per codice fiscale valido
    if "check_codfisc2" in checks:
        # st.write('OK')
        codvalido = (
            df["Codice fiscale"].str.match(
                "[A-Z|a-z][A-Z|a-z][A-Z|a-z][A-Z|a-z][A-Z|a-z][A-Z|a-z]\d\d[A-Z|a-z]\d\d[A-Z|a-z]\d\d\d[A-Z|a-z]"
            )
            == True
        )
        dfcod = df[codvalido]
        ggnot40 = dfcod["Codice fiscale"].str[9:11].astype(int) < 40
        g40 = dfcod["Codice fiscale"].str[9:11].astype(int) > 40
        df40 = dfcod[g40]
        dfnot40 = dfcod[ggnot40]
        gg40 = (
            pd.to_datetime(df40["Data di nascita"]).dt.day
            == df40["Codice fiscale"].str[9:11].astype(int) - 40
        )
        gg = pd.to_datetime(dfnot40["Data di nascita"]).dt.day == dfnot40[
            "Codice fiscale"
        ].str[9:11].astype(int)
        l = len(dfnot40[~gg])
        l40 = len(df40[~gg40])
        if l > 0 or l40 > 0:
            frames = [dfnot40[~gg], df40[~gg40]]
            result = pd.concat(frames)
            st.error("Errore data nascita (giorno) per codice fiscale")
            gridOptions = buildGrid(result)
            AgGrid(result, gridOptions=gridOptions, enable_enterprise_modules=True)
        # gridOptions = buildGrid(df40[~gg40])
        # AgGrid(df40[~gg40], gridOptions=gridOptions, enable_enterprise_modules=True)
        anno = dfcod["Data di nascita"].dt.year == 2000 + dfcod["Codice fiscale"].str[
            6:8
        ].astype(int)
        l = len(dfcod[~anno])
        if l > 0:
            st.error("Errore data nascita (anno) per codice fiscale")
            gridOptions = buildGrid(dfcod[~anno])
            AgGrid(
                dfcod[~anno], gridOptions=gridOptions, enable_enterprise_modules=True
            )


def check_ErrorePresenza(df, checks):
    if "check_ErrorePresenza" in checks:
        ore_rendicontate_uguale_zero = df["Ore totali rendicontate per il 2020"] == 0
        l = len(df[ore_rendicontate_uguale_zero])
        if l > 0:
            st.error("Errore presenza (Ore totali rendicontate = 0)")
            # st.table(df[ore_rendicontate_uguale_zero])
            gridOptions = buildGrid(df[ore_rendicontate_uguale_zero])
            AgGrid(
                df[ore_rendicontate_uguale_zero],
                gridOptions=gridOptions,
                enable_enterprise_modules=True,
            )


def check_AgeChild(df, checks):
    if "age_child" in checks:
        giorni = (
            df["Data inizio contratto (o data inizio assistenza se diversa)"]
            - df["Data di nascita"]
        ).dt.days < 90
        # st.dataframe(giorni.values)
        l = len(df[giorni])
        if l > 0:
            st.error("Errore età bambino (< 90 giorni)")
            # st.table(df[giorni])
            gridOptions = buildGrid(df[giorni])
            AgGrid(df[giorni], gridOptions=gridOptions, enable_enterprise_modules=True)


def check_ErroreDati543(df, checks):
    if "check_ErroreDati543" in checks:
        errore_dati_543p1 = (
            df["Data inizio contratto (o data inizio assistenza se diversa)"]
            <= DATAINIZIOMINIMA
        )
        errore_dati_543p2 = (
            df[
                "Ore contrattualizzate non erogate\nai sensi della delibera\nn. 543_1025/2020"
            ]
            == 0
        )
        l = len(df[errore_dati_543p1 & errore_dati_543p2])
        if l > 0:
            st.error("Errore dati 543")
            # st.table(df[errore_dati_543p1 & errore_dati_543p2])
            gridOptions = buildGrid(df[errore_dati_543p1 & errore_dati_543p2])
            AgGrid(
                df[errore_dati_543p1 & errore_dati_543p2],
                gridOptions=gridOptions,
                enable_enterprise_modules=True,
            )


def check_FineAssistenzaMax4Anni(df, checks):
    if "check_FineAssistenzaMax4Anni" in checks:
        giorni = (
            df["Data fine contratto\n(o data fine assistenza se diversa) *"]
            - df["Data di nascita"]
        ).dt.days > 1464
        l = len(df[giorni])
        if l > 0:
            st.error("Errore fine contratto assistenza")
            # st.table(df[giorni])
            gridOptions = buildGrid(df[giorni])
            AgGrid(df[giorni], gridOptions=gridOptions, enable_enterprise_modules=True)


def check_Kindergarten_1(df, checks):
    if "check_Kindergarten_1" in checks:
        data_nascita = df["Data di nascita"] <= KONTROLLEKINDERGARTEN_DATANASCITA_1
        data_fine_assistenza = (
            df["Data fine contratto\n(o data fine assistenza se diversa) *"]
            > KONTROLLEKINDERGARTEN_DATAFINEASSISTENZA_1
        )
        l = len(df[data_nascita & data_fine_assistenza])
        if l > 0:
            st.error("Errore controllo Kindergarten #1")
            # st.table(df[data_nascita & data_fine_assistenza])
            gridOptions = buildGrid(df[data_nascita & data_fine_assistenza])
            AgGrid(
                df[data_nascita & data_fine_assistenza],
                gridOptions=gridOptions,
                enable_enterprise_modules=True,
            )


def check_Kindergarten_2(df, checks):
    if "check_Kindergarten_2" in checks:
        data_nascita = df["Data di nascita"] >= KONTROLLEKINDERGARTEN_DATANASCITA_2
        data_fine_ass = df[
            "Data fine contratto\n(o data fine assistenza se diversa) *"
        ] > pd.to_datetime(
            "15.09."
            + (pd.to_datetime(df["Data di nascita"]).dt.year + 3).astype("str"),
            infer_datetime_format=True,
        )
        l = len(df[data_nascita & data_fine_ass])
        if l > 0:
            st.error("Errore controllo Kindergarten #2")
            gridOptions = buildGrid(df[data_nascita & data_fine_ass])
            AgGrid(
                df[data_nascita & data_fine_ass],
                gridOptions=gridOptions,
                enable_enterprise_modules=True,
            )


def check_ErroreFinanziamentoCompensativo(df, checks):
    if "check_ErroreFinanziamentoCompensativo" in checks:
        data_inizio = (
            df["Data inizio contratto (o data inizio assistenza se diversa)"]
            >= DATAINIZIOMINIMA
        )
        ore_compensative = (
            df[
                "Ore contrattualizzate non erogate\nnella fase 2 (finanziamento compensativo)"
            ]
            > 0
        )
        l = len(df[data_inizio & ore_compensative])
        if l > 0:
            st.error("Errore finanziamento compensativo")
            # st.table(df[data_inizio & ore_compensative])
            gridOptions = buildGrid(df[data_inizio & ore_compensative])
            AgGrid(
                df[data_inizio & ore_compensative],
                gridOptions=gridOptions,
                enable_enterprise_modules=True,
            )


def check_FehlerEingewöhnung(df, checks):
    if "check_FehlerEingewöhnung" in checks:
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
        l = len(df[data_inizio_minima & data_inizio_massima & ore_contrattualizzate])
        if l > 0:
            st.error("Fehler Eingewöhnung")
            # st.table(df[data_inizio_minima & data_inizio_massima & ore_contrattualizzate])
            gridOptions = buildGrid(
                df[data_inizio_minima & data_inizio_massima & ore_contrattualizzate]
            )
            AgGrid(
                df[data_inizio_minima & data_inizio_massima & ore_contrattualizzate],
                gridOptions=gridOptions,
                enable_enterprise_modules=True,
            )


def check_ErroreCovid(df, checks):
    if "check_ErroreCovid" in checks:
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
            df[
                "Ore contrattualizzate non erogate\nai sensi della delibera\nn. 733/2020"
            ]
            > 0
        )
        ore_contrattualizzate = (
            df[
                "Ore contrattualizzate non erogate\nnella fase 2 (finanziamento compensativo)"
            ]
            > 0
        )
        l = len(df[data_fine_assistenza & (ore_543 | ore_733 | ore_contrattualizzate)])
        if l > 0:
            st.error("Errore Covid #1")
            # st.table(df[data_fine_assistenza & (ore_543 | ore_733 | ore_contrattualizzate)])
            gridOptions = buildGrid(
                df[data_fine_assistenza & (ore_543 | ore_733 | ore_contrattualizzate)]
            )
            AgGrid(
                df[data_fine_assistenza & (ore_543 | ore_733 | ore_contrattualizzate)],
                gridOptions=gridOptions,
                enable_enterprise_modules=True,
            )


def check_ErroreCovid2(df, checks):
    if "check_ErroreCovid2" in checks:
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
        l = len(
            df[(data_inizio_ass & ore_543) | (data_inizio_ass & ore_contrattualizzate)]
        )
        if l > 0:
            st.error("Errore Covid #2")
            gridOptions = buildGrid(
                df[
                    (data_inizio_ass & ore_543)
                    | (data_inizio_ass & ore_contrattualizzate)
                ]
            )
            AgGrid(
                df[
                    (data_inizio_ass & ore_543)
                    | (data_inizio_ass & ore_contrattualizzate)
                ],
                gridOptions=gridOptions,
                enable_enterprise_modules=True,
            )


# fine checks





def get_data(uploaded_files):
    dfout = None
    status = st.empty()

    for uploaded_file in uploaded_files:
        # st.write(uploaded_file.name)
        try:
            status.write("[*] " + uploaded_file.name + " caricato")
            df = pd.read_excel(uploaded_file)
            status.write("[*] " + uploaded_file.name + " elaborato")
            df = prepare_data(df, uploaded_file)
        except:
            st.error(uploaded_file.name + ' non è un file Excel')
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
        status.write(
            "[*] Tutti i dati sono stati elaborati -  PER INIZIARE DA CAPO: RICARICARE LA PAGINA"
        )
    return dfout


def choose_checks():
    checks = {}
    attivatutti = st.checkbox("Selezionare/deselezionare tutti i controlli")
    st.write("")

    c1, c2, c3, c4 = st.columns(4)

    if attivatutti:
        checkcodfisc = c1.checkbox(
            "Controllo formato codice fiscale", value=True, key="checkcodfiscale"
        )
        checkage = c2.checkbox("Controllo età bambino", value=True, key="checkage")
        checkInizioMinoreFine = c3.checkbox(
            "Controllo date contrattuali", value=True, key="checkInizioMinoreFine"
        )
        checkErrorePresenza = c4.checkbox(
            "Controllo errore presenza", value=True, key="checkErrorePresenza"
        )
        checkErroreDati543 = c1.checkbox(
            "Controllo errore dati 543", value=True, key="checkErroreDati543"
        )
        checkFineAssistenzaMax4Anni = c2.checkbox(
            "Controllo fine contratto assistenza",
            value=True,
            key="checkFineAssistenzaMax4Anni",
        )
        checkKindergarten1 = c3.checkbox(
            "Controllo Kindergarten #1", value=True, key="checkKindergarten1"
        )
        checkKindergarten2 = c4.checkbox(
            "Controllo Kindergarten #2", value=True, key="checkKindergarten2"
        )
        checkErroreFinanziamentoCompensativo = c1.checkbox(
            "Controllo finanziamento compensativo",
            value=True,
            key="checkErroreFinanziamentoCompensativo",
        )
        checkFehlerEingewöhnung = c2.checkbox(
            "Controllo Fehler Eingewöhnung",
            value=True,
            key="checkFehlerEingewöhnung",
        )
        checkErroreCovid = c3.checkbox(
            "Controllo Covid #1", value=True, key="checkErroreCovid"
        )
        checkErroreCovid2 = c4.checkbox(
            "Controllo Covid #2", value=True, key="checkErroreCovid2"
        )  #
        checkcodfisc2 = c1.checkbox(
            "Controllo data nascita per codice fiscale",
            value=True,
            key="checkcodfisc2",
        )
    else:
        checkcodfisc = c1.checkbox(
            "Controllo formato codice fiscale", value=False, key="checkcodfiscale"
        )
        checkage = c2.checkbox("Controllo età bambino", value=False, key="checkage")
        checkInizioMinoreFine = c3.checkbox(
            "Controllo date contrattuali", value=False, key="checkInizioMinoreFine"
        )
        checkErrorePresenza = c4.checkbox(
            "Controllo errore presenza", value=False, key="checkErrorePresenza"
        )
        checkErroreDati543 = c1.checkbox(
            "Controllo errore dati 543", value=False, key="checkErroreDati543"
        )
        checkFineAssistenzaMax4Anni = c2.checkbox(
            "Controllo fine contratto assistenza",
            value=False,
            key="checkFineAssistenzaMax4Anni",
        )
        checkKindergarten1 = c3.checkbox(
            "Controllo Kindergarten #1", value=False, key="checkKindergarten1"
        )
        checkKindergarten2 = c4.checkbox(
            "Controllo Kindergarten #2", value=False, key="checkKindergarten2"
        )
        checkErroreFinanziamentoCompensativo = c1.checkbox(
            "Controllo finanziamento compensativo",
            value=False,
            key="checkErroreFinanziamentoCompensativo",
        )
        checkFehlerEingewöhnung = c2.checkbox(
            "Controllo Fehler Eingewöhnung",
            value=False,
            key="checkFehlerEingewöhnung",
        )
        checkErroreCovid = c3.checkbox(
            "Controllo Covid #1", value=False, key="checkErroreCovid"
        )
        checkErroreCovid2 = c4.checkbox(
            "Controllo Covid #2", value=False, key="checkErroreCovid2"
        )
        checkcodfisc2 = c1.checkbox(
            "Controllo data nascita per codice fiscale",
            value=False,
            key="checkcodfisc2",
        )

    if checkcodfisc:
        checks["check_codfisc"] = True
    if checkage:
        checks["age_child"] = True
    if checkInizioMinoreFine:
        checks["check_InizioMinoreFine"] = True
    if checkErrorePresenza:
        checks["check_ErrorePresenza"] = True
    if checkErroreDati543:
        checks["check_ErroreDati543"] = True
    if checkFineAssistenzaMax4Anni:
        checks["check_FineAssistenzaMax4Anni"] = True
    if checkKindergarten1:
        checks["check_Kindergarten_1"] = True
    if checkKindergarten2:
        checks["check_Kindergarten_2"] = True
    if checkErroreFinanziamentoCompensativo:
        checks["check_ErroreFinanziamentoCompensativo"] = True
    if checkFehlerEingewöhnung:
        checks["check_FehlerEingewöhnung"] = True
    if checkErroreCovid:
        checks["check_ErroreCovid"] = True
    if checkErroreCovid2:
        checks["check_ErroreCovid2"] = True
    if checkcodfisc2:
        checks["check_codfisc2"] = True

    return checks


def prepare_data(df, uploaded_file):

    # estraiamo comune e nome ente da dove ci aspettiamo che siano
    # nel dataframe creato dal singolo file Excel
    traeger = df.iloc[2]
    traeger = traeger[3].title()
    gemeinde = df.iloc[3]
    gemeinde = gemeinde[3]
    df = pd.read_excel(
        uploaded_file,
        parse_dates=[
            "Data di nascita",
            "Data fine contratto\n(o data fine assistenza se diversa) *",
            "Data inizio contratto (o data inizio assistenza se diversa)",
        ],
        header=8,
    )

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

    # creiamo due nuove colonne e le riempiamo con comune ed ente
    # estratti prima
    df.insert(1, "Comune", gemeinde)
    df.insert(1, "Ente", traeger)

    # sostituiamo tutti i NaN con *0*
    df = df.fillna(0)

    # scriviamo anche il nome del file perché non si sa mai che non possa servire
    df.insert(0,'filename', uploaded_file.name)
    #df['filename'] = uploaded_file.name


    # aggiungiamo le colonne che ci servono più tardi per i codici errore
    # e assegniamo un valore dummy
    dfbool = make_bool_columns(df)



    return dfbool


def compute_hours(df, ar):
    ar = int(ar)  # convertiamo anno riferimento in *int*
    df["inizio"] = df[
        "Data inizio contratto (o data inizio assistenza se diversa)"
    ]  # intanto inseriamo i valori che ci sono
    df["fine"] = df["Data fine contratto\n(o data fine assistenza se diversa) *"]
    # se data inizio minore di anno riferimento allora mettiamo il 1. gennaio dell'anno riferimento
    iniz = df["inizio"].dt.year < ar  # condizione logica
    df.loc[iniz, "inizio"] = (
        str(ar) + "-01-01"
    )  # cerchiamo i valori < anno riferimento e sostituiamo con 01/01
    fin = df["fine"].dt.year > ar  # condizione logica
    df.loc[fin, "fine"] = str(ar) + "-12-31"  # sostituzione
    df.insert(
        9, "GiorniAssistenzaAnnoRiferimento (" + str(ar) + ")", 0
    )  # aggiungiamo colonna e mettiamo anno riferimento
    df["GiorniAssistenzaAnnoRiferimento (" + str(ar) + ")"] = (
        df["fine"] - df["inizio"]
    ).dt.days  # calcolo giorni anno riferimento
    # df = df.drop(['inizio','fine'], axis=1) # le colonne non servono più
    return df



def dwnld(df, k):
    f = df.to_csv().encode("utf-8")
    st.download_button(
        label=k + " downloaden",
        data=f,
        file_name="export.csv",
        mime="text/csv",
        key=k,
    )

def app():

    st.header('FAMILIENAGENTUR - AGENZIA PER LA FAMIGLIA')
    st.subheader('Controllo errori KITAS (v. 0.2)')
    dfout = None
    # anno_riferimento = 2020
    uploaded_files = st.file_uploader(
        "Scegliere file Excel da caricare", accept_multiple_files=True
    )

    anno_riferimento = st.selectbox("Anno riferimento", ("2020", "2021", "2022"))

    checks = choose_checks()

    f = st.form("Auswahl", clear_on_submit=True)

    with f:
        submit = f.form_submit_button("Iniziare elaborazione e controllo errori")
        if submit:
            dfout = get_data(uploaded_files)
            if dfout is not None:
                dfout = compute_hours(dfout, anno_riferimento)

                dffinal = check_data(dfout, checks)

                #dwnld(dffinal, "Zusammengefügte Daten")


app()