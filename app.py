import streamlit as st
import pandas as pd
import calendar
from datetime import date, datetime
import io
import random

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(layout="wide", page_title="ShiftMaster Pro", page_icon="🏥")

# --- COSTANTI ---
ORE_TURNO = 12.25
ORE_DEBITO_GG = 7.2
PATRONO = (6, 19)

CODICI_TURNO = ["", "G12", "N12", "G12B", "N12B", "GTI", "NTI", "GSL", "NSL", "GBO", "NBO", "AO:6", "PEDI", "MAL", "FERIE", "R", "SN"]

# --- FUNZIONI DI CALCOLO ---
def get_festivita(anno):
    return [date(anno, 1, 1), date(anno, 1, 6), date(anno, 4, 25), date(anno, 5, 1), 
            date(anno, 6, 2), date(anno, 6, 19), date(anno, 8, 15), date(anno, 11, 1), 
            date(anno, 12, 8), date(anno, 12, 25), date(anno, 12, 26)]

def calcola_debito_mensile(mese, anno, pt=100, ore_104=0):
    festivi = get_festivita(anno)
    num_giorni = calendar.monthrange(anno, mese)[1]
    giorni_feriali = 0
    for d in range(1, num_giorni + 1):
        dt = date(anno, mese, d)
        if dt.weekday() < 5 and dt not in festivi:
            giorni_feriali += 1
    return round((giorni_feriali * ORE_DEBITO_GG * (pt/100)) - ore_104, 2)

