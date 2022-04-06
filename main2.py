#from distutils.command import check
import pandas as pd
import streamlit as st



class make_gui():

    def upload_files(self):
        
        uploaded_files=st.file_uploader('Bitte Dateien auswählen',accept_multiple_files=True)
        return uploaded_files

    def which_year(self):
        anno_riferimento = st.selectbox('Referenz Jahr',('2020','2021','2022'))
        return anno_riferimento

    def cntnr(self):
        # we assign these values to avoid the *TypeError: cannot unpack non-iterable NoneType object' error
        # not sure it is a good idea :-/
        anno_riferimento = 2020
        uploaded_files = None
        with st.form('Auswahl'):
            anno_riferimento = self.which_year()
            uploaded_files = self.upload_files()
            submit = st.form_submit_button('Starten')
            self.status = st.empty()
            if submit:
                return (uploaded_files, anno_riferimento)
        return (uploaded_files, anno_riferimento)

    def dwnld(self,dfout):
        f = dfout.to_csv().encode('utf-8')
        st.download_button(label="Download", data=f, file_name='export.csv', mime='text/csv', key='download')

    def show_status(self,t):
        #status = st.empty()
        self.status.warning(t)



def get_data(uploaded_files, mg):
    dfout = None
    
    for uploaded_file in uploaded_files:
        #st.write(uploaded_file.name)
        mg.show_status(uploaded_file.name + ' wird geladen')
        df = pd.read_excel(uploaded_file)
        mg.show_status(uploaded_file.name + ' wird bearbeitet')

        # meglio lasciare prepare_data qui
        # altrimenti diventa difficile estrarre comune ed ente
        df = prepare_data(df,uploaded_file)

        # se dfout non esiste lo creiamo
        if dfout is None:       
            dfout = pd.DataFrame(columns = df.columns)
            dfout = df
        else:
            dfout = pd.concat([dfout,df])
    
    # ora sono tutti concatenati e possiamo restituire il dataframe
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

def check_data(dfout):
    st.warning('Steuerkodex falsch')
    st.table(dfout[dfout['Codice fiscale'].str.match('[A-Z|a-z][A-Z|a-z][A-Z|a-z][A-Z|a-z][A-Z|a-z][A-Z|a-z]\d\d[A-Z|a-z]\d\d[A-Z|a-z]\d\d\d[A-Z|a-z]') == False])

def compute_hours(df,ar):
    ar = int(ar)
    df['inizio'] = df['Data inizio contratto (o data inizio assistenza se diversa)']
    df['fine'] = df['Data fine contratto\n(o data fine assistenza se diversa) *']
    iniz = df['inizio'].dt.year < ar
    df.loc[iniz,'inizio'] = "2020-01-01"
    fin = df['fine'].dt.year > ar
    df.loc[fin,'fine'] = "2020-12-31"
    df.insert(9,'GiorniAssistenzaAnnoRiferimento ('+str(ar)+')',0)
    df["GiorniAssistenzaAnnoRiferimento ("+str(ar)+")"] = (df['fine'] - df['inizio']).dt.days
    df = df.drop(['inizio','fine'], axis=1)
    return df


def app():
    mg = make_gui()
    dfout = None
    anno_riferimento = 2020
    uploaded_files, anno_riferimento = mg.cntnr()
    
    dfout = get_data(uploaded_files, mg)
    if dfout is not None:
        dfout = compute_hours(dfout, anno_riferimento)
        check_data(dfout)
        st.write(dfout)
        mg.dwnld(dfout)
        
        



app()