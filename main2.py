#from distutils.command import check
import pandas as pd
import streamlit as st

DATAINIZIOMINIMA = '05.03.2020'
ORE2020 = 1920
KONTROLLEKINDERGARTEN_DATANASCITA_1 = '28.02.2017'
KONTROLLEKINDERGARTEN_DATAFINEASSISTENZA_1 = '15.09.2019'
KONTROLLEKINDERGARTEN_DATANASCITA_2 = '01.03.2017'
KONTROLLEKINDERGARTEN_DATAFINEASSISTENZA_1 = '15.09.2019'

class make_gui():

    def upload_files(self):
        
        uploaded_files=self.upldr.file_uploader('Scegliere file Escel da caricare',accept_multiple_files=True)
        return uploaded_files

    def which_year(self):
        anno_riferimento = self.year.selectbox('Anno riferimento',('2020','2021','2022'))
        return anno_riferimento

    def cntnr(self):
        # we assign these values to avoid the *TypeError: cannot unpack non-iterable NoneType object' error
        # not sure it is a good idea :-/
        #anno_riferimento = 2020
        uploaded_files = None
        f = st.form('Auswahl', clear_on_submit=True)
        with f:
            self.upldr = st.empty()
            self.year = st.empty()
            self.bttn = st.empty()
            uploaded_files = self.upload_files()
            anno_riferimento = self.which_year()          
            submit = self.bttn.form_submit_button('Iniziare elaborazione e controllo errori')
            self.status = st.empty()
            self.status.empty()
            if submit:
                self.upldr.empty()
                self.year.empty()
                submit = self.bttn.form_submit_button('Da capo')
                return (uploaded_files, anno_riferimento)

        return (uploaded_files, anno_riferimento)

    def dwnld(self,dfout, k):
        f = dfout.to_csv().encode('utf-8')
        st.download_button(label=k + " downloaden", data=f, file_name='export.csv', mime='text/csv', key=k)

    def show_status(self,t):
        #status = st.empty()
        self.status.write(t)

    def error_cntnr(self,l,df):
        self.error_cntnr = st.empty()
        with self.error_cntnr.expander("Steuerkodex falsch: " + str(l)):
            a = 0
            c1,c2,c3,c4 = st.columns([1,1,1,1])
            c1.info('Nome')
            c2.info('Ente')
            c3.info('Comune')
            c4.info('Codice fiscale')
            while a < l:
                c1.write(df['Cognome e nome bambino'].values[a])
                c2.write(df['Ente'].values[a])
                c3.write(df['Comune'].values[a])
                c4.write(df['Codice fiscale'].values[a])
                a = a +1
            self.dwnld(df,'Fehlerhafte Steuerkodexe')

def get_data(uploaded_files, mg):
    dfout = None
    
    for uploaded_file in uploaded_files:
        #st.write(uploaded_file.name)
        mg.show_status('[*] ' + uploaded_file.name + ' caricato')
        df = pd.read_excel(uploaded_file)
        mg.show_status('[*] ' + uploaded_file.name + ' elaborato')

        # meglio lasciare prepare_data qui
        # altrimenti diventa difficile estrarre comune ed ente
        df = prepare_data(df,uploaded_file)

        # se dfout non esiste lo creiamo
        if dfout is None:       
            dfout = pd.DataFrame(columns = df.columns)
            dfout = df
        else:
            # inserire qui il controllo del nome ente, che deve essere lo stesso per i file caricati?
            dfout = pd.concat([dfout,df])
    
    
    # ora sono tutti concatenati e possiamo restituire il dataframe
    if dfout is not None:
        mg.show_status('[*] Tutti i dati sono stati elaborati')
    return dfout


def prepare_data(df, uploaded_file):

        # estraiamo conune e nome ente da dove ci aspettiamo che siano
        # nel dataframe creato dal singolo file Excel
        traeger = df.iloc[2]
        traeger = traeger[3].title()
        gemeinde = df.iloc[3]
        gemeinde = gemeinde[3]
        df = pd.read_excel(uploaded_file,parse_dates = ['Data di nascita','Data fine contratto\n(o data fine assistenza se diversa) *','Data inizio contratto (o data inizio assistenza se diversa)'], header=8)
        
        #prima convertiamo la colonna in numerica, forzando NaN sui non numerici
        df['Numero \nprogressivo'] = pd.to_numeric(df['Numero \nprogressivo'],errors='coerce')       
        #selezioniamo solo le righe che hanno un valore numerico in *Numero progressivo*
        # in questo modo eliminiamo le righe inutili dopo l'ultimo *numero progressivo*
        validi = df['Numero \nprogressivo'].notna()
        
        # teniamo solo record validi
        df = df[validi]

        #elimiamo colonne che sono servono più
        df = df.drop(['Numero \nprogressivo'], axis=1)

        # creiamo due nuove colonne e le riempiamo con comune ed ente 
        # estratti prima
        df.insert(1,'Comune',gemeinde)
        df.insert(1,'Ente',traeger)

        # sostituiamo tutti i NaN con *0*
        df = df.fillna(0)

        return df        

