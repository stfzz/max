import pandas as pd
import streamlit as st



class make_gui():
    
    def upload_files(self):
        uploaded_files=st.file_uploader('Bitte Dateien auswählen',accept_multiple_files=True)

        return uploaded_files


def get_data(uploaded_files):
    dfout = None
    for uploaded_file in uploaded_files:
        st.write(uploaded_file.name)
        df = pd.read_excel(uploaded_file)
        df = prepare_data(df,uploaded_file)
        if dfout is None:       # se dfout non esiste lo creiamo
            dfout = pd.DataFrame(columns = df.columns)
            dfout = df
        else:
            dfout = pd.concat([dfout,df])
    st.dataframe(dfout)


def prepare_data(df, uploaded_file):
        traeger = df.iloc[2]
        traeger = traeger[3].title()
        gemeinde = df.iloc[3]
        gemeinde = gemeinde[3]
        df = pd.read_excel(uploaded_file,parse_dates = ['Data di nascita','Data fine contratto\n(o data fine assistenza se diversa) *','Data inizio contratto (o data inizio assistenza se diversa)'], header=8)
        #prima convertiamo la colonna in numerica, forzando NaN sui non numerici
        df['Numero \nprogressivo'] = pd.to_numeric(df['Numero \nprogressivo'],errors='coerce')       
        #selezioniamo solo le righe che hanno un valore numerico in *Numero progressivo*
        validi = df['Numero \nprogressivo'].notna()
        df = df[validi]
        df = df.drop(['Numero \nprogressivo'], axis=1)
        df.insert(1,'Comune',gemeinde)
        df.insert(1,'Ente',traeger)
        df = df.fillna(0)
        return df        



def app():
    mg = make_gui()
    uploaded_files = mg.upload_files()
    get_data(uploaded_files)




app()