# --- INIZIALIZZAZIONE STAFF ---
if 'staff' not in st.session_state:
    data_staff = [
        {"Nome": "MEROLLA MASSIMO", "MSA1": True, "MSA2": True, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Coordinatore"},
        {"Nome": "BALDO GABRIELE", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Infermieri"},
        {"Nome": "BROGGINI CHARLOTTE", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Infermieri"},
        {"Nome": "CANCLINI FEDERICA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Infermieri"},
        {"Nome": "FRANZINI MARTINO", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Infermieri"},
        {"Nome": "GHILOTTI PAOLO", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Infermieri"},
        {"Nome": "PIETROGIOVANNA CHIARA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Infermieri"},
        {"Nome": "POLETTI RIZZI ALESSIA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Infermieri"},
        {"Nome": "RODIGARI GIULIA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Infermieri"},
        {"Nome": "SPINI NADIA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Infermieri"},
        {"Nome": "BARBARO GALANTINO SILVIA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Infermieri"},
        {"Nome": "CRUPI CARMEN", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Infermieri"},
        {"Nome": "GAMBARRI CRISTINA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Infermieri"},
        {"Nome": "GERALI ALESSIA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Infermieri"},
        {"Nome": "INNOCENTI DANIELA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Infermieri"},
        {"Nome": "MIOTTI SOFIA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Infermieri"},
        {"Nome": "PANIZZA CATERINA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Infermieri"},
        {"Nome": "PESARO DAVIDE", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Infermieri"},
        {"Nome": "SCARAMUZZI JACOPO", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Infermieri"},
        {"Nome": "STEDILE PATRIZIA", "MSA1": True, "MSA2": False, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Infermieri"},
        {"Nome": "BELTRACCHI VITTORIA", "MSA1": True, "MSA2": True, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Bormio"},
        {"Nome": "BORSERINI FRANCESCA", "MSA1": True, "MSA2": True, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Bormio"},
        {"Nome": "CAPELLI GIOVANNA", "MSA1": True, "MSA2": True, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Bormio"},
        {"Nome": "GALASSO DONATELLA", "MSA1": True, "MSA2": True, "Notti": True, "PT": 100, "H104": 0, "Gruppo": "Bormio"},
        {"Nome": "PES SILVIA", "MSA1": True, "MSA2": True, "Notti": False, "PT": 100, "H104": 0, "Gruppo": "Bormio"}
    ]
    st.session_state.staff = pd.DataFrame(data_staff)

# --- TABS ---
tab_turni, tab_anagrafica, tab_analisi = st.tabs(["🗓️ Griglia Turni", "👥 Gestione Personale", "📊 Analisi & Copertura"])

# --- ANAGRAFICA ---
with tab_anagrafica:
    st.header("Anagrafica Personale")
    st.session_state.staff = st.data_editor(st.session_state.staff, num_rows="dynamic", use_container_width=True)

# --- TURNI ---
with tab_turni:
    col1, col2, col3 = st.columns([1, 1, 2])
    mese = col1.selectbox("Mese", range(1, 13), index=datetime.now().month-1)
    anno = col2.number_input("Anno", value=2026)
    
    num_gg = calendar.monthrange(anno, mese)[1]
    giorni = [f"{d}" for d in range(1, num_gg+1)]
    nomi = st.session_state.staff["Nome"].tolist()
    
    if 'griglia' not in st.session_state or st.session_state.get('last_m') != mese:
        st.session_state.griglia = pd.DataFrame("", index=nomi, columns=giorni)
        st.session_state.last_m = mese

    st.session_state.griglia = st.session_state.griglia.reindex(nomi).fillna("")

    # --- TASTO GENERA ---
    if st.button("🪄 GENERA TURNI AUTOMATICI (RIEMPI BUCHI)"):
        with st.spinner("L'algoritmo sta calcolando la distribuzione equa..."):
            for d in giorni:
                turni_necessari = ["G12", "G12", "G12", "N12", "N12", "N12", "G12B", "N12B", "GTI", "NTI", "GSL", "NSL"]
                random.shuffle(turni_necessari)
                
                for t in turni_necessari:
                    # Se il turno è già coperto in questo giorno, passiamo al prossimo
                    if (st.session_state.griglia[d] == t).any(): continue
                    
                    # Troviamo chi può farlo
                    candidati = st.session_state.staff.copy()
                    # Filtri: non deve lavorare già, deve avere MSA se serve, deve avere Notti se serve
                    candidati = candidati[~candidati["Nome"].isin(st.session_state.griglia.index[st.session_state.griglia[d] != ""])]
                    if t in ["GTI", "NTI", "GSL", "NSL"]: candidati = candidati[candidati["MSA1"] == True]
                    if t in ["GBO", "NBO"]: candidati = candidati[candidati["MSA2"] == True]
                    if "N" in t: candidati = candidati[candidati["Notti"] == True]
                    
                    if not candidati.empty:
                        scelto = random.choice(candidati["Nome"].tolist())
                        st.session_state.griglia.at[scelto, d] = t
        st.success("Turni generati! Ora puoi rifinirli manualmente.")

    # --- DATA EDITOR ---
    config = {g: st.column_config.SelectboxColumn(g, options=CODICI_TURNO, width="small") for g in giorni}
    grid_edit = st.data_editor(st.session_state.griglia, column_config=config, use_container_width=True, height=800)
    st.session_state.griglia = grid_edit

# --- ANALISI & COPERTURA ---
with tab_analisi:
    st.header("Verifica Copertura Giornaliera")
    check = []
    for d in giorni:
        c = grid_edit[d].tolist()
        check.append({
            "Giorno": d,
            "PS G12 (req 3)": c.count("G12"),
            "PS N12 (req 3)": c.count("N12"),
            "OBI (req 1+1)": f"{c.count('G12B')}+{c.count('N12B')}",
            "Amb (req 4)": c.count("GTI")+c.count("NTI")+c.count("GSL")+c.count("NSL")
        })
    st.dataframe(pd.DataFrame(check).set_index("Giorno").T, use_container_width=True)

    st.header("Bilancio Ore Mensili")
    report = []
    for _, inf in st.session_state.staff.iterrows():
        ore = sum([ORE_TURNO for t in grid_edit.loc[inf["Nome"]] if any(x in str(t) for x in ["G12", "N12", "GTI", "NTI", "GSL", "NSL", "GBO", "NBO"])])
        ore += sum([float(str(t).split(":")[1]) for t in grid_edit.loc[inf["Nome"]] if "AO:" in str(t)])
        debito = calcola_debito_mensile(mese, anno, inf["PT"], inf["H104"])
        report.append({"Nome": inf["Nome"], "Debito": debito, "Fatte": ore, "Saldo": round(ore-debito, 2)})
    
    df_rep = pd.DataFrame(report)
    st.table(df_rep)

    st.header("🚑 Suggeritore Sostituzioni")
    g_buco = st.selectbox("In quale giorno manca personale?", giorni)
    if st.button("Suggerisci chi può coprire"):
        liberi = st.session_state.staff[~st.session_state.staff["Nome"].isin(grid_edit.index[grid_edit[g_buco] != ""])]
        st.write("Persone libere e disponibili quel giorno:")
        st.dataframe(liberi[["Nome", "MSA1", "MSA2", "Notti"]])

# --- EXPORT ---
if st.sidebar.button("💾 Scarica Excel"):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine='xlsxwriter') as wr:
        grid_edit.to_excel(wr, sheet_name='Turni')
    st.sidebar.download_button("📥 Download", buf.getvalue(), f"Turni_{mese}_{anno}.xlsx")