def check_data(df,mg):
    df_codfisc = check_codfisc(df,mg)
    check_AgeChild(df,mg)
    check_InizioMinoreFine(df,mg)
    check_ErrorePresenza(df,mg)
    check_ErroreDati543(df,mg)
    check_FineAssistenzaMax4Anni(df,mg)

def check_InizioMinoreFine(df,mg):
    inizio_minore_fine = df['Data inizio contratto (o data inizio assistenza se diversa)'] > df['Data fine contratto\n(o data fine assistenza se diversa) *']
    l = len(df[inizio_minore_fine])
    if l > 0:
        st.warning('Errore date contrattuali')
        st.table(df[inizio_minore_fine])

def check_codfisc(df,mg):
    # definiamo condizione logica per codice fiscale invalido
    codinvalido = df['Codice fiscale'].str.match('[A-Z|a-z][A-Z|a-z][A-Z|a-z][A-Z|a-z][A-Z|a-z][A-Z|a-z]\d\d[A-Z|a-z]\d\d[A-Z|a-z]\d\d\d[A-Z|a-z]') == False
    # se maggiore di 0 allora abbiamo trovato codici fiscali invalidi
    l = len(df[codinvalido])
    if l > 0:
        df_codfisc = df[codinvalido]
        st.warning('Codice Fiscale errore formato')
        st.table(df_codfisc)
        #mg.error_cntnr(l,df_codfisc)
        return df_codfisc
        # da aggiungere: controllo anno, mese e gg in riferimento al codifisc

def check_ErrorePresenza(df,mg):
     
    ore_rendicontate_uguale_zero = df['Ore totali rendicontate per il 2020'] == 0        
    l = len(df[ore_rendicontate_uguale_zero])
    if l > 0:
        st.warning('Errore presenza (Ore totali rendicontate = 0)')
        st.table(df[ore_rendicontate_uguale_zero])

def check_AgeChild(df,mg):
    giorni = (df['Data inizio contratto (o data inizio assistenza se diversa)'] - df['Data di nascita']).dt.days < 90
    #st.dataframe(giorni.values)
    l = len(df[giorni])
    if l > 0:
        st.warning('Errore età bamino (< 90 giorni')
        st.table(df[giorni])

def check_ErroreDati543(df,mg):
    errore_dati_543p1 = (df['Data inizio contratto (o data inizio assistenza se diversa)'] <= DATAINIZIOMINIMA)
    errore_dati_543p2 = (df['Ore contrattualizzate non erogate\nai sensi della delibera\nn. 543_1025/2020'] == 0)
    l = len(df[errore_dati_543p1 & errore_dati_543p2])
    if l > 0:
        st.warning('Errore dati 543')
        st.table(df[errore_dati_543p1 & errore_dati_543p2])

def check_FineAssistenzaMax4Anni(df,mg):
    giorni = (df['Data fine contratto\n(o data fine assistenza se diversa) *'] - df['Data di nascita']).dt.days > 1464
    l = len(df[giorni])
    if l > 0:
        st.warning('Errore fine contratto assistenza')
        st.table(df[giorni])


def compute_hours(df,ar):
    ar = int(ar) # convertiamo anno riferimento in *int*
    df['inizio'] = df['Data inizio contratto (o data inizio assistenza se diversa)'] # intanto inseriamo i valori che ci sono
    df['fine'] = df['Data fine contratto\n(o data fine assistenza se diversa) *']
    # se data inizio minore di anno riferimento allora mettiamo il 1. gennaio dell'anno riferimento
    iniz = df['inizio'].dt.year < ar # condizione logica
    df.loc[iniz,'inizio'] = str(ar) + "-01-01" # cerchiamo i valori < anno riferimento e sostituiamo con 01/01
    fin = df['fine'].dt.year > ar # condizione logica
    df.loc[fin,'fine'] = str(ar) + "-12-31" # sostituzione
    df.insert(9,'GiorniAssistenzaAnnoRiferimento ('+str(ar)+')',0) # aggiungiamo colonna e mettiamo anno riferimento
    df["GiorniAssistenzaAnnoRiferimento ("+str(ar)+")"] = (df['fine'] - df['inizio']).dt.days # calcolo giorni anno riferimento
    #df = df.drop(['inizio','fine'], axis=1) # le colonne non servono più
    return df


def app():
    mg = make_gui()
    dfout = None
    #anno_riferimento = 2020
    uploaded_files, anno_riferimento = mg.cntnr()
    
    dfout = get_data(uploaded_files, mg)
    if dfout is not None:
        dfout = compute_hours(dfout, anno_riferimento)
        check_data(dfout, mg)
        #st.write(dfout)
        mg.dwnld(dfout,'Zusammengefügte Daten')

        
app()
