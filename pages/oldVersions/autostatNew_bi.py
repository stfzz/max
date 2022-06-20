import pandas as pd

# import ipywidgets as widgets
from fpdf import FPDF
import sys


class PDF(FPDF):
    def header(self):
        # Logo
        self.image("head.jpg", 5, 1, 200)
        self.ln(20)

    def footer(self):
        self.set_text_color(148, 153, 148)
        # self.image('foot2.jpg', 5, 270, 200)
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font("Arial", "", 8)
        # Page number
        self.cell(0, 10, "Seite " + str(self.page_no()) + "/{nb}", 0, 0, "C")


def makeBilingual(a):
    if str(a) == "Ja":
        a = "Ja/Sì"
    if str(a) == "Sehr gut":
        a = "Sehr gut/Molto bene"
    if str(a) == "Gut":
        a = "Gut/Bene"
    if str(a) == "Ausreichend":
        a = "Ausreichend/Sufficiente"
    if str(a) == "Zum Teil":
        a = "Zum Teil/In parte"
    if str(a) == "Eher nicht":
        a = "Eher nicht/Non molto"
    if str(a) == "Nein":
        a = "Nein/No"
    if str(a) == "War nicht vorgesehen":
        a = "War nicht vorgesehen/Non era previsto"
    if str(a) == "Nicht ausreichend":
        a = "Nicht ausreichend/Insufficiente"
    if str(a) == "Sonstiges":
        a = "Nein/nicht ausreichend - No/insufficiente"
    return a


def cleanString(s):
    s = s.replace("–", "-")
    s = s.replace("„", '"')
    s = s.replace("“", '"')
    s = s.replace("…", "...")
    s = s.replace("’", '"')
    s = s.replace("”", '"')
    s = s.replace("\n", "")
    return s


def fixFileName(t):
    t = cleanString(t)
    fn = t + ".pdf"
    fn = fn.replace("/", " ")
    fn = fn.replace("\n", " ")
    fn = fn.replace("'", "")
    fn = fn.replace('"', "")
    fn = fn.replace("&", " ")
    fn = fn.replace("“", "")
    fn = fn.replace("”", "")
    fn = fn.replace("(in Rot Projekte ohne Gemeinde)", "")
    # fn=fn.replace('“ETA BETA”','Eta Beta')

    print("\nFILE name is:", fn)
    return fn


def writeTitle(t, df2):
    pdf.ln(8)
    pdf.set_font("Arial", "", 14)
    pdf.ln()
    pdf.cell(
        0,
        8,
        "Zufriedenheitserhebung zur Ferien- bzw. Nachmittagsbetreuung 2021 - Ergebnisse",
        0,
        1,
        "C",
    )
    pdf.cell(
        0,
        10,
        "Sondaggio di gradimento assistenza pomeridiana e durante le ferie 2021 - Risultati",
        0,
        1,
        "C",
    )
    pdf.ln(8)
    pdf.set_font("Arial", "B", 11)
    t = cleanString(t)
    l = str(len(set(df2["Projekt"])))
    txt = (
        "Trägerkörperschaft/Ente gestore: "
        + t.upper()
        + "\nAnzahl Projekte/Numero progetti: "
        + l
        + ", ausgefüllte Fragebögen/questionari compilati: "
        + str(len(df2))
    )
    txt = txt.replace("(IN ROT PROJEKTE OHNE GEMEINDE)", "")
    pdf.multi_cell(0, 8, txt, 0, 1, "J")


def writeProjekt(p, z):
    if p == "nan":
        p = "NotFound"
    try:
        txt = (
            str(z)
            + ") Projekt/Progetto: "
            + p
            + ", "
            + str(len(df3))
            + " Fragebögen/Questionari"
        )
        txt = cleanString(txt)
        print("\t" + txt)
        pdf.set_font("Arial", "B", 10)
        pdf.ln(5)
        pdf.multi_cell(180, 5, txt, 0, 1, "L")
    except:
        print(type(p), "p is ", p)


def getTraeger(t):
    try:
        df2 = df[df["Träger"] == t]
    except:
        print("error with ", t)
    return df2


