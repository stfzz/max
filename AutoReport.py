import pandas as pd
from fpdf import FPDF
from os import path
import streamlit as st

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


class PDF(FPDF):
    def header(self):
        # Logo
        #self.image('head.jpg', 5, 1, 200)
        self.ln(20)
    def footer(self):
        self.set_text_color(148,153,148)
        #self.image('foot2.jpg', 5, 270, 200)
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', '', 8)
        # Page number
        self.cell(0, 10, 'Seite ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')






def app():
    try:
        df = pd.read_excel("storico.xlsx")
        st.write(len(df))
    except:
        st.write("file storico non trovato")
    
    for errore in ERRORDICT:
        st.write(errore)

    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=20.0)
    pdf.add_font(
        "DejaVuSansCondensed-Oblique",
        "",
        "DejaVuSansCondensed-Oblique.ttf",
        uni=True,
    )
    pdf.add_page()
    pdf.alias_nb_pages()
    pdf.set_font("DejaVuSansCondensed-Oblique", "", 12)
    pdf.cell(
        0,
        8,
        "Risultati analisi file rendiconti TAGESMÜTTER ",
        0,
        1,
        "C",
    )
    
    lista_enti = df["Ente"].unique()
    #st.write(lista_enti)
    for ente in lista_enti:
        st.write(lista_enti)
        pdf.cell(1,5,f"Risultati per {ente}",0,1)
        pdf.ln(4)
        df_errori = df[df["Ente"] == ente]
        #for errore in ERRORDICT:
        #    if not df_errori[df_errori[errore] == True].empty:
        #        pdf.cell(1,5,f"Trovato un errore per  {ERRORDICT[errore]}",0,1)
        #        st.write(df_errori[df_errori[errore] == True])

        pdf.ln(4)

    pdf.output("testPDF.pdf", "F")

app()