def theKeys():
    lk = {
        "Entsprechen Inhalte der Beschreibung?": "Inwiefern entsprechen die Inhalte des Kurses/Angebotes der Projektbeschreibung? - In che misura le attività proposte coincidevano con la descrizione del corso?",
        "Wie war das Angebot organisiert?": "Wie war das Angebot organisiert? - Come valuta l'organizzazione del corso/progetto?",
        "Hat Angebot Kind gefallen?": "Wie hat das Angebot Ihren Kind gefallen? - Quanto è piaciuta l'offerta a Suo/a figlio/a?",
        "War Programm abwechslungsreich?": "War das Programm abwechslungsreich gestaltet? - Le attività proposte erano abbastanza varie?",
        "Wie bewerten Sie Ort und Räumlichkeiten?": "Wie bewerten Sie Ort und Räumlichkeiten des Angebots? - Come valuta luogo e locali dell'offerta?",
        "Ging Angebot auf Bedürfnisse Kindes ein?": "Ging das Angebot auf die Bedürfnisse Ihres Kindes ein? - Nell'offerta si è tenuto conto dei bisogni di vostro/a figlio/a?",
        "Bestanden Bewegungsmöglichkeiten im Freien?": "Bestanden Bewegungsmöglichkeiten im Freien? - Si sono svolte attività di movimento all'aperto?",
        "Wie bewerten Sie Kompetenz Betreuungspersonals?": "Wie bewerten Sie die Kompetenz des Betreuungspersonals? - Come valuta la competenza del personale educativo?",
        "Wie bewerten Sie Qualität Verpflegung?": "Wie bewerten Sie die Qualität der gebotenen Verpflegung? - Come valuta la qualità del servizio mensa?",
        "Bring- und Abholzeiten bedürfnisgerecht?": "Waren die Bring- und Abholzeiten bedürfnisgerecht? - I tempi di consegna e ritiro erano flessibili?",
        "Wurden Informationen Vorfeld geliefert?": "Wurden alle wichtigen Informationen im Vorfeld geliefert? - Sono state fornite tutte le informazioni necessarie prima dell'iscrizione?",
        "Teilnahmegebühren angemessen?": "Halten Sie die Teilnahmegebühren für angemessen? - Il costo Le sembra adeguato?",
        "Kind noch einmal dieses/ähnliches Angebot?": "Würde sich Ihr Kind noch einmal für dieses oder ein ähnliches Angebot entscheiden? - Suo/a figlio/a sceglierebbe di nuovo questo corso/progetto o simili?",
    }
    return lk


def theKeys2():
    lk2 = {
        "Eingeschrieben_Ansprechendes Programm": "Ansprechendes Programm - Programma interessante",
        "Eingeschrieben_Kontakt zu Gleichaltrigen": "Kontakt zu Gleichaltrigen - Contatto con coetanei/e",
        "Eingeschrieben_Berufstätigkeit der Eltern": "Berufstätigkeit der Eltern - Impegni lavorativi dei genitori",
        "Eingeschrieben_Förderung der Entwicklung des Kindes": "Förderung der Entwicklung des Kindes - Promuovere lo sviluppo del/della bambino/a",
    }

    lk3 = {
        "GrundAngebot_Nähe Wohnort/Arbeitsplatz": "Nähe am Wohnort oder Arbeitsplatz - Vicinanza all"
        "abitazione o al posto di lavoro",
        "GrundAngebot_Von Bekannten empfohlen": "Von Bekannten empfohlen - Consigliato da amici/conoscenti (di mio/a figlio/a)",
        "GrundAngebot_Gute Erfahrung": "Gute Erfahrung mit bisherigen Angeboten des Trägers - Buone esperienze con l'offerta del gestore",
        "GrundAngebot_Zeitraum": "Zeitraum/Dauer des Kurses/Angebotes - Periodo e/o orario del corso/progetto",
        "GrundAngebot_Preis-Leistungsverhältnis": "Preis-Leistungsverhältnis des Kurses/Angebotes - Rapporto qualità/costo del corso/progetto",
        "GrundAngebot_Tätigkeiten/Programm": "Angebotene Tätigkeiten/Programm - Attività/programmi offerti",
    }
    return lk2, lk3


def doTheKey(lk, df3, sowhat):
    pdf.set_font("Arial", "", 10)
    for k in lk:
        llla = {}
        pdf.ln(4)
        pdf.multi_cell(0, 4, lk[k], 0, 1, "L")
        pdf.ln(2)
        df3 = df3[~df3[k].isnull()]  # get rid of nan values
        la = set(df3[k])
        for a in la:
            llla[a] = makeBilingual(a)
        llla = {llla[z]: z for z in llla}  # invert keys and values
        pdf.set_font("Arial", "I", 10)
        for a in sorted(
            llla, key=len
        ):  # in questo modo abbiamo Nein/Sonstiges alla fine della lista
            try:
                b = (df3[k].value_counts(normalize=True, dropna=False) * 100)[llla[a]]
            except:
                # print('k= ',k,'a= ',llla[a],'b: ',b)
                sys.exit()
            txt1 = "\t\t" + str(a)
            txt2 = str(round(b, 1)) + "%"
            pdf.ln(4)
            pdf.cell(50, 0, txt1, 0, 0, "L")
            pdf.cell(50, 0, txt2, 0, 1, "R")

            if sowhat != "niet":
                if str(a) == "Nein/nicht ausreichend - No/insufficiente":
                    kk = k.replace("?", "")
                    kk = kk + "_Sonstiges"
                    bb = set(df3[kk])
                    if len(bb) == 1:
                        pdf.set_font("Arial", "", 10)
                        pdf.ln(5)
                        pdf.cell(0, 0, "\t\tKeine Anmerkung/Nessuna annotazione", 0, 1)
                        continue
                    x = 0
                    pdf.ln(5)
                    pdf.set_font("Arial", "", 10)
                    pdf.cell(0, 0, "\t\tAnmerkungen/Annotazioni:", 0, 1)
                    pdf.ln(3)
                    pdf.cell(5, 0, "", 0, 0)

                    for i in bb:
                        if str(i) != "nan":
                            x = x + 1
                            pdf.set_font("DejaVuSansCondensed-Oblique", "", 9)
                            pdf.multi_cell(165, 4, str(x) + ") " + str(i))
                            pdf.ln(1)
                            pdf.cell(5, 0, "", 0, 0)
                    pdf.set_font("Arial", "I", 10)
        pdf.ln(4)
        pdf.set_font("Arial", "", 10)


def doTheKeys2(lk2, lk3, df3, sowhat):
    pdf.set_font("Arial", "", 10)
    tit = "Weshalb haben Sie Ihr Kind in einen Kurs/ein Angebot der Ferien- bzw. Nachmittagsbetreuung eingeschrieben?\nPerché ha scelto di iscrivere Suo/a figlio/a a un corso/progetto di assistenza pomeridiana e/o durante le ferie scolastiche?"
    pdf.ln(6)
    pdf.multi_cell(0, 4, tit, 0, 1, "L")
    pdf.ln(2)
    pdf.set_font("Arial", "I", 10)
    for k in lk2:
        txt = 0
        try:
            txt = (
                str(
                    round(
                        (df3[k].value_counts(normalize=True, dropna=False) * 100)["Ja"],
                        1,
                    )
                )
                + "%"
            )
        except:
            continue

        pdf.ln(4)
        pdf.cell(127, 0, "\t\t" + lk2[k], 0, 0, "L")
        pdf.cell(50, 0, txt, 0, 1, "R")

    pdf.ln(4)
    txt = round(
        (
            len(df3["Eingeschrieben_Sonstiges"].value_counts(normalize=True))
            / len(df3["Eingeschrieben_Sonstiges"])
            * 100
        ),
        1,
    )
    txt = str(txt)
    txt = txt + "%"
    if sowhat != "niet":
        if txt != "0.0%":
            pdf.cell(127, 0, "\t\tSonstige Gründe/Altri motivi", 0, 0, "L")
            pdf.cell(50, 0, txt, 0, 0, "R")
            pdf.ln(4)
            s = set(df3["Eingeschrieben_Sonstiges"])
            x = 0
            pdf.set_font("Arial", "", 10)
            pdf.ln(1)
            pdf.cell(60, 0, "\t\tAnmerkungen/Commenti:", 0, 1)
            pdf.ln(3)
            pdf.cell(5, 0, "", 0, 0)
            for i in s:
                if str(i) != "nan":
                    x = x + 1
                    pdf.set_font("DejaVuSansCondensed-Oblique", "", 9)
                    pdf.multi_cell(165, 4, str(x) + ") " + str(i))
                    pdf.ln(1)
                    pdf.cell(5, 0, "", 0, 0)
            pdf.set_font("Arial", "", 10)
    elif sowhat == "niet":
        if txt != "0.0%":
            pdf.cell(127, 0, "\t\tSonstige Gründe/Altri motivi", 0, 0, "L")
            pdf.cell(50, 0, txt, 0, 0, "R")
            pdf.ln(9)

    tit = "Aus welchem Grund haben Sie dieses spezifische Angebot gewählt?\nPer quale motivo ha scelto questa specifica offerta?"
    pdf.set_font("Arial", "", 10)
    pdf.ln(6)
    pdf.multi_cell(0, 4, tit, 0, 1, "L")
    pdf.ln(2)
    pdf.set_font("Arial", "I", 10)
    for k in lk3:
        txt = 0
        try:
            txt = (
                str(
                    round(
                        (df3[k].value_counts(normalize=True, dropna=False) * 100)["Ja"],
                        1,
                    )
                )
                + "%"
            )
        except:
            continue
        pdf.ln(4)
        pdf.cell(127, 0, "\t\t" + lk3[k], 0, 0, "L")
        pdf.cell(50, 0, txt, 0, 1, "R")


def doComments(df3):
    n = 1
    pdf.ln(8)
    if (
        len(set(df3["Anmerkungen/Verbesserungsvorschläge"])) < 2
    ):  # non tutti lasciano un commento
        return
    pdf.set_font("Arial", "", 10)
    tit = "Anmerkungen und Verbesserungsvorschläge - Osservazioni e suggerimenti"
    tit = tit.upper()
    pdf.ln(2)
    pdf.cell(0, 0, tit, 0, 1, "L")
    pdf.ln(2)
    for a in set(df3["Anmerkungen/Verbesserungsvorschläge"]):
        if str(a) != "nan":
            pdf.ln(2)
            txt = str(a)
            txt = str(n) + ") " + txt
            pdf.set_font("sysfont", "", 9.5)
            pdf.multi_cell(0, 4, txt)  # ,0,1,'L')
            n = n + 1


if __name__ == "__main__":

    df = pd.read_excel("../ExportVollständigNeuNoDemo.xlsx")
    df = makeBilingual(df)
    lt = set(df["Träger"])
    lg = set(df["Gemeinde"])
    print("we have", len(lt), "Träger")
    print("we have", len(lg), "Gemeinden")
    lk = theKeys()
    lk2, lk3 = theKeys2()
    x = 0
    y = 0
    for t in lt:
        x = x + 1
        pdf = PDF()
        pdf.set_auto_page_break(auto=True, margin=20.0)
        pdf.add_font(
            "DejaVuSansCondensed-Oblique",
            "",
            "DejaVuSansCondensed-Oblique.ttf",
            uni=True,
        )
        pdf.add_font("sysfont", "", r"c:\WINDOWS\Fonts\arial.ttf", uni=True)
        pdf.add_page()
        pdf.alias_nb_pages()
        if t == "-->NotFound<--":
            x = x - 1
            continue
        if t != "KFS":  # or t!= 'Gemeinde Lüsen':
            continue
        #        if t != 'ASS. GIOV. “ETA BETA” JUGENDVEREIN ':
        #            continue
        fn = fixFileName(t)
        df2 = getTraeger(t)  # riceviamo un df con solo il traeger in questione
        writeTitle(t, df2)
        lp = set(df2["Projekt"]) # lista dei progetti per il traeger in questione
        z = 0
        for p in lp:
            z = z + 1
            y = y + 1
            df3 = df2[df2["Projekt"] == p]
            writeProjekt(p, z)
            doTheKey(lk, df3, "yep")
            doTheKeys2(lk2, lk3, df3, "yep")
            doComments(df3)
            pdf.add_page()

        pdf.set_font("Arial", "", 13)
        pdf.ln()
        pdf.cell(
            0,
            8,
            "Zufriedenheitserhebung zur Ferien- bzw. Nachmittagsbetreuung 2021 - Ergebnisse Südtirol",
            0,
            1,
            "C",
        )
        pdf.cell(
            0,
            10,
            "Sondaggio di gradimento assistenza pomeridiana e durante le ferie 2021 - Risultati Alto Adige",
            0,
            1,
            "C",
        )
        pdf.ln(8)
        pdf.set_font("Arial", "", 10)
        doTheKey(lk, df, "niet")
        doTheKeys2(lk2, lk3, df, "niet")
        pdf.output(fn, "F")
    print("----> generated PDF files: ", x)
    print("----> crunched projects: ", y